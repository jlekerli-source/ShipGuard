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


def load_json(path: Path) -> tuple[dict[str, Any] | None, str]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return None, "file not found"
    except json.JSONDecodeError as exc:
        return None, f"invalid JSON: {exc}"
    if not isinstance(data, dict):
        return None, "JSON root is not an object"
    return data, ""


def get_path(data: dict[str, Any], path: str) -> Any:
    current: Any = data
    for part in path.split("."):
        if not isinstance(current, dict):
            return None
        current = current.get(part)
    return current


def find_verdict_json(artifact_dir: Path) -> list[Path]:
    if not artifact_dir.exists():
        return []
    if artifact_dir.is_file() and artifact_dir.name == "shipguard-verdict.json":
        return [artifact_dir]
    return sorted(item for item in artifact_dir.rglob("shipguard-verdict.json") if item.is_file())


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
    category: str = "workflow",
) -> None:
    checks.append({"ruleId": rule_id, "label": label, "required": required, "status": "pass" if passed else severity})
    if not passed:
        findings.append(finding(severity, rule_id, evidence, recommendation, proof, category=category))


def inspect_runtime_artifact(args: argparse.Namespace, root: Path) -> dict[str, Any]:
    artifact_arg = getattr(args, "artifact_dir", "") or ""
    if not artifact_arg:
        return {
            "provided": False,
            "status": "not-provided",
            "checks": [],
            "findings": [],
            "verdictStatus": "",
            "verdictPath": "",
            "markdownPath": "",
            "proofReportSummary": "",
            "proofReportNextAction": "",
            "validationCoverageStatus": "",
            "evidenceReceiptSchemaVersion": "",
            "mergeVerdictStatus": "",
            "mergeVerdictAllowed": None,
            "changedFileCount": 0,
            "summary": "No downloaded shipguard-verdict artifact was provided.",
        }

    artifact_dir = Path(artifact_arg)
    if not artifact_dir.is_absolute():
        artifact_dir = root / artifact_dir

    checks: list[dict[str, Any]] = []
    findings: list[dict[str, Any]] = []
    verdict_candidates = find_verdict_json(artifact_dir)
    artifact_exists = artifact_dir.exists()
    artifact_display = rel_path(artifact_dir, root, bool(args.shareable))
    check_signal(
        checks,
        findings,
        rule_id="runtime-artifact-directory-present",
        label="Downloaded artifact directory exists",
        passed=artifact_exists,
        required=True,
        severity="blocked",
        evidence=f"Artifact directory not found: {artifact_display}",
        recommendation="Download the GitHub Actions artifact before runtime verification.",
        proof="Run gh run download <run-id> --name shipguard-verdict --dir /tmp/shipguard-verdict-artifact.",
    )
    check_signal(
        checks,
        findings,
        rule_id="runtime-verdict-json-present",
        label="shipguard-verdict.json present",
        passed=len(verdict_candidates) >= 1,
        required=True,
        severity="blocked",
        evidence="No shipguard-verdict.json file was found in the downloaded artifact.",
        recommendation="Confirm the workflow uploads /tmp/shipguard-verdict as the shipguard-verdict artifact.",
        proof="Download the artifact again and rerun shipguard action verify-pr --artifact-dir <dir>.",
    )
    if len(verdict_candidates) > 1:
        checks.append({"ruleId": "runtime-verdict-json-unique", "label": "Single verdict JSON", "required": False, "status": "review"})
        findings.append(
            finding(
                "review",
                "runtime-verdict-json-unique",
                f"Found {len(verdict_candidates)} shipguard-verdict.json files under the artifact directory.",
                "Keep the uploaded artifact to one ShipGuard verdict directory so reviewers do not choose between conflicting reports.",
                "Rerun after downloading the intended artifact name or cleaning duplicate extracted directories.",
                category="artifact",
            )
        )
    elif verdict_candidates:
        checks.append({"ruleId": "runtime-verdict-json-unique", "label": "Single verdict JSON", "required": False, "status": "pass"})

    verdict_path = verdict_candidates[0] if verdict_candidates else artifact_dir / "shipguard-verdict.json"
    verdict, parse_error = load_json(verdict_path)
    check_signal(
        checks,
        findings,
        rule_id="runtime-verdict-json-parseable",
        label="Verdict JSON parses",
        passed=verdict is not None,
        required=True,
        severity="blocked",
        evidence=parse_error or "shipguard-verdict.json could not be parsed.",
        recommendation="Use the JSON artifact produced by shipguard verify, not a log or partial file.",
        proof="Open shipguard-verdict.json and confirm it is valid JSON.",
    )

    verdict_status = ""
    markdown_path = verdict_path.with_suffix(".md")
    proof_report_summary = ""
    proof_report_next_action = ""
    validation_coverage_status = ""
    evidence_receipt_schema_version = ""
    merge_verdict_status = ""
    merge_verdict_allowed: bool | None = None
    changed_file_count = 0
    if verdict is not None:
        verdict_status = str(verdict.get("status") or "")
        proof_report_summary = str(get_path(verdict, "proofReport.summary") or "")
        proof_report_next_action = str(get_path(verdict, "proofReport.nextAction.command") or "")
        validation_coverage_status = str(get_path(verdict, "validationCoverage.status") or "")
        evidence_receipt_schema_version = str(get_path(verdict, "evidenceReceiptSchema.schemaVersion") or "")
        merge_verdict = get_path(verdict, "diffFirstAnalysis.mergeVerdict")
        if isinstance(merge_verdict, dict):
            merge_verdict_status = str(merge_verdict.get("status") or "")
            allowed = merge_verdict.get("allowed")
            if isinstance(allowed, bool):
                merge_verdict_allowed = allowed
        changed_files = get_path(verdict, "diffFirstAnalysis.changedFiles")
        if isinstance(changed_files, list):
            changed_file_count = len(changed_files)
        required_paths = [
            ("runtime-verdict-tool", "tool", "shipguard verify", "Verdict came from shipguard verify"),
            ("runtime-verdict-status", "status", None, "Verdict status present"),
            ("runtime-proof-report", "proofReport.summary", None, "Proof report summary present"),
            ("runtime-proof-report-validation", "proofReport.validation.status", None, "Proof report validation status present"),
            ("runtime-proof-report-claims", "proofReport.claims.label", None, "Proof report claim summary present"),
            ("runtime-validation-coverage", "validationCoverage.status", None, "Validation coverage present"),
            ("runtime-evidence-receipt-schema", "evidenceReceiptSchema.schemaVersion", "2.0", "Evidence receipt schema v2 present"),
            ("runtime-diff-first-analysis", "diffFirstAnalysis.mergeVerdict", None, "Diff-first merge verdict present"),
            ("runtime-next-action", "proofReport.nextAction.command", None, "Next action command present"),
        ]
        for rule_id, path, expected, label in required_paths:
            value = get_path(verdict, path)
            passed = bool(value) if expected is None else value == expected
            check_signal(
                checks,
                findings,
                rule_id=rule_id,
                label=label,
                passed=passed,
                required=True,
                severity="blocked",
                evidence=f"{path} is {value!r}; expected {expected!r}" if expected is not None else f"{path} is missing or empty.",
                recommendation="Download the full shipguard-verdict artifact produced by shipguard verify.",
                proof="Inspect shipguard-verdict.json and rerun this runtime artifact audit.",
                category="artifact",
            )
        if verdict_status not in {"pass", "review", "blocked"}:
            checks.append({"ruleId": "runtime-verdict-status-known", "label": "Verdict status is recognized", "required": True, "status": "blocked"})
            findings.append(
                finding(
                    "blocked",
                    "runtime-verdict-status-known",
                    f"Verdict status {verdict_status!r} is not one of pass/review/blocked.",
                    "Use a current shipguard verify artifact so automation can route the PR result.",
                    "Regenerate the artifact with shipguard verify from the current toolkit.",
                    category="artifact",
                )
            )
        else:
            checks.append({"ruleId": "runtime-verdict-status-known", "label": "Verdict status is recognized", "required": True, "status": "pass"})

    markdown_exists = markdown_path.exists()
    check_signal(
        checks,
        findings,
        rule_id="runtime-verdict-markdown-present",
        label="shipguard-verdict.md present",
        passed=markdown_exists,
        required=True,
        severity="review",
        evidence=f"Markdown verdict not found beside JSON: {rel_path(markdown_path, root, bool(args.shareable))}",
        recommendation="Upload both shipguard-verdict.json and shipguard-verdict.md so humans can inspect the proof without parsing JSON.",
        proof="Download the artifact and confirm shipguard-verdict.md is present.",
        category="artifact",
    )
    if markdown_exists:
        markdown = read_text(markdown_path)
        check_signal(
            checks,
            findings,
            rule_id="runtime-verdict-markdown-proof-report",
            label="Markdown renders proof report",
            passed="ShipGuard Proof Report" in markdown,
            required=True,
            severity="review",
            evidence="shipguard-verdict.md does not contain the proof-report heading.",
            recommendation="Upload the Markdown emitted by shipguard verify, not a renamed or truncated file.",
            proof="Open shipguard-verdict.md and confirm the top proof report is readable.",
            category="artifact",
        )

    blocked = [item for item in findings if item["severity"] == "blocked"]
    review = [item for item in findings if item["severity"] == "review"]
    status = "blocked" if blocked else "review" if review else "pass"
    return {
        "provided": True,
        "path": artifact_display,
        "status": status,
        "checks": checks,
        "findings": findings,
        "verdictStatus": verdict_status,
        "verdictPath": rel_path(verdict_path, root, bool(args.shareable)) if verdict_candidates else "",
        "markdownPath": rel_path(markdown_path, root, bool(args.shareable)) if markdown_exists else "",
        "proofReportSummary": proof_report_summary,
        "proofReportNextAction": proof_report_next_action,
        "validationCoverageStatus": validation_coverage_status,
        "evidenceReceiptSchemaVersion": evidence_receipt_schema_version,
        "mergeVerdictStatus": merge_verdict_status,
        "mergeVerdictAllowed": merge_verdict_allowed,
        "changedFileCount": changed_file_count,
        "summary": f"{len(checks)} runtime artifact signal(s) checked; verdict status {verdict_status or 'unknown'}.",
    }


def prioritized_finding(findings: list[dict[str, Any]]) -> dict[str, Any] | None:
    for severity in ("blocked", "review", "opportunity"):
        for item in findings:
            if item.get("severity") == severity:
                return item
    return findings[0] if findings else None


def phase_summary(title: str, findings: list[dict[str, Any]], *, not_run: bool = False) -> dict[str, Any]:
    blocked = [item for item in findings if item.get("severity") == "blocked"]
    review = [item for item in findings if item.get("severity") == "review"]
    first = prioritized_finding(findings)
    if not_run:
        status = "not-run"
    elif blocked:
        status = "blocked"
    elif review:
        status = "review"
    else:
        status = "pass"
    return {
        "title": title,
        "status": status,
        "blockedRules": [str(item.get("ruleId")) for item in blocked],
        "reviewRules": [str(item.get("ruleId")) for item in review],
        "firstFix": {
            "ruleId": str(first.get("ruleId")) if first else "",
            "recommendation": str(first.get("recommendation")) if first else "",
            "proofGuidance": str(first.get("proofGuidance")) if first else "",
        },
    }


def build_failure_guide(
    findings: list[dict[str, Any]],
    runtime_artifact: dict[str, Any],
    *,
    static_audit_command: str,
    artifact_audit_command: str,
) -> dict[str, Any]:
    runtime_findings = runtime_artifact.get("findings") if isinstance(runtime_artifact.get("findings"), list) else []
    runtime_ids = {id(item) for item in runtime_findings}
    static_findings = [item for item in findings if id(item) not in runtime_ids]
    first = prioritized_finding(findings)
    runtime_not_run = not bool(runtime_artifact.get("provided"))
    runtime_phase = phase_summary("Runtime artifact proof", runtime_findings, not_run=runtime_not_run)
    if runtime_not_run:
        runtime_phase["firstFix"] = {
            "ruleId": "runtime-artifact-not-provided",
            "recommendation": "Open a tiny PR, download the shipguard-verdict artifact, then rerun this audit with --artifact-dir.",
            "proofGuidance": artifact_audit_command,
        }
    if first:
        summary = f"First blocker: {first.get('ruleId')} - {first.get('recommendation')}"
    elif runtime_not_run:
        summary = "Static setup is ready; runtime proof still needs one small PR run and downloaded shipguard-verdict artifact inspection."
    else:
        summary = "Workflow setup and runtime artifact are ready for reviewer proof routing."
    return {
        "summary": summary,
        "firstBlockingRuleId": str(first.get("ruleId")) if first and first.get("severity") == "blocked" else "",
        "firstAction": {
            "ruleId": str(first.get("ruleId")) if first else "",
            "severity": str(first.get("severity")) if first else "",
            "recommendation": str(first.get("recommendation")) if first else "",
            "proofGuidance": str(first.get("proofGuidance")) if first else "",
        },
        "phases": [
            phase_summary("Static workflow setup", static_findings),
            runtime_phase,
        ],
        "commands": {
            "rerunStaticAudit": static_audit_command,
            "downloadArtifactAndAudit": artifact_audit_command,
        },
    }


def build_runtime_reviewer_handoff(runtime_artifact: dict[str, Any], *, artifact_audit_command: str) -> dict[str, Any]:
    provided = bool(runtime_artifact.get("provided"))
    runtime_status = str(runtime_artifact.get("status") or "")
    verdict_status = str(runtime_artifact.get("verdictStatus") or "")
    merge_status = str(runtime_artifact.get("mergeVerdictStatus") or "")
    merge_allowed = runtime_artifact.get("mergeVerdictAllowed")
    validation_status = str(runtime_artifact.get("validationCoverageStatus") or "")
    schema_version = str(runtime_artifact.get("evidenceReceiptSchemaVersion") or "")
    proof_next_action = str(runtime_artifact.get("proofReportNextAction") or "")
    findings = runtime_artifact.get("findings") if isinstance(runtime_artifact.get("findings"), list) else []
    first_finding = prioritized_finding(findings)
    reviewer_command = "gh pr view <pr-number> --json statusCheckRollup,reviewDecision,mergeStateStatus"
    proof_to_attach = [
        "shipguard-verdict.json",
        "shipguard-verdict.md",
        "validation receipt referenced by shipguard-verdict.json",
    ]

    if not provided:
        decision = "download-runtime-artifact"
        reviewer_action = "Open a tiny PR, download the shipguard-verdict artifact, then rerun this audit with --artifact-dir."
        failure_meaning = "Static workflow text can be ready while reviewer proof is still absent; do not treat setup-only output as PR proof."
        reviewer_command = artifact_audit_command
        proof_to_attach = ["downloaded shipguard-verdict artifact from a real pull request run"]
    elif runtime_status != "pass":
        decision = "do-not-use-artifact"
        reviewer_action = str(first_finding.get("recommendation")) if first_finding else "Regenerate the shipguard-verdict artifact before review."
        failure_meaning = "The downloaded artifact is incomplete, stale, or not produced by shipguard verify, so it cannot route a reviewer decision."
        reviewer_command = artifact_audit_command
    elif merge_allowed is False or verdict_status == "blocked" or merge_status == "blocked":
        decision = "do-not-merge"
        reviewer_action = proof_next_action or "Keep the PR blocked until ShipGuard verification and normal review are green."
        failure_meaning = "The artifact is consumable, but its verdict says the PR is blocked."
    elif verdict_status == "review" or merge_status == "review":
        decision = "needs-maintainer-review"
        reviewer_action = proof_next_action or "Attach the verdict artifacts and complete manual maintainer review before merging."
        failure_meaning = "The artifact is consumable, but it requests maintainer review instead of a clean pass."
    elif verdict_status == "pass" and merge_allowed is True:
        decision = "ready-for-maintainer-review"
        reviewer_action = proof_next_action or "Attach the verdict artifacts to the PR and finish normal code review."
        failure_meaning = "No ShipGuard runtime-artifact blocker was found; this is proof routing, not automatic merge permission."
    else:
        decision = "needs-maintainer-review"
        reviewer_action = proof_next_action or "Inspect the verdict artifact and complete normal maintainer review."
        failure_meaning = "The artifact is consumable, but ShipGuard could not reduce it to a clean pass/block decision."

    return {
        "applicable": provided,
        "decision": decision,
        "verdictStatus": verdict_status,
        "mergeVerdictStatus": merge_status,
        "mergeVerdictAllowed": merge_allowed,
        "validationCoverageStatus": validation_status,
        "evidenceReceiptSchemaVersion": schema_version,
        "changedFileCount": runtime_artifact.get("changedFileCount") or 0,
        "reviewerCommand": reviewer_command,
        "reviewerAction": reviewer_action,
        "proofToAttach": proof_to_attach,
        "failureMeaning": failure_meaning,
        "nonClaim": "ShipGuard verifies the uploaded proof artifact and workflow wiring; it does not replace normal PR review or repository policy.",
    }


def build_first_run_install_handoff(*, workflow_path: str) -> dict[str, Any]:
    copy_command = "mkdir -p .github/workflows && cp examples/workflows/verify-pr.yml .github/workflows/shipguard-verify-pr.yml"
    static_audit_command = f"shipguard action verify-pr --workflow {workflow_path} --out /tmp/shipguard-action-verify-pr --shareable"
    artifact_audit_command = (
        "gh run download <run-id> --name shipguard-verdict --dir /tmp/shipguard-verdict-artifact && "
        f"shipguard action verify-pr --workflow {workflow_path} --artifact-dir /tmp/shipguard-verdict-artifact --out /tmp/shipguard-action-verify-pr --shareable"
    )
    return {
        "sourceWorkflow": "examples/workflows/verify-pr.yml",
        "destinationWorkflow": workflow_path,
        "copyCommand": copy_command,
        "configureCommand": f"edit SHIPGUARD_VALIDATION_COMMAND in {workflow_path}",
        "staticAuditCommand": static_audit_command,
        "runtimeArtifactCommand": artifact_audit_command,
        "proofBoundary": "This installs the transparent workflow starter and audits wiring; it does not prove a real PR run until the uploaded shipguard-verdict artifact is downloaded and consumed.",
    }


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

    runtime_artifact = inspect_runtime_artifact(args, root)
    artifact_findings = runtime_artifact.get("findings") if isinstance(runtime_artifact.get("findings"), list) else []
    findings.extend(artifact_findings)
    if runtime_artifact.get("provided"):
        checks.extend(runtime_artifact.get("checks") or [])

    blocked_count = sum(1 for item in findings if item["severity"] == "blocked")
    review_count = sum(1 for item in findings if item["severity"] == "review")
    status = "blocked" if blocked_count else "review" if review_count else "pass"
    first_run_handoff = build_first_run_install_handoff(workflow_path=".github/workflows/shipguard-verify-pr.yml")
    artifact_audit_command = first_run_handoff["runtimeArtifactCommand"]
    static_audit_command = first_run_handoff["staticAuditCommand"]
    runtime_reviewer_handoff = build_runtime_reviewer_handoff(runtime_artifact, artifact_audit_command=artifact_audit_command)
    if status == "pass" and runtime_artifact.get("provided"):
        next_command = str(runtime_reviewer_handoff.get("reviewerCommand") or "")
    elif runtime_artifact.get("provided") and runtime_artifact.get("status") != "pass":
        next_command = artifact_audit_command
    elif status == "pass":
        next_command = artifact_audit_command
    else:
        next_command = static_audit_command
    failure_guide = build_failure_guide(
        findings,
        runtime_artifact,
        static_audit_command=static_audit_command,
        artifact_audit_command=artifact_audit_command,
    )
    next_finding = prioritized_finding(findings)
    proof_source = (
        "read-only workflow text inspection plus downloaded shipguard-verdict artifact inspection; no target validation command executed locally"
        if runtime_artifact.get("provided")
        else "read-only workflow text inspection; no target validation command executed"
    )
    result_ux = build_result_ux(
        status=status,
        summary=f"{len(checks)} verify-PR workflow signal(s) checked; {blocked_count} blocked, {review_count} review.",
        proof_source=proof_source,
        why_it_matters="The first GitHub Action path should fail setup mistakes before a maintainer trusts a missing or decorative proof artifact.",
        next_command=next_command,
        next_action_summary=(
            next_finding["recommendation"]
            if next_finding
            else (
                str(runtime_reviewer_handoff.get("reviewerAction") or "")
                if runtime_artifact.get("provided")
                else "Workflow is structurally ready for a real PR run; open a tiny PR, then download and inspect the uploaded shipguard-verdict artifact with ShipGuard."
            )
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
            "runtimeArtifactProvided": bool(runtime_artifact.get("provided")),
        },
        "checks": checks,
        "findings": findings,
        "runtimeArtifact": runtime_artifact,
        "runtimeReviewerHandoff": runtime_reviewer_handoff,
        "freshMaintainerFailureGuide": failure_guide,
        "firstRunInstallHandoff": first_run_handoff,
        "firstRunProofPath": [
            {"step": "Copy the transparent workflow starter.", "command": first_run_handoff["copyCommand"]},
            {"step": "Replace the placeholder validation command.", "command": first_run_handoff["configureCommand"]},
            {"step": "Run the read-only setup audit.", "command": first_run_handoff["staticAuditCommand"]},
            {"step": "Open a tiny PR and inspect the uploaded proof.", "command": first_run_handoff["runtimeArtifactCommand"]},
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
            "Does the freshMaintainerFailureGuide identify the first blocker before lower-severity review items?",
            "Does it distinguish static workflow setup proof from runtime GitHub artifact proof?",
            "Does it block missing task/diff/receipt/verify/upload wiring instead of accepting decorative workflow text?",
            "When a downloaded artifact is provided, does it verify that shipguard-verdict.json and Markdown are complete enough for a reviewer to trust the artifact as proof routing?",
            "When a runtime artifact is consumable, does the report give the reviewer a concrete decision, proof-to-attach list, and failure meaning instead of a vague status note?",
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
        f"- Runtime artifact provided: {report['summary']['runtimeArtifactProvided']}",
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
    artifact = report.get("runtimeArtifact") or {}
    lines.extend(["", "## Runtime Artifact", ""])
    lines.append(f"- Provided: {artifact.get('provided')}")
    lines.append(f"- Status: `{artifact.get('status')}`")
    lines.append(f"- Verdict status: `{artifact.get('verdictStatus') or 'unknown'}`")
    if artifact.get("verdictPath"):
        lines.append(f"- Verdict JSON: `{artifact.get('verdictPath')}`")
    if artifact.get("markdownPath"):
        lines.append(f"- Verdict Markdown: `{artifact.get('markdownPath')}`")
    lines.append(f"- Summary: {artifact.get('summary')}")
    reviewer = report.get("runtimeReviewerHandoff") if isinstance(report.get("runtimeReviewerHandoff"), dict) else {}
    lines.extend(["", "## Runtime Reviewer Handoff", ""])
    lines.append(f"- Decision: `{reviewer.get('decision') or 'unknown'}`")
    lines.append(f"- Verdict status: `{reviewer.get('verdictStatus') or 'unknown'}`")
    lines.append(f"- Merge verdict: `{reviewer.get('mergeVerdictStatus') or 'unknown'}` (allowed: {reviewer.get('mergeVerdictAllowed')})")
    lines.append(f"- Validation coverage: `{reviewer.get('validationCoverageStatus') or 'unknown'}`")
    lines.append(f"- Evidence receipt schema: `{reviewer.get('evidenceReceiptSchemaVersion') or 'unknown'}`")
    lines.append(f"- Changed files in verdict: {reviewer.get('changedFileCount') or 0}")
    if reviewer.get("reviewerCommand"):
        lines.append(f"- Reviewer command: `{reviewer.get('reviewerCommand')}`")
    lines.append(f"- Reviewer action: {reviewer.get('reviewerAction')}")
    proof_to_attach = reviewer.get("proofToAttach") if isinstance(reviewer.get("proofToAttach"), list) else []
    if proof_to_attach:
        lines.append("- Proof to attach:")
        for item in proof_to_attach:
            lines.append(f"  - {item}")
    lines.append(f"- Failure meaning: {reviewer.get('failureMeaning')}")
    lines.append(f"- Non-claim: {reviewer.get('nonClaim')}")
    guide = report.get("freshMaintainerFailureGuide") or {}
    lines.extend(["", "## Fresh Maintainer Failure Guide", ""])
    lines.append(f"- Summary: {guide.get('summary')}")
    first_action = guide.get("firstAction") if isinstance(guide.get("firstAction"), dict) else {}
    if first_action.get("ruleId"):
        lines.append(f"- First action: `{first_action.get('ruleId')}` ({first_action.get('severity')}) - {first_action.get('recommendation')}")
    phases = guide.get("phases") if isinstance(guide.get("phases"), list) else []
    if phases:
        lines.extend(["", "| Phase | Status | First fix |", "| --- | --- | --- |"])
        for phase in phases:
            if not isinstance(phase, dict):
                continue
            first_fix = phase.get("firstFix") if isinstance(phase.get("firstFix"), dict) else {}
            fix_text = first_fix.get("recommendation") or "No action required."
            lines.append(f"| {phase.get('title')} | `{phase.get('status')}` | {fix_text} |")
    handoff = report.get("firstRunInstallHandoff") if isinstance(report.get("firstRunInstallHandoff"), dict) else {}
    lines.extend(["", "## First-Run Install Handoff", ""])
    lines.append(f"- Source workflow: `{handoff.get('sourceWorkflow')}`")
    lines.append(f"- Destination workflow: `{handoff.get('destinationWorkflow')}`")
    lines.append(f"- Copy command: `{handoff.get('copyCommand')}`")
    lines.append(f"- Configure command: `{handoff.get('configureCommand')}`")
    lines.append(f"- Static audit: `{handoff.get('staticAuditCommand')}`")
    lines.append(f"- Runtime artifact audit: `{handoff.get('runtimeArtifactCommand')}`")
    lines.append(f"- Proof boundary: {handoff.get('proofBoundary')}")
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
    parser.add_argument("--artifact-dir", default="", help="Downloaded shipguard-verdict artifact directory from gh run download.")
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
