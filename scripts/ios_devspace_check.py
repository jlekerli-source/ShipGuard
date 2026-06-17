#!/usr/bin/env python3
"""Statically grade ShipGuard Devspace connector readiness."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import sys
from pathlib import Path
from typing import Any
from urllib.parse import parse_qsl, urlparse


SCHEMA_VERSION = 1
TOOL = "shipguard ios devspace-check"
TOKEN_QUERY_KEYS = {
    "access_token",
    "auth_token",
    "bearer_token",
    "codexpro_token",
    "key",
    "secret",
    "shipguard_token",
    "token",
}
DEFAULT_FILES = [
    "bin/shipguard",
    "scripts/shipguard_devspace_mcp.py",
    "docs/shipguard-devspace.md",
    "plugins/ios-shipguard/skills/ios-shipguard/SKILL.md",
    "plugins/ios-shipguard/skills/ios-shipguard/references/modes.md",
]


def utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def fail(message: str) -> None:
    print(f"ios-devspace-check: {message}", file=sys.stderr)
    raise SystemExit(1)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Grade ShipGuard Devspace MCP/App connector readiness without starting the server."
    )
    parser.add_argument("--path", default=".", help="ShipGuard repository root to inspect. Default: current directory")
    parser.add_argument("--out", help="Output directory for ios-devspace-check.md and ios-devspace-check.json")
    parser.add_argument("--preview-out", help="Existing shipguard ios preview output directory to summarize")
    parser.add_argument("--public-url", help="Tunneled/public Devspace MCP URL planned for ChatGPT Developer Mode")
    parser.add_argument("--bearer-token-env", help="Environment variable name that will hold the Devspace bearer token")
    parser.add_argument(
        "--shareable",
        action="store_true",
        help="Omit local absolute paths from JSON and Markdown so the report can be scored or shared without redaction.",
    )
    parser.add_argument("--strict", action="store_true", help="Exit non-zero when status is not pass")
    parser.add_argument("--json", action="store_true", help="Print JSON to stdout")
    parser.add_argument("--markdown", action="store_true", help="Print Markdown to stdout")
    return parser.parse_args()


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="ignore")


def report_path(path: Path, *, root: Path, shareable: bool, placeholder: str) -> str:
    if not shareable:
        return str(path)
    try:
        rel = path.relative_to(root)
        return rel.as_posix() or "."
    except ValueError:
        return f"<{placeholder}>"


def read_json_optional(path: Path) -> dict[str, Any] | None:
    try:
        loaded = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    return loaded if isinstance(loaded, dict) else None


def read_jsonl_objects(path: Path) -> list[dict[str, Any]]:
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError:
        return []
    rows: list[dict[str, Any]] = []
    for line in lines:
        if not line.strip():
            continue
        try:
            loaded = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(loaded, dict):
            rows.append(loaded)
    return rows


def source_bundle(root: Path) -> tuple[dict[str, str], list[str]]:
    texts: dict[str, str] = {}
    missing: list[str] = []
    for rel in DEFAULT_FILES:
        path = root / rel
        if path.is_file():
            texts[rel] = read_text(path)
        else:
            missing.append(rel)
    return texts, missing


def has_all(texts: dict[str, str], rel: str, tokens: list[str]) -> bool:
    text = texts.get(rel, "")
    return all(token in text for token in tokens)


def has_any(texts: dict[str, str], rel: str, tokens: list[str]) -> bool:
    text = texts.get(rel, "")
    return any(token in text for token in tokens)


def check(
    checks: list[dict[str, Any]],
    *,
    rule_id: str,
    category: str,
    title: str,
    passed: bool,
    evidence: str,
    recommendation: str,
    proof: str,
    severity: str = "high",
) -> None:
    status = "pass" if passed else ("blocked" if severity == "high" else severity)
    checks.append(
        {
            "ruleId": rule_id,
            "category": category,
            "title": title,
            "status": status,
            "severity": "none" if passed else severity,
            "evidence": evidence,
            "recommendation": recommendation,
            "proofGuidance": proof,
        }
    )


def add_finding(
    findings: list[dict[str, Any]],
    *,
    severity: str,
    rule_id: str,
    category: str,
    evidence: str,
    recommendation: str,
    proof: str,
) -> None:
    findings.append(
        {
            "severity": severity,
            "ruleId": rule_id,
            "category": category,
            "evidence": evidence,
            "recommendation": recommendation,
            "proofGuidance": proof,
        }
    )


def findings_from_checks(checks: list[dict[str, Any]]) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    for item in checks:
        severity = str(item.get("severity") or "none")
        if severity == "none":
            continue
        add_finding(
            findings,
            severity=severity,
            rule_id=str(item["ruleId"]),
            category=str(item["category"]),
            evidence=str(item["evidence"]),
            recommendation=str(item["recommendation"]),
            proof=str(item["proofGuidance"]),
        )
    return findings


def status_for(findings: list[dict[str, Any]]) -> str:
    if any(item["severity"] == "high" for item in findings):
        return "blocked"
    if any(item["severity"] == "review" for item in findings):
        return "review"
    return "pass"


def preview_evidence(raw_path: str | None, findings: list[dict[str, Any]], *, root: Path, shareable: bool) -> dict[str, Any]:
    if not raw_path:
        add_finding(
            findings,
            severity="opportunity",
            rule_id="preview-evidence-not-provided",
            category="preview",
            evidence="No --preview-out directory was supplied.",
            recommendation="Run shipguard ios preview first when grading a real ChatGPT visual-planning flow.",
            proof="Pass --preview-out <dir> containing session.json, handoff.json, handoff.md, and preview-events.jsonl.",
        )
        return {
            "provided": False,
            "status": "not-provided",
            "handoffQualityStatus": "not-checked",
            "recommendation": "Run shipguard ios preview --out <dir> before live visual-planning checks.",
        }

    path = Path(raw_path).expanduser().resolve()
    expected = ["session.json", "handoff.json", "handoff.md", "preview-events.jsonl"]
    present = [name for name in expected if (path / name).is_file()]
    missing = [name for name in expected if name not in present]
    preview_finding_start = len(findings)
    if missing:
        add_finding(
            findings,
            severity="review",
            rule_id="preview-evidence-incomplete",
            category="preview",
            evidence=f"Preview directory {path.name} is missing: {', '.join(missing)}",
            recommendation="Use a complete ios preview output before claiming visual-planning readiness.",
            proof="Regenerate preview evidence with shipguard ios preview --out <dir> and record at least one event.",
        )

    session = read_json_optional(path / "session.json") if (path / "session.json").is_file() else None
    handoff = read_json_optional(path / "handoff.json") if (path / "handoff.json").is_file() else None
    events = read_jsonl_objects(path / "preview-events.jsonl") if (path / "preview-events.jsonl").is_file() else []
    handoff_markdown = read_text(path / "handoff.md") if (path / "handoff.md").is_file() else ""
    latest_event = handoff.get("latestEvent") if isinstance(handoff, dict) and isinstance(handoff.get("latestEvent"), dict) else None
    if latest_event is None and events:
        latest_event = events[-1]
    target = handoff.get("targetResolution") if isinstance(handoff, dict) and isinstance(handoff.get("targetResolution"), dict) else None
    xcode = target.get("xcodeBuildMCP") if isinstance(target, dict) and isinstance(target.get("xcodeBuildMCP"), dict) else {}
    latest_event_type = str(latest_event.get("type") or "") if isinstance(latest_event, dict) else ""
    latest_event_action = str(latest_event.get("action") or "") if isinstance(latest_event, dict) else ""

    if "handoff.json" in present and handoff is None:
        add_finding(
            findings,
            severity="review",
            rule_id="preview-handoff-json-invalid",
            category="preview",
            evidence="handoff.json is present but is not parseable as a JSON object.",
            recommendation="Keep preview handoff JSON machine-readable so Devspace can grade target-resolution safety.",
            proof="Regenerate preview evidence with shipguard ios preview and rerun devspace-check.",
        )
    if "preview-events.jsonl" in present and not events:
        add_finding(
            findings,
            severity="review",
            rule_id="preview-events-empty",
            category="preview",
            evidence="preview-events.jsonl has no parseable event receipts.",
            recommendation="Record at least one click, context-menu, copy-change, visual-bug, or note receipt before using Devspace as visual proof.",
            proof="Record a preview event, then confirm preview-events.jsonl contains JSONL receipts.",
        )
    if handoff is not None and target is None:
        add_finding(
            findings,
            severity="review",
            rule_id="preview-handoff-target-resolution-missing",
            category="preview",
            evidence="handoff.json does not include targetResolution.",
            recommendation="Keep preview handoffs explicit about semantic target resolution and raw-coordinate safety.",
            proof="Regenerate handoff.json and confirm targetResolution.rawCoordinateTapAllowed is false.",
        )
    if isinstance(target, dict) and target.get("rawCoordinateTapAllowed") is True:
        add_finding(
            findings,
            severity="high",
            rule_id="preview-handoff-raw-coordinate-tap-enabled",
            category="preview",
            evidence="handoff.json allows raw coordinate taps.",
            recommendation="Never let browser coordinates become simulator input; require semantic XcodeBuildMCP elementRef matching first.",
            proof="Set targetResolution.rawCoordinateTapAllowed to false and rerun devspace-check --strict.",
        )
    if latest_event_type in {"tap-request", "navigate-request"} and xcode.get("elementRefRequiredBeforeTouch") is not True:
        add_finding(
            findings,
            severity="high",
            rule_id="preview-handoff-element-ref-not-required",
            category="preview",
            evidence=f"{latest_event_type} handoff does not require elementRef before touch.",
            recommendation="Require semantic elementRef proof before simulator touch for tap or navigation events.",
            proof="Confirm targetResolution.xcodeBuildMCP.elementRefRequiredBeforeTouch is true.",
        )
    safety_markdown_present = (
        "Raw coordinate tap allowed" in handoff_markdown
        and "Do not use browser coordinates as simulator taps" in handoff_markdown
    )
    if "handoff.md" in present and not safety_markdown_present:
        add_finding(
            findings,
            severity="review",
            rule_id="preview-handoff-safety-markdown-missing",
            category="preview",
            evidence="handoff.md does not include raw-coordinate and semantic-target safety language.",
            recommendation="Keep the Markdown handoff safe to paste into ChatGPT or Codex without reconstructing safety rules.",
            proof="Confirm handoff.md includes raw-coordinate and semantic elementRef requirements.",
        )

    preview_findings = findings[preview_finding_start:]
    if any(item["severity"] == "high" for item in preview_findings):
        handoff_status = "blocked"
    elif any(item["severity"] == "review" for item in preview_findings):
        handoff_status = "review"
    elif missing:
        handoff_status = "incomplete"
    else:
        handoff_status = "pass"

    return {
        "provided": True,
        "path": report_path(path, root=root, shareable=shareable, placeholder="preview-out"),
        "status": "complete" if not missing else "incomplete",
        "handoffQualityStatus": handoff_status,
        "present": present,
        "missing": missing,
        "eventCount": len(events),
        "latestEvent": {
            "type": latest_event_type or None,
            "source": latest_event.get("source") if isinstance(latest_event, dict) else None,
            "action": latest_event_action or None,
            "hasNote": bool(latest_event.get("note")) if isinstance(latest_event, dict) else False,
            "hasCoordinates": bool(
                isinstance(latest_event, dict)
                and ("normalizedX" in latest_event or "normalizedY" in latest_event or "pixelX" in latest_event or "pixelY" in latest_event)
            ),
        },
        "targetResolution": {
            "status": target.get("status") if isinstance(target, dict) else None,
            "intent": target.get("intent") if isinstance(target, dict) else None,
            "rawCoordinateTapAllowed": target.get("rawCoordinateTapAllowed") if isinstance(target, dict) else None,
            "xcodeNextTool": xcode.get("nextTool") if isinstance(xcode, dict) else None,
            "elementRefRequiredBeforeTouch": xcode.get("elementRefRequiredBeforeTouch") if isinstance(xcode, dict) else None,
        },
        "handoff": {
            "jsonPresent": handoff is not None,
            "markdownPresent": bool(handoff_markdown.strip()),
            "promptPresent": bool(handoff.get("prompt")) if isinstance(handoff, dict) else False,
            "safetyMarkdownPresent": safety_markdown_present,
        },
        "session": {
            "tool": session.get("tool") if isinstance(session, dict) else None,
            "hasPreviewUrl": bool(session.get("previewUrl") or session.get("url")) if isinstance(session, dict) else False,
        },
    }


def public_url_check(public_url: str | None, bearer_token_env: str | None, findings: list[dict[str, Any]]) -> dict[str, Any]:
    if not public_url:
        return {
            "provided": False,
            "status": "local-only",
            "evidence": "No public URL was supplied; Devspace remains a local-only planning bridge.",
        }

    parsed = urlparse(public_url)
    query_keys = sorted({key for key, _value in parse_qsl(parsed.query, keep_blank_values=True)})
    token_query_keys = sorted(key for key in query_keys if key.lower() in TOKEN_QUERY_KEYS or "token" in key.lower())
    sanitized = {
        "scheme": parsed.scheme,
        "host": parsed.hostname or "",
        "path": parsed.path or "/",
        "queryKeys": query_keys,
        "tokenQueryKeys": token_query_keys,
    }

    if parsed.scheme != "https":
        add_finding(
            findings,
            severity="high",
            rule_id="public-devspace-url-not-https",
            category="public-url",
            evidence=f"Public URL uses scheme={parsed.scheme or '<missing>'}; host={parsed.hostname or '<missing>'}",
            recommendation="Expose ChatGPT Developer Mode only through an HTTPS tunnel.",
            proof="Use an HTTPS tunnel URL ending in /mcp, then rerun this check.",
        )
    if token_query_keys:
        add_finding(
            findings,
            severity="high",
            rule_id="public-devspace-token-in-url",
            category="public-url",
            evidence=f"Public URL contains token-like query keys: {', '.join(token_query_keys)}",
            recommendation="Move bearer secrets out of URLs and into ChatGPT app auth or MCP bearer-token configuration.",
            proof="Remove token query parameters; pass only --bearer-token-env <ENV_NAME> to this checker.",
        )
    if not bearer_token_env:
        add_finding(
            findings,
            severity="high",
            rule_id="public-devspace-missing-bearer-env",
            category="public-url",
            evidence=f"Public URL host={parsed.hostname or '<missing>'} was supplied without --bearer-token-env.",
            recommendation="Require bearer auth for any tunneled or public Devspace endpoint.",
            proof="Start Devspace with --bearer-token-env SHIPGUARD_DEVSPACE_TOKEN and configure ChatGPT app auth.",
        )
    elif not re.match(r"^[A-Z_][A-Z0-9_]*$", bearer_token_env):
        add_finding(
            findings,
            severity="review",
            rule_id="bearer-env-name-nonstandard",
            category="public-url",
            evidence=f"Bearer env name {bearer_token_env!r} is not an all-caps shell-style variable.",
            recommendation="Use a clear env var such as SHIPGUARD_DEVSPACE_TOKEN and do not put the value in reports.",
            proof="Rerun with --bearer-token-env SHIPGUARD_DEVSPACE_TOKEN.",
        )

    return {
        "provided": True,
        "status": "reviewed",
        "sanitized": sanitized,
        "bearerTokenEnvProvided": bool(bearer_token_env),
        "bearerTokenEnvName": bearer_token_env or None,
        "note": "Token values are never read or printed by this checker.",
    }


def build_report(args: argparse.Namespace) -> dict[str, Any]:
    root = Path(args.path).expanduser().resolve()
    if not root.exists():
        fail(f"path not found: {root}")
    texts, missing = source_bundle(root)
    script = "scripts/shipguard_devspace_mcp.py"
    docs = "docs/shipguard-devspace.md"
    skill = "plugins/ios-shipguard/skills/ios-shipguard/SKILL.md"
    modes = "plugins/ios-shipguard/skills/ios-shipguard/references/modes.md"
    bin_path = "bin/shipguard"
    checks: list[dict[str, Any]] = []
    model_boundary_docs = has_all(texts, docs, ["Model choice happens in ChatGPT", "cannot force a specific ChatGPT model"])
    model_boundary_skill = has_any(texts, skill, ["model choice happens in ChatGPT", "Model choice happens in ChatGPT"]) or has_any(
        texts, modes, ["model choice happens in ChatGPT", "Model choice happens in ChatGPT"]
    )

    check(
        checks,
        rule_id="devspace-source-artifacts-present",
        category="source",
        title="Devspace source, docs, and plugin guidance are present",
        passed=not missing,
        evidence="All Devspace source artifacts found." if not missing else f"Missing: {', '.join(missing)}",
        recommendation="Keep the checker, live MCP bridge, docs, and plugin skill packaged together.",
        proof="Run ./bin/shipguard validate and ./tests/package_release_test.sh.",
    )
    check(
        checks,
        rule_id="devspace-command-routed",
        category="cli",
        title="CLI routes ios devspace through the ShipGuard MCP bridge",
        passed=has_all(texts, bin_path, ["shipguard ios devspace", "shipguard_devspace_mcp.py"]),
        evidence="bin/shipguard advertises and dispatches ios devspace.",
        recommendation="Expose Devspace through the public CLI before documenting connector workflows.",
        proof="Run ./bin/shipguard ios devspace --help.",
    )
    check(
        checks,
        rule_id="devspace-loopback-default",
        category="network",
        title="HTTP mode is loopback-first and rejects unauthenticated remote origins",
        passed=has_all(
            texts,
            script,
            ['default="127.0.0.1"', "LOOPBACK_HOSTS", "non-loopback Host rejected", '"Origin", "Referer"'],
        ),
        evidence="Source declares a loopback default and non-loopback Host/Origin/Referer rejection.",
        recommendation="Keep local unauthenticated Devspace bound to loopback; require auth plus HTTPS tunnel for ChatGPT.",
        proof="Run ./tests/shipguard_devspace_mcp_test.sh and inspect production_readiness output.",
    )
    check(
        checks,
        rule_id="devspace-bearer-auth-supported",
        category="auth",
        title="Bearer auth is available for tunneled Developer Mode",
        passed=has_all(texts, script, ["--bearer-token-env", "--bearer-token-file", "Authorization", "Bearer", "load_bearer_token"]),
        evidence="Devspace can load bearer tokens from env or file and validates Authorization headers.",
        recommendation="Use bearer auth for every public or tunneled endpoint.",
        proof="Start Devspace with --bearer-token-env SHIPGUARD_DEVSPACE_TOKEN and call production_readiness.",
    )
    check(
        checks,
        rule_id="devspace-widget-contract",
        category="mcp-app",
        title="Widget resource uses a versioned MCP Apps URI and MIME profile",
        passed=has_all(texts, script, ["ui://widget/shipguard-preview-v", "text/html;profile=mcp-app", "resources/read"]),
        evidence="Source defines WIDGET_URI, RESOURCE_MIME_TYPE, and resources/read output.",
        recommendation="Keep widget URI changes versioned and rerun ChatGPT app reconnect testing after descriptor changes.",
        proof="Run ./tests/shipguard_devspace_mcp_test.sh and confirm resources/read returns the widget URI.",
    )
    check(
        checks,
        rule_id="devspace-render-output-template",
        category="mcp-app",
        title="Render tool advertises openai/outputTemplate",
        passed=has_all(texts, script, ["render_preview_widget", "openai/outputTemplate", "WIDGET_URI"]),
        evidence="render_preview_widget descriptor and result metadata reference the widget template.",
        recommendation="Attach outputTemplate only to render tools so ChatGPT has a clear visual surface.",
        proof="Call tools/list and render_preview_widget in the Devspace MCP test.",
    )
    check(
        checks,
        rule_id="devspace-screenshot-token-meta-only",
        category="secrets",
        title="Bearer-auth screenshot view tokens stay in widget-only metadata",
        passed=has_all(
            texts,
            script,
            ["screenshot_view_token", "shipguard/screenshotProxyUrl", "include_view_token=False", "_meta"],
        ),
        evidence="Structured screenshot payload omits the view token while _meta carries the widget-only proxy URL.",
        recommendation="Never put screenshot view tokens in model-visible structuredContent or Markdown.",
        proof="Run the authenticated branch of ./tests/shipguard_devspace_mcp_test.sh.",
    )
    check(
        checks,
        rule_id="devspace-no-raw-coordinate-taps",
        category="simulator-safety",
        title="Visual events require semantic target resolution before simulator input",
        passed=has_all(texts, script, ["rawCoordinateTapAllowed", "False", "preview_match_target"])
        and has_all(texts, docs, ["rawCoordinateTapAllowed = false", "never performs simulator input"]),
        evidence="Source and docs route taps through targetResolution and preview_match_target, not raw coordinate execution.",
        recommendation="Keep preview clicks as intent receipts until XcodeBuildMCP elementRef proof exists.",
        proof="Record a tap request, call preview_target_resolution, then use XcodeBuildMCP semantic targets for real input.",
    )
    check(
        checks,
        rule_id="devspace-codex-handoff-not-auto-executed",
        category="handoff",
        title="Devspace prepares Codex handoffs without launching Codex from MCP",
        passed=has_all(texts, script, ["codex_prepare_handoff", "codex-handoff", "--execute"])
        and has_all(texts, docs, ["does not execute Codex from MCP", "--execute"]),
        evidence="Devspace can prepare supervisor artifacts; execution remains a separate trusted local action.",
        recommendation="Keep execution outside MCP tools and require explicit local approval for app-server runs.",
        proof="Call codex_prepare_handoff and confirm it emits executeCommand without running it.",
    )
    check(
        checks,
        rule_id="devspace-production-readiness-tool",
        category="readiness",
        title="A production_readiness tool explains local-only and hosted-use blockers",
        passed=has_all(texts, script, ["production_readiness", "productionReady", "requiredBeforeProduction"])
        and has_all(texts, docs, ["Use `production_readiness`", "does not enable non-loopback binding"]),
        evidence="The MCP surface includes production_readiness and docs require it before hosted-use discussion.",
        recommendation="Run production_readiness before sharing any tunneled endpoint or hosted Devspace plan.",
        proof="Call production_readiness in MCP and archive its structuredContent in the connector QA report.",
    )
    check(
        checks,
        rule_id="devspace-report-redaction-route",
        category="shareability",
        title="Docs route Devspace artifacts through redaction before sharing",
        passed=has_all(texts, docs, ["shipguard ios redact", "Do not paste secrets into preview notes"])
        and has_all(texts, skill, ["report-quality", "redact"]),
        evidence="Docs and skill guidance tell users to redact reports/logs before external planning or publication.",
        recommendation="Keep report-quality and redaction in the Devspace workflow before GitHub or ChatGPT sharing.",
        proof="Run ./bin/shipguard ios report-quality and ./bin/shipguard ios redact on generated local reports.",
    )
    check(
        checks,
        rule_id="devspace-chatgpt-model-boundary",
        category="product-boundary",
        title="Docs state that model selection happens in ChatGPT, not ShipGuard",
        passed=model_boundary_docs and model_boundary_skill,
        evidence="ShipGuard describes Devspace as a connector path, not a model switch or model-limit bypass.",
        recommendation="Keep model-choice claims honest in plugin guidance and public docs.",
        proof="Review docs/shipguard-devspace.md and the ios-shipguard skill after each plugin refresh.",
    )

    findings = findings_from_checks(checks)
    preview = preview_evidence(args.preview_out, findings, root=root, shareable=bool(args.shareable))
    public_url = public_url_check(args.public_url, args.bearer_token_env, findings)
    status = status_for(findings)
    pass_count = sum(1 for item in checks if item["status"] == "pass")

    return {
        "schemaVersion": SCHEMA_VERSION,
        "tool": TOOL,
        "generatedAt": utc_now(),
        "status": status,
        "shipguardOnly": True,
        "path": report_path(root, root=root, shareable=bool(args.shareable), placeholder="shipguard-repo"),
        "shareability": {
            "mode": "shareable" if args.shareable else "local",
            "localAbsolutePathsIncluded": not bool(args.shareable),
            "note": "Use --shareable before moving this report into ChatGPT, GitHub, docs, benchmark fixtures, or release evidence."
            if not args.shareable
            else "Local absolute paths are omitted from report fields; still run report-quality before public sharing.",
        },
        "summary": {
            "checksPassed": pass_count,
            "checksTotal": len(checks),
            "findings": len(findings),
            "highFindings": sum(1 for item in findings if item["severity"] == "high"),
            "reviewFindings": sum(1 for item in findings if item["severity"] == "review"),
            "opportunities": sum(1 for item in findings if item["severity"] == "opportunity"),
        },
        "scopeBoundary": {
            "purpose": "Grade ShipGuard Devspace connector readiness; do not grade or edit a target app.",
            "allowedUses": [
                "Improve ShipGuard Devspace reports, docs, tests, and plugin routing.",
                "Decide whether a Devspace endpoint is safe enough for local ChatGPT Developer Mode testing.",
                "Create public ShipGuard fixtures from repeated connector-readiness gaps.",
            ],
            "forbiddenUses": [
                "Do not use this report as Ringly, Ilmify, or target-app remediation work.",
                "Do not claim production hosting readiness from local static checks alone.",
                "Do not paste bearer-token values, screenshot view tokens, or private app artifacts into public reports.",
            ],
        },
        "inputs": {
            "publicUrl": public_url,
            "previewEvidence": preview,
            "bearerTokenEnvProvided": bool(args.bearer_token_env),
        },
        "checks": checks,
        "findings": findings,
        "codexProInspiredSignals": [
            {
                "signal": "local MCP bridge with conservative safety defaults",
                "shipguardUse": "Keep Devspace loopback-first, auth-gated for tunnels, and explicit about hosted-use blockers.",
            },
            {
                "signal": "handoff mode before execution",
                "shipguardUse": "Use codex_prepare_handoff and ios codex-handoff artifacts before any Codex app-server execution.",
            },
            {
                "signal": "compact Apps SDK widget card",
                "shipguardUse": "Keep render_preview_widget as the visual planning surface and version widget URI changes.",
            },
            {
                "signal": "stable public URL guidance without model-limit claims",
                "shipguardUse": "Document HTTPS tunnel plus bearer auth while leaving ChatGPT model selection to ChatGPT.",
            },
        ],
        "recommendedCommands": [
            "./bin/shipguard ios devspace-check --shareable --out /tmp/ios-shipguard-devspace-check",
            "./tests/shipguard_devspace_mcp_test.sh",
            "./bin/shipguard ios report-quality --reports <devspace-report-dir> --out <quality-dir>",
            "./bin/shipguard ios redact --in <devspace-report-dir> --out <redacted-dir>",
        ],
    }


def table_cell(value: object, limit: int = 110) -> str:
    text = str(value).replace("\n", " ").replace("|", "\\|").strip()
    if len(text) <= limit:
        return text
    return text[: limit - 1].rstrip() + "..."


def render_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# iOS Devspace Connector Readiness",
        "",
        f"- Status: {report['status']}",
        f"- Checks: {report['summary']['checksPassed']}/{report['summary']['checksTotal']} passed",
        f"- Findings: {report['summary']['findings']}",
        f"- Shareability mode: {report.get('shareability', {}).get('mode', 'local')}",
        f"- Purpose: {report['scopeBoundary']['purpose']}",
        "",
        "## Findings",
        "",
    ]
    if report["findings"]:
        lines.extend(["| Severity | Rule | Evidence | Recommendation |", "| --- | --- | --- | --- |"])
        for item in report["findings"]:
            lines.append(
                f"| {item['severity']} | {item['ruleId']} | {table_cell(item['evidence'])} | {table_cell(item['recommendation'])} |"
            )
    else:
        lines.append("No connector-readiness issues were detected.")

    lines.extend(
        [
            "",
            "## Checks",
            "",
            "| Status | Rule | Evidence | Proof Guidance |",
            "| --- | --- | --- | --- |",
        ]
    )
    for item in report["checks"]:
        lines.append(
            f"| {item['status']} | {item['ruleId']} | {table_cell(item['evidence'])} | {table_cell(item['proofGuidance'])} |"
        )

    public_url = report["inputs"]["publicUrl"]
    preview = report["inputs"]["previewEvidence"]
    target = preview.get("targetResolution") if isinstance(preview.get("targetResolution"), dict) else {}
    lines.extend(
        [
            "",
            "## Inputs",
            "",
            f"- Public URL status: {public_url['status']}",
            f"- Preview evidence status: {preview['status']}",
            f"- Preview handoff quality: {preview.get('handoffQualityStatus', 'not-checked')}",
            f"- Preview event count: {preview.get('eventCount', 0)}",
        ]
    )
    if target:
        lines.extend(
            [
                f"- Target status: {target.get('status') or 'unknown'}",
                f"- Raw coordinate tap allowed: {str(target.get('rawCoordinateTapAllowed') is True).lower()}",
                f"- Element ref required before touch: {str(target.get('elementRefRequiredBeforeTouch') is True).lower()}",
            ]
        )
    lines.extend(
        [
            "",
            "## CodexPro-Inspired ShipGuard Signals",
            "",
        ]
    )
    for item in report["codexProInspiredSignals"]:
        lines.append(f"- {item['signal']}: {item['shipguardUse']}")

    lines.extend(
        [
            "",
            "## Boundary",
            "",
            "- This is ShipGuard product QA only.",
            "- Do not turn private app evidence into app work from this report.",
            "- Do not claim production hosting readiness without a separate security and operations review.",
            "",
            "## Recommended Commands",
            "",
            "```bash",
            *report["recommendedCommands"],
            "```",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    args = parse_args()
    report = build_report(args)
    markdown = render_markdown(report)

    if args.out:
        out_dir = Path(args.out).expanduser().resolve()
        out_dir.mkdir(parents=True, exist_ok=True)
        (out_dir / "ios-devspace-check.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        (out_dir / "ios-devspace-check.md").write_text(markdown, encoding="utf-8")
        print(f"wrote: {out_dir / 'ios-devspace-check.json'}")
        print(f"wrote: {out_dir / 'ios-devspace-check.md'}")
    elif args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print(markdown)

    if args.strict and report["status"] != "pass":
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
