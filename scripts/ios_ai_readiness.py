#!/usr/bin/env python3
"""Audit iOS AI capability choices before implementation."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import re
import sys
from pathlib import Path
from typing import Any

import ios_doctor
import ios_scan_scope


SCHEMA_VERSION = 1


def utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def fail(message: str) -> None:
    print(f"ios-ai-readiness: {message}", file=sys.stderr)
    raise SystemExit(1)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Audit whether an iOS feature should use Foundation Models, Core AI, Core ML, OpenAI API, or no AI."
    )
    parser.add_argument("--path", default=".", help="iOS project or package root to scan")
    parser.add_argument("--out", help="Output directory for ios-ai-readiness.md and ios-ai-readiness.json")
    parser.add_argument(
        "--shipguard-eval",
        action="store_true",
        help="Mark this scan as ShipGuard product QA only; findings must not become target-app work.",
    )
    parser.add_argument("--json", action="store_true", help="Print JSON to stdout instead of Markdown")
    parser.add_argument("--markdown", action="store_true", help="Print Markdown to stdout")
    return parser.parse_args()


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="ignore")


def rel(path: Path, root: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return path.as_posix()


def should_skip_dir(path: Path) -> bool:
    return ios_scan_scope.should_skip_dir(path)


def iter_files(root: Path) -> list[Path]:
    return ios_scan_scope.iter_files(root).files


def unique_sorted(values: list[str]) -> list[str]:
    return sorted({value for value in values if value})


def token_detection(capability: str, token: str, path: Path, root: Path, line_number: int, evidence: str) -> dict[str, Any]:
    return {
        "capability": capability,
        "token": token,
        "file": rel(path, root),
        "line": line_number,
        "evidence": evidence.strip(),
    }


TOKEN_RULES = [
    ("Foundation Models", ["FoundationModels", "SystemLanguageModel", "LanguageModelSession", "Generable", "@Generable"]),
    ("Core AI", ["CoreAI", "AIModel", "AIFoundation", "model asset catalog"]),
    ("Core ML", ["CoreML", "MLModel", "MLFeatureProvider", "MLMultiArray", "VNCoreMLModel", ".mlmodel", ".mlpackage"]),
    ("OpenAI API", ["api.openai.com", "/v1/responses", "/v1/chat/completions", "OPENAI_API_KEY", "AsyncOpenAI", "OpenAIClient", "Responses API"]),
    ("Natural Language", ["NaturalLanguage", "NLModel", "NLTagger", "NLEmbedding"]),
]


def scan_files(root: Path, files: list[Path]) -> dict[str, Any]:
    detections: list[dict[str, Any]] = []
    imports: dict[str, list[str]] = {}
    model_assets: list[str] = []
    source_files = [path for path in files if path.suffix in {".swift", ".m", ".mm", ".h", ".json", ".plist"}]

    for path in files:
        if path.suffix in {".mlmodel", ".mlpackage"} or path.name.endswith(".mlmodelc"):
            model_assets.append(rel(path, root))
            detections.append(token_detection("Core ML", path.suffix or path.name, path, root, 1, path.name))

    for path in source_files:
        text = read_text(path)
        rel_path = rel(path, root)
        if path.suffix == ".swift":
            imports[rel_path] = unique_sorted(re.findall(r"^\s*import\s+([A-Za-z0-9_]+)\b", text, re.M))
        for index, line in enumerate(text.splitlines(), start=1):
            for capability, tokens in TOKEN_RULES:
                for token in tokens:
                    if token in line:
                        detections.append(token_detection(capability, token, path, root, index, line))

    counts: dict[str, int] = {}
    for item in detections:
        counts[item["capability"]] = counts.get(item["capability"], 0) + 1
    return {
        "detections": detections,
        "imports": imports,
        "modelAssets": model_assets,
        "counts": counts,
        "sourceFiles": len(source_files),
    }


def collect_doctor_facts(root: Path) -> dict[str, Any]:
    report = ios_doctor.build_report(root)
    swift_versions: list[str] = []
    deployment_targets: list[str] = []
    for project in report.get("xcode_projects", []):
        swift_versions.extend(str(item) for item in project.get("swift_versions", []))
        deployment_targets.extend(str(item) for item in project.get("deployment_targets", []))
    for package in report.get("swift_packages", []):
        if package.get("swift_tools_version"):
            swift_versions.append(str(package["swift_tools_version"]))
        deployment_targets.extend(str(item).replace("_", ".") for item in package.get("ios_platforms", []))
    return {
        "swiftVersions": unique_sorted(swift_versions),
        "deploymentTargets": unique_sorted(deployment_targets),
        "privacyManifests": [item.get("path") for item in report.get("privacy_manifests", []) if isinstance(item, dict)],
        "targets": report.get("summary", {}).get("targets", 0),
    }


def option_row(
    option: str,
    status: str,
    best_for: str,
    privacy: str,
    latency: str,
    cost: str,
    fallback: str,
    proof: str,
) -> dict[str, str]:
    return {
        "option": option,
        "status": status,
        "bestFor": best_for,
        "privacy": privacy,
        "latency": latency,
        "cost": cost,
        "fallback": fallback,
        "proof": proof,
    }


def build_decision_matrix(counts: dict[str, int]) -> list[dict[str, str]]:
    has_foundation = counts.get("Foundation Models", 0) > 0
    has_core_ai = counts.get("Core AI", 0) > 0
    has_core_ml = counts.get("Core ML", 0) > 0
    has_openai = counts.get("OpenAI API", 0) > 0
    has_any = any(counts.values())

    return [
        option_row(
            "Foundation Models",
            "detected" if has_foundation else "candidate",
            "On-device text generation, summarization, extraction, refinement, and dialog where Apple Intelligence availability fits.",
            "Strongest when prompts and outputs can remain on device; still review user data and system availability.",
            "Low network latency, but constrained by device, OS, model availability, and context limits.",
            "No per-request cloud API cost; engineering cost is availability and fallback handling.",
            "Fallback to deterministic UX, server/cloud model, or disabled AI state when the system model is unavailable.",
            "Run on supported and unsupported devices/OS versions; record availability, language, refusal, and fallback behavior.",
        ),
        option_row(
            "Core AI",
            "detected" if has_core_ai else "candidate",
            "App-owned AI model assets and runtime deployment where the team controls model packaging and update strategy.",
            "Local model execution can reduce data exposure, but model assets and personalization still need privacy review.",
            "Depends on model size, hardware, compilation, and warm-up behavior.",
            "No hosted inference bill, but larger binary, model update, and performance costs can dominate.",
            "Fallback to smaller local model, Core ML path, server model, or deterministic feature.",
            "Measure model load time, memory, thermal impact, and output quality on minimum supported devices.",
        ),
        option_row(
            "Core ML",
            "detected" if has_core_ml else "candidate",
            "Classification, ranking, vision, speech, tabular, or custom predictive tasks with known model inputs and outputs.",
            "Local inference avoids sending raw user data to a cloud model; model files and derived features still need review.",
            "Predictable when model size and hardware targets are bounded.",
            "No per-request cloud cost; app size, conversion, validation, and model-update flow are the cost centers.",
            "Fallback to rules, server classification, or no result when the model is missing or unsupported.",
            "Run model fixtures, input validation, performance budgets, and minimum-device checks.",
        ),
        option_row(
            "OpenAI API",
            "detected" if has_openai else "candidate",
            "High-capability language, multimodal, reasoning, tool-calling, retrieval, or agentic workflows that exceed local models.",
            "Requires cloud data-flow review, server-side key handling, retention policy decisions, and user consent where needed.",
            "Network-dependent; use streaming, smaller models, prompt caching, and fallback UX for latency-sensitive paths.",
            "Per-token/request costs and hosted-tool costs must be budgeted and observed.",
            "Fallback to local model, deterministic UX, cached result, offline state, or human handoff.",
            "Use a server-side proxy, no client-side API key, structured output validation, abuse controls, and live latency/cost instrumentation.",
        ),
        option_row(
            "No AI",
            "recommended" if not has_any else "candidate",
            "Deterministic features, simple copy, static routing, permission explanations, and workflows where AI adds risk without user value.",
            "Best privacy and reliability profile when output can be deterministic.",
            "Lowest latency and easiest offline behavior.",
            "Lowest recurring cost.",
            "N/A; this is the fallback for weak AI value or unresolved privacy constraints.",
            "Prove the deterministic path satisfies the user job before adding AI complexity.",
        ),
    ]


def finding(rule_id: str, severity: str, title: str, evidence: str, recommendation: str) -> dict[str, str]:
    return {
        "ruleId": rule_id,
        "severity": severity,
        "title": title,
        "evidence": evidence,
        "recommendation": recommendation,
    }


def build_findings(counts: dict[str, int], facts: dict[str, Any]) -> list[dict[str, str]]:
    findings: list[dict[str, str]] = []
    if counts.get("OpenAI API", 0) > 0:
        findings.append(
            finding(
                "openai-api-cloud-privacy-gate",
                "high",
                "OpenAI API usage needs cloud data-flow approval",
                f"{counts['OpenAI API']} OpenAI API token(s) detected.",
                "Require server-side API key handling, retention/privacy review, cost budget, latency fallback, and structured output validation before implementation.",
            )
        )
    if counts.get("Foundation Models", 0) > 0:
        findings.append(
            finding(
                "foundation-models-availability-gate",
                "review",
                "Foundation Models usage needs availability fallback",
                f"{counts['Foundation Models']} Foundation Models token(s) detected.",
                "Gate the feature on model availability, supported OS/device/language, refusal behavior, and a non-AI fallback.",
            )
        )
    if counts.get("Core ML", 0) > 0:
        findings.append(
            finding(
                "core-ml-performance-gate",
                "review",
                "Core ML usage needs model-performance proof",
                f"{counts['Core ML']} Core ML token(s) or assets detected.",
                "Record model size, load time, memory, thermal impact, fixture accuracy, and minimum-device performance.",
            )
        )
    if not any(counts.values()):
        findings.append(
            finding(
                "no-ai-detected",
                "opportunity",
                "No AI capability tokens detected",
                "No Foundation Models, Core AI, Core ML, NaturalLanguage, or OpenAI API tokens were detected.",
                "Prefer no AI until a user-visible job, data boundary, expected output quality, and fallback path are defined.",
            )
        )
    if not facts["privacyManifests"]:
        findings.append(
            finding(
                "privacy-manifest-review",
                "review",
                "Privacy manifest evidence is missing",
                "No PrivacyInfo.xcprivacy file was discovered.",
                "Before AI features ship, document data collection, model inputs, retention, and third-party data transfers.",
            )
        )
    return findings


def blocked_questions(counts: dict[str, int]) -> list[str]:
    questions = [
        "What user-visible job requires AI instead of deterministic logic?",
        "Which data fields would be sent to a model, and which must stay on device?",
        "What is the acceptable latency budget, offline behavior, and failure copy?",
        "What quality bar, evaluation fixture, or human-review rule proves the output is safe enough?",
    ]
    if counts.get("OpenAI API", 0) > 0:
        questions.extend(
            [
                "Where will the server-side OpenAI API proxy live, and how are API keys, abuse controls, and logs protected?",
                "What token/request budget, model tier, structured output schema, and retry policy are acceptable?",
            ]
        )
    if counts.get("Foundation Models", 0) > 0:
        questions.append("Which unsupported-device, unavailable-model, language, and refusal states must fall back without blocking the app?")
    if counts.get("Core ML", 0) > 0:
        questions.append("Which model file, version, input normalization, accuracy fixture, and minimum-device performance budget are required?")
    return questions


def choose_summary(counts: dict[str, int]) -> str:
    if counts.get("OpenAI API", 0) and counts.get("Foundation Models", 0):
        return "Hybrid detected: compare on-device Foundation Models for private/low-latency cases against OpenAI API for higher-capability or tool-backed workflows."
    if counts.get("OpenAI API", 0):
        return "OpenAI API path detected; cloud privacy, server-side key handling, cost, and latency controls are mandatory before implementation."
    if counts.get("Foundation Models", 0):
        return "Foundation Models path detected; availability and fallback handling are the primary implementation risks."
    if counts.get("Core ML", 0):
        return "Core ML path detected; model packaging, performance, and fixture accuracy are the primary implementation risks."
    return "No AI implementation tokens detected; choose no AI until product value and data boundaries justify model use."


def shipguard_eval_boundary() -> dict[str, Any]:
    return {
        "targetAppsReadOnly": True,
        "shipguardOnly": True,
        "allowedUses": [
            "Evaluate ShipGuard AI-readiness report quality.",
            "Identify noisy AI-token detection, missing fallback guidance, or unclear model-choice tradeoffs.",
            "Create redacted public fixtures or eval cases in ShipGuard.",
        ],
        "forbiddenUses": [
            "Do not edit the scanned app from this run.",
            "Do not create app-specific AI, Core ML, Foundation Models, or OpenAI implementation tasks from this run.",
            "Do not present target-app findings as the active development goal.",
        ],
    }


def shipguard_eval_questions() -> list[str]:
    return [
        "Did the report distinguish real runtime usage from planning, tests, and blocked-boundary references?",
        "Were model-choice tradeoffs concrete enough for a solo developer to decide no-AI versus on-device versus cloud?",
        "Was the detections table capped enough to stay readable while preserving full JSON evidence?",
        "Which observation should become a public fixture or eval case before changing the rule again?",
    ]


def build_report(root: Path, *, shipguard_eval: bool = False) -> dict[str, Any]:
    if not root.exists():
        fail(f"path not found: {root}")
    if not root.is_dir():
        fail(f"path must be a directory: {root}")
    scan_scope = ios_scan_scope.iter_files(root)
    files = scan_scope.files
    scan = scan_files(root, files)
    facts = collect_doctor_facts(root)
    counts = scan["counts"]
    matrix = build_decision_matrix(counts)
    findings = build_findings(counts, facts)
    questions = blocked_questions(counts)
    status = "blocked" if any(item["severity"] == "high" for item in findings) else ("review" if findings else "pass")
    return {
        "schemaVersion": SCHEMA_VERSION,
        "tool": "shipguard ios ai-readiness",
        "intent": "shipguard-evaluation" if shipguard_eval else "app-development",
        "generatedAt": utc_now(),
        "status": status,
        "recommendationSummary": choose_summary(counts),
        "summary": {
            "sourceFiles": scan["sourceFiles"],
            "detections": len(scan["detections"]),
            "foundationModels": counts.get("Foundation Models", 0),
            "coreAI": counts.get("Core AI", 0),
            "coreML": counts.get("Core ML", 0),
            "openAIAPI": counts.get("OpenAI API", 0),
            "naturalLanguage": counts.get("Natural Language", 0),
            "modelAssets": len(scan["modelAssets"]),
            "privacyManifests": len(facts["privacyManifests"]),
        },
        "scanScope": ios_scan_scope.summary(scan_scope),
        "detections": scan["detections"],
        "modelAssets": scan["modelAssets"],
        "decisionMatrix": matrix,
        "scopeBoundary": shipguard_eval_boundary() if shipguard_eval else None,
        "reportQualityQuestions": shipguard_eval_questions() if shipguard_eval else [],
        "findings": findings,
        "blockedQuestions": questions,
        "doctorFacts": facts,
        "sourceReferences": [
            {
                "name": "Apple Foundation Models",
                "url": "https://developer.apple.com/documentation/foundationmodels/",
                "use": "On-device generative model option for supported Apple Intelligence environments.",
            },
            {
                "name": "Apple Core ML",
                "url": "https://developer.apple.com/documentation/coreml",
                "use": "Local app-integrated ML model option for custom predictive workloads.",
            },
            {
                "name": "OpenAI Responses API",
                "url": "https://developers.openai.com/api/reference/resources/responses/methods/create",
                "use": "Cloud model option for multimodal, tool-calling, reasoning, and structured-output workflows.",
            },
        ],
    }


def render_markdown(report: dict[str, Any]) -> str:
    summary = report["summary"]
    lines = [
        "# iOS AI Readiness Audit",
        "",
        f"- Status: `{report['status']}`",
        f"- Intent: `{report['intent']}`",
        f"- Recommendation: {report['recommendationSummary']}",
        f"- Source files: {summary['sourceFiles']}",
        f"- AI detections: {summary['detections']}",
        f"- Foundation Models tokens: {summary['foundationModels']}",
        f"- Core ML tokens/assets: {summary['coreML'] + summary['modelAssets']}",
        f"- OpenAI API tokens: {summary['openAIAPI']}",
        f"- Skipped generated/proof/cache directories: {report['scanScope']['skippedDirectoryCount']}",
        "",
    ]
    if report["intent"] == "shipguard-evaluation":
        boundary = report["scopeBoundary"]
        lines.extend(
            [
                "## ShipGuard Evaluation Boundary",
                "",
                "- This scan is ShipGuard product QA only.",
                "- The scanned app is a read-only input; do not edit it from this run.",
                "- Use findings to improve ShipGuard AI-readiness rules, docs, report shape, or eval fixtures.",
                "- Do not turn findings into target-app AI implementation tasks unless a separate app-work request explicitly authorizes it.",
                "",
                "Allowed uses: " + "; ".join(boundary["allowedUses"]),
                "",
                "Forbidden uses: " + "; ".join(boundary["forbiddenUses"]),
                "",
            ]
        )
    if report["scanScope"]["skippedDirectories"]:
        lines.extend(["## Scan Scope", ""])
        for directory in report["scanScope"]["skippedDirectories"][:8]:
            lines.append(f"- Skipped `{directory}`")
        if report["scanScope"]["skippedDirectoryListTruncated"]:
            lines.append("- Additional skipped directories are listed in JSON.")
        lines.append("")
    lines.extend(
        [
        "## On-Device Versus Cloud Decision Matrix",
        "",
        "| Option | Status | Best For | Privacy | Latency | Cost | Fallback | Proof |",
        "| --- | --- | --- | --- | --- | --- | --- | --- |",
        ]
    )
    for item in report["decisionMatrix"]:
        lines.append(
            f"| {item['option']} | {item['status']} | {item['bestFor']} | {item['privacy']} | {item['latency']} | {item['cost']} | {item['fallback']} | {item['proof']} |"
        )

    lines.extend(["", "## Detections", ""])
    if report["detections"]:
        selected_detections = report["detections"][:60]
        if len(report["detections"]) > len(selected_detections):
            lines.append("Detections are capped here so the Markdown stays scannable; the JSON report contains every detection.")
            lines.append("")
        lines.extend(["| Capability | Token | Location | Evidence |", "| --- | --- | --- | --- |"])
        for item in selected_detections:
            lines.append(f"| {item['capability']} | `{item['token']}` | `{item['file']}:{item['line']}` | `{item['evidence']}` |")
        hidden_count = len(report["detections"]) - len(selected_detections)
        if hidden_count > 0:
            lines.append(f"| ... | ... | ... | {hidden_count} more detections in JSON |")
    else:
        lines.append("No AI capability tokens or model assets were detected.")

    lines.extend(["", "## Findings", ""])
    if report["findings"]:
        lines.extend(["| Severity | Rule | Finding | Recommendation |", "| --- | --- | --- | --- |"])
        for item in report["findings"]:
            lines.append(f"| {item['severity']} | `{item['ruleId']}` | {item['title']} | {item['recommendation']} |")
    else:
        lines.append("No AI readiness findings were detected.")

    if report["reportQualityQuestions"]:
        lines.extend(["", "## Report Quality Questions", ""])
        for question in report["reportQualityQuestions"]:
            lines.append(f"- {question}")

    lines.extend(["", "## Blocked Questions", ""])
    for question in report["blockedQuestions"]:
        lines.append(f"- {question}")

    lines.extend(["", "## References", ""])
    for item in report["sourceReferences"]:
        lines.append(f"- {item['name']}: {item['url']}")
    lines.append("")
    return "\n".join(lines)


def write_outputs(report: dict[str, Any], out_dir: Path) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "ios-ai-readiness.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (out_dir / "ios-ai-readiness.md").write_text(render_markdown(report), encoding="utf-8")
    print(f"wrote: {out_dir / 'ios-ai-readiness.md'}")
    print(f"wrote: {out_dir / 'ios-ai-readiness.json'}")
    print(f"status: {report['status']}")


def main() -> int:
    args = parse_args()
    root = Path(args.path).expanduser().resolve()
    report = build_report(root, shipguard_eval=args.shipguard_eval)
    if args.out:
        write_outputs(report, Path(args.out).expanduser().resolve())
    elif args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print(render_markdown(report), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
