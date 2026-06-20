#!/usr/bin/env python3
"""Read-only first-run QA for the transparent ShipGuard verify-PR workflow."""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:
    from shipguard_result import build_result_ux, render_result_markdown
except ModuleNotFoundError:  # pragma: no cover - direct script fallback
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from shipguard_result import build_result_ux, render_result_markdown


SCHEMA_VERSION = 1
TOOL = "shipguard action verify-pr"
SURFACE = "ShipGuard Verify-PR First-Run Proof"
PLACEHOLDER = "replace-with-your-test-command"


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return ""


def rel_path(path: Path, root: Path, shareable: bool) -> str:
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return path.name if shareable else str(path)


def has_all(text: str, *needles: str) -> bool:
    return all(needle in text for needle in needles)


def has_regex(text: str, pattern: str) -> bool:
    return re.search(pattern, text, flags=re.MULTILINE) is not None


def finding(severity: str, rule_id: str, evidence: str, recommendation: str, proof: str, category: str = "workflow") -> dict[str, Any]:
    return {
        "severity": severity,
        "category": category,
        "ruleId": rule_id,
        "evidence": evidence,
        "recommendation": recommendation,
        "proofGuidance": proof,
    }


def check_signal(
    checks: list[dict[str, Any]],
    findings: list[dict[str, Any]],
    *,
    rule_id: str,
    label: str,
    passed: bool,
    required: bool,
    severity: str,
    evidence: str,
    recommendation: str,
    proof: str,
) -> None:
    checks.append({"ruleId": rule_id, "label": label, "required": required, "status": "pass" if passed else severity})
    if not passed:
        findings.append(finding(severity, rule_id, evidence, recommendation, proof))


def build_report(args: argparse.Namespace) -> dict[str, Any]:
    root = Path(args.path).resolve()
    workflow = Path(args.workflow)
    if not workflow.is_absolute():
        workflow = root / workflow
    text = read_text(workflow)
    findings: list[dict[str, Any]] = []
    checks: list[dict[str, Any]] = []

    exists = bool(text)
    check_signal(
        checks,
        findings,
        rule_id="workflow-file-present",
        label="Workflow file exists",
        passed=exists,
        required=True,
        severity="blocked",
        evidence=f"Workflow file not found: {workflow}",
        recommendation="Create a verify-PR workflow from examples/workflows/verify-pr.yml, then rerun this report.",
        proof="Run shipguard action verify-pr --workflow .github/workflows/shipguard-verify-pr.yml --out <dir>.",
    )

    if not exists:
        status = "blocked"
    else:
        check_signal(
            checks,
            findings,
            rule_id="pull-request-trigger",
            label="Pull request trigger",
            passed="pull_request:" in text or has_regex(text, r"^\s*-\s*pull_request\s*$"),
            required=True,
            severity="blocked",
            evidence="The workflow does not declare a pull_request trigger.",
            recommendation="Run the verify workflow on pull_request so ShipGuard can evaluate proposed AI-assisted changes before merge.",
            proof="Rerun shipguard action verify-pr after adding a pull_request trigger.",
        )
        if "pull_request_target" in text:
            findings.append(
                finding(
                    "blocked",
                    "pull-request-target-risk",
                    "The workflow uses pull_request_target, which can expose privileged context to untrusted PR code.",
                    "Use pull_request for the first verify path unless a separate threat model proves pull_request_target is safe.",
                    "Rerun this report after replacing pull_request_target or documenting a hardened, reviewed design.",
                    category="security",
                )
            )
            checks.append({"ruleId": "pull-request-target-risk", "label": "No pull_request_target trigger", "required": True, "status": "blocked"})
        else:
            checks.append({"ruleId": "pull-request-target-risk", "label": "No pull_request_target trigger", "required": True, "status": "pass"})

        check_signal(
            checks,
            findings,
            rule_id="checkout-full-history",
            label="Checkout with PR diff support",
            passed="actions/checkout@" in text and "fetch-depth: 0" in text,
            required=True,
            severity="review",
            evidence="The workflow does not clearly check out full history for base...HEAD PR diffs.",
            recommendation="Use actions/checkout with fetch-depth: 0 before building the PR diff.",
            proof="Rerun this report and confirm the PR diff step still uses origin/${{ github.base_ref }}...HEAD.",
        )
        check_signal(
            checks,
            findings,
            rule_id="shipguard-install-step",
            label="ShipGuard install step",
            passed=("git clone" in text and "ShipGuard" in text and "GITHUB_PATH" in text) or "pipx install shipguard" in text,
            required=True,
            severity="blocked",
            evidence="No clear ShipGuard install step was found.",
            recommendation="Install ShipGuard before prepare/verify. The transparent starter currently clones ShipGuard and adds bin to GITHUB_PATH.",
            proof="Run the workflow once and confirm shipguard version resolves before prepare.",
        )
        check_signal(
            checks,
            findings,
            rule_id="pr-diff-step",
            label="PR diff artifact",
            passed=has_all(text, "git diff", "github.base_ref", "/tmp/shipguard-pr.diff"),
            required=True,
            severity="blocked",
            evidence="The workflow does not clearly write the PR diff to /tmp/shipguard-pr.diff.",
            recommendation="Build the diff from origin/${{ github.base_ref }}...HEAD and pass it to shipguard verify.",
            proof="Upload or inspect /tmp/shipguard-pr.diff in a test PR run.",
        )
        placeholder_count = text.count(PLACEHOLDER)
        if placeholder_count:
            findings.append(
                finding(
                    "review",
                    "validation-command-placeholder",
                    f"SHIPGUARD_VALIDATION_COMMAND still contains the placeholder {PLACEHOLDER!r} ({placeholder_count} occurrence(s)).",
                    "Replace the placeholder with the repository's real test command before treating the workflow as installed.",
                    "Rerun shipguard action verify-pr after setting the command, then open a small PR and inspect the uploaded shipguard-verdict artifact.",
                )
            )
            checks.append({"ruleId": "validation-command-placeholder", "label": "Validation command configured", "required": True, "status": "review"})
        else:
            checks.append({"ruleId": "validation-command-placeholder", "label": "Validation command configured", "required": True, "status": "pass"})
        check_signal(
            checks,
            findings,
            rule_id="prepare-validation-wiring",
            label="Prepare uses validation command",
            passed=has_all(text, "shipguard prepare", "--validation", "SHIPGUARD_VALIDATION_COMMAND"),
            required=True,
            severity="blocked",
            evidence="shipguard prepare is not clearly wired to SHIPGUARD_VALIDATION_COMMAND.",
            recommendation="Use one validation command value for task preparation, execution, and receipt generation.",
            proof="Rerun this report and inspect the prepared task's validation contract in a PR artifact.",
        )
        check_signal(
            checks,
            findings,
            rule_id="validation-execution",
            label="Validation command executes",
            passed=has_all(text, "bash -lc", "SHIPGUARD_VALIDATION_COMMAND", "/tmp/shipguard-validation.log"),
            required=True,
            severity="blocked",
            evidence="The workflow does not clearly execute the validation command and write a log.",
            recommendation="Run the configured command through bash -lc and capture /tmp/shipguard-validation.log.",
            proof="Confirm the uploaded verdict references a structured receipt for the command that actually ran.",
        )
        check_signal(
            checks,
            findings,
            rule_id="structured-validation-receipt",
            label="Structured validation receipt",
            passed=has_all(text, '"schemaVersion"', '"2.0"', '"receiptType"', '"validation"', '"exitCode"', '"artifact"', "sha256"),
            required=True,
            severity="blocked",
            evidence="The workflow does not clearly write a v2 structured validation receipt with artifact hash.",
            recommendation="Write /tmp/shipguard-validation-receipt.json with schemaVersion 2.0, command, exitCode, status, commit, and log SHA-256.",
            proof="Run shipguard verify with the JSON receipt, not only a plain log.",
        )
        check_signal(
            checks,
            findings,
            rule_id="verify-step",
            label="ShipGuard verify step",
            passed=has_all(text, "shipguard verify", "--task", "/tmp/shipguard-task/shipguard-task.json", "--diff", "/tmp/shipguard-pr.diff", "--evidence", "/tmp/shipguard-validation-receipt.json"),
            required=True,
            severity="blocked",
            evidence="The workflow does not clearly run shipguard verify with task, diff, and validation receipt.",
            recommendation="Keep the verify step explicit and pass the prepared task, PR diff, and structured validation receipt.",
            proof="Inspect /tmp/shipguard-verdict/shipguard-verdict.json from a test PR run.",
        )
        check_signal(
            checks,
            findings,
            rule_id="verify-always-runs",
            label="Verify runs after failed validation",
            passed="if: always()" in text and "shipguard verify" in text,
            required=True,
            severity="review",
            evidence="The verify step is not clearly guarded with if: always().",
            recommendation="Use if: always() so failed validation still produces a ShipGuard verdict artifact.",
            proof="Open a PR with a failing validation command and confirm shipguard-verdict uploads.",
        )
        check_signal(
            checks,
            findings,
            rule_id="proof-artifact-upload",
            label="Proof artifact upload",
            passed=has_all(text, "actions/upload-artifact@v4", "shipguard-verdict", "/tmp/shipguard-verdict"),
            required=True,
            severity="blocked",
            evidence="The workflow does not clearly upload the ShipGuard verdict directory.",
            recommendation="Upload /tmp/shipguard-verdict as the shipguard-verdict artifact so reviewers can inspect JSON and Markdown proof.",
            proof="Confirm the GitHub Actions run exposes shipguard-verdict as a downloadable artifact.",
        )
        if "secrets." in text:
            findings.append(
                finding(
                    "review",
                    "secret-reference-review",
                    "The workflow references GitHub secrets.",
                    "Keep the first verify-PR path free of secrets unless the repo has a reviewed reason.",
                    "Rerun this report after removing secret usage or attach a threat-model note to the PR.",
                    category="security",
                )
            )
            checks.append({"ruleId": "secret-reference-review", "label": "No first-run secrets", "required": False, "status": "review"})

        blocked = [item for item in findings if item["severity"] == "blocked"]
        review = [item for item in findings if item["severity"] == "review"]
        status = "blocked" if blocked else "review" if review else "pass"

    blocked_count = sum(1 for item in findings if item["severity"] == "blocked")
    review_count = sum(1 for item in findings if item["severity"] == "review")
    next_command = (
        "shipguard action verify-pr --workflow .github/workflows/shipguard-verify-pr.yml --out /tmp/shipguard-action-verify-pr --shareable"
        if status != "pass"
        else "gh run download <run-id> --name shipguard-verdict --dir /tmp/shipguard-verdict-artifact"
    )
    result_ux = build_result_ux(
        status=status,
        summary=f"{len(checks)} verify-PR workflow signal(s) checked; {blocked_count} blocked, {review_count} review.",
        proof_source="read-only workflow text inspection; no target validation command executed",
        why_it_matters="The first GitHub Action path should fail setup mistakes before a maintainer trusts a missing or decorative proof artifact.",
        next_command=next_command,
        next_action_summary=(
            findings[0]["recommendation"]
            if findings
            else "Workflow is structurally ready for a real PR run; open a tiny PR, then download and inspect the uploaded shipguard-verdict artifact."
        ),
    )

    return {
        "schemaVersion": SCHEMA_VERSION,
        "tool": TOOL,
        "surface": SURFACE,
        "generatedAt": utc_now(),
        "status": status,
        "path": "." if args.shareable else str(root),
        "workflow": rel_path(workflow, root, args.shareable),
        "summary": {
            "checks": len(checks),
            "blockedFindings": blocked_count,
            "reviewFindings": review_count,
            "placeholderValidationCommand": PLACEHOLDER in text,
            "runtimeProofRequired": True,
        },
        "checks": checks,
        "findings": findings,
        "firstRunProofPath": [
            {"step": "Copy the transparent workflow starter.", "command": "cp examples/workflows/verify-pr.yml .github/workflows/shipguard-verify-pr.yml"},
            {"step": "Replace the placeholder validation command.", "command": "edit SHIPGUARD_VALIDATION_COMMAND in .github/workflows/shipguard-verify-pr.yml"},
            {"step": "Run the read-only setup audit.", "command": "shipguard action verify-pr --workflow .github/workflows/shipguard-verify-pr.yml --out /tmp/shipguard-action-verify-pr --shareable"},
            {"step": "Open a tiny PR and inspect the uploaded proof.", "command": "download the shipguard-verdict artifact from the GitHub Actions run"},
        ],
        "scopeBoundary": {
            "readOnly": True,
            "doesNotRunValidationCommand": True,
            "doesNotPush": True,
            "doesNotModifyTargetRepo": True,
            "shipguardOnly": True,
        },
        "nonClaims": [
            "This report does not prove the workflow has run on GitHub.",
            "This report does not prove the target repository's tests pass.",
            "This report does not replace inspecting the uploaded shipguard-verdict artifact from a real PR run.",
        ],
        "reportQualityQuestions": [
            "Does the report tell a fresh maintainer exactly why their verify-PR workflow is not ready yet?",
            "Does it distinguish static workflow setup proof from runtime GitHub artifact proof?",
            "Does it block missing task/diff/receipt/verify/upload wiring instead of accepting decorative workflow text?",
        ],
        "resultUX": result_ux,
        "shareable": bool(args.shareable),
        "shipguardEval": bool(args.shipguard_eval),
    }


def render_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# ShipGuard Verify-PR First-Run Proof",
        "",
        *render_result_markdown(report["resultUX"]),
        "",
        "## Summary",
        "",
        f"- Status: `{report['status']}`",
        f"- Workflow: `{report['workflow']}`",
        f"- Checks: {report['summary']['checks']}",
        f"- Blocked findings: {report['summary']['blockedFindings']}",
        f"- Review findings: {report['summary']['reviewFindings']}",
        f"- Placeholder validation command: {report['summary']['placeholderValidationCommand']}",
        f"- Runtime proof required: {report['summary']['runtimeProofRequired']}",
        "",
        "## Checks",
        "",
        "| Status | Rule | Required | Signal |",
        "| --- | --- | --- | --- |",
    ]
    for item in report["checks"]:
        lines.append(f"| `{item['status']}` | `{item['ruleId']}` | {item['required']} | {item['label']} |")
    lines.extend(["", "## Findings", ""])
    if report["findings"]:
        lines.extend(["| Severity | Rule | Evidence | Recommendation |", "| --- | --- | --- | --- |"])
        for item in report["findings"]:
            lines.append(f"| `{item['severity']}` | `{item['ruleId']}` | {item['evidence']} | {item['recommendation']} |")
    else:
        lines.append("No static verify-PR setup findings.")
    lines.extend(["", "## First-Run Proof Path", ""])
    for item in report["firstRunProofPath"]:
        lines.append(f"- {item['step']} `{item['command']}`")
    lines.extend(["", "## Scope Boundary", ""])
    for key, value in report["scopeBoundary"].items():
        lines.append(f"- `{key}`: {value}")
    lines.extend(["", "## Non-Claims", ""])
    for item in report["nonClaims"]:
        lines.append(f"- {item}")
    lines.extend(["", "## Report-Quality Questions", ""])
    for item in report["reportQualityQuestions"]:
        lines.append(f"- {item}")
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit the transparent ShipGuard verify-PR GitHub Actions workflow without executing target tests.")
    parser.add_argument("--path", default=".", help="Repository root for relative workflow paths.")
    parser.add_argument("--workflow", default="examples/workflows/verify-pr.yml", help="Workflow file to inspect.")
    parser.add_argument("--out", required=False, help="Output directory.")
    parser.add_argument("--shipguard-eval", action="store_true", help="Mark output as ShipGuard product QA.")
    parser.add_argument("--shareable", action="store_true", help="Redact local absolute paths from report fields.")
    parser.add_argument("--json", action="store_true", help="Print JSON to stdout instead of writing files.")
    parser.add_argument("--markdown", action="store_true", help="Print Markdown to stdout instead of writing files.")
    args = parser.parse_args()

    report = build_report(args)
    markdown = render_markdown(report)
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    elif args.markdown:
        print(markdown)
    else:
        if not args.out:
            parser.error("--out is required unless --json or --markdown is used")
        out_dir = Path(args.out)
        out_dir.mkdir(parents=True, exist_ok=True)
        json_path = out_dir / "action-verify-pr.json"
        markdown_path = out_dir / "action-verify-pr.md"
        json_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        markdown_path.write_text(markdown, encoding="utf-8")
        print(f"wrote: {json_path}")
        print(f"wrote: {markdown_path}")
        print(f"status: {report['status']}")
    return 0 if report["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
