#!/usr/bin/env python3
"""ShipGuard Lean Review: review a diff for unnecessary code."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import re
from pathlib import Path
from typing import Any

from lean_audit import build_precision_review, finding, has_safety_context, read_text


TOOL = "shipguard lean review"
SURFACE = "ShipGuard Lean Review"
SCHEMA_VERSION = 1
CODE_SUFFIXES = {".js", ".jsx", ".ts", ".tsx", ".mjs", ".cjs", ".py", ".sh", ".swift"}


def utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Review a unified diff for over-engineering, thin wrappers, native replacements, and proof-required safety boundaries."
    )
    parser.add_argument("--diff", required=True, help="Unified diff/patch to inspect")
    parser.add_argument("--path", default=".", help="Repository root used for context and shareable locations")
    parser.add_argument("--out", required=True, help="Output directory")
    parser.add_argument("--shipguard-eval", action="store_true", help="Add ShipGuard-only report-quality questions")
    parser.add_argument("--shareable", action="store_true", help="Omit local absolute roots from JSON and Markdown")
    parser.add_argument("--json", action="store_true", help="Print JSON report to stdout")
    parser.add_argument("--markdown", action="store_true", help="Print Markdown report to stdout")
    return parser.parse_args()


def parse_unified_diff(text: str) -> list[dict[str, Any]]:
    files: list[dict[str, Any]] = []
    current: dict[str, Any] | None = None
    new_line = 0
    for line in text.splitlines():
        if line.startswith("diff --git "):
            if current:
                files.append(current)
            parts = line.split()
            file_name = parts[-1][2:] if len(parts) >= 4 and parts[-1].startswith("b/") else parts[-1]
            current = {"file": file_name, "added": [], "removed": []}
            new_line = 0
            continue
        if current is None:
            continue
        if line.startswith("+++ "):
            target = line[4:].strip()
            if target.startswith("b/"):
                current["file"] = target[2:]
            continue
        hunk = re.match(r"@@ -\d+(?:,\d+)? \+(\d+)(?:,\d+)? @@", line)
        if hunk:
            new_line = int(hunk.group(1)) - 1
            continue
        if line.startswith("+") and not line.startswith("+++"):
            new_line += 1
            current["added"].append({"line": new_line, "text": line[1:]})
            continue
        if line.startswith("-") and not line.startswith("---"):
            current["removed"].append({"text": line[1:]})
            continue
        if line.startswith(" "):
            new_line += 1
    if current:
        files.append(current)
    return files


def line_texts(file_diff: dict[str, Any]) -> list[str]:
    return [str(item.get("text", "")) for item in file_diff.get("added", [])]


def first_added_line(file_diff: dict[str, Any], pattern: str) -> int | None:
    regex = re.compile(pattern, re.IGNORECASE)
    for item in file_diff.get("added", []):
        if regex.search(str(item.get("text", ""))):
            return int(item.get("line") or 0) or None
    return None


def scan_diff(root: Path, files: list[dict[str, Any]]) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    for file_diff in files:
        file_name = str(file_diff.get("file", ""))
        suffix = Path(file_name).suffix
        is_code = suffix in CODE_SUFFIXES
        added_lines = line_texts(file_diff)
        added_text = "\n".join(added_lines)
        if not added_text.strip():
            continue
        context_path = root / file_name
        context_text = read_text(context_path)
        safe_context = has_safety_context(context_path, context_text + "\n" + added_text)

        checks = [
            (
                "native-date-input-diff",
                r"(react-datepicker|flatpickr|moment|date-fns|luxon|dayjs|<DatePicker\b)",
                "native",
                "Date-picker/date-helper code added in this diff. Try the platform date control or formatter before owning custom picker plumbing.",
                "Prove locale, timezone, invalid input, and interaction behavior before deleting or adding custom date behavior.",
            ),
            (
                "native-color-input-diff",
                r"(react-color|tinycolor|SketchPicker|ChromePicker|ColorPicker)",
                "native",
                "Color-picker code added in this diff. Try native color controls or design-token selection before custom picker state.",
                "Keep custom code only when palette constraints, alpha, contrast, or brand-token rules are product requirements.",
            ),
            (
                "stdlib-url-params-diff",
                r"(split\([\"']&[\"']\)|split\([\"']=[\"']\)|encodeURIComponent|decodeURIComponent)",
                "stdlib",
                "Manual query-string parsing appeared in the diff. Prefer URL and URLSearchParams when runtime support allows it.",
                "Add one check for repeated keys, empty values, encoding, and malformed input before replacing behavior.",
            ),
            (
                "dependency-small-helper-diff",
                r"(from [\"']lodash|require\([\"']lodash|from [\"']underscore|require\([\"']underscore)",
                "stdlib",
                "A general utility dependency was added or touched. Check whether language/runtime primitives cover the actual call site.",
                "List actual imports and keep the dependency when it provides meaningful edge-case behavior.",
            ),
            (
                "deferred-shortcut-without-trigger",
                r"^\s*(#|//|/\*|<!--)\s*(ponytail|shipguard-lean):(?!(?=.*\bceiling\s*:)(?=.*\bupgrade\s*:))",
                "debt",
                "A lean shortcut marker was added without both a ceiling and an upgrade trigger.",
                "Use `ceiling:` and `upgrade:` in the comment so the shortcut is reviewable later.",
            ),
            (
                "speculative-future-hook-diff",
                r"\b(TODO|FIXME|temporary|for later|future-proof|placeholder)\b",
                "delete",
                "Speculative or placeholder wording was added. Delete it unless it is tied to an accepted task or proof boundary.",
                "If the placeholder must stay, link it to an owner, trigger, and validation path.",
            ),
        ]
        for rule_id, pattern, category, recommendation, proof in checks:
            if category == "delete" and not is_code:
                continue
            if not re.search(pattern, added_text, flags=re.IGNORECASE | re.MULTILINE):
                continue
            findings.append(
                finding(
                    severity="review" if category in {"delete", "debt"} else "opportunity",
                    category=f"{category}-diff-review",
                    rule_id=rule_id,
                    file=file_name,
                    line=first_added_line(file_diff, pattern),
                    evidence=next((line.strip() for line in added_lines if re.search(pattern, line, re.IGNORECASE)), "")[:160],
                    recommendation=recommendation,
                    proof=proof,
                )
            )

        wrapper_match = re.search(
            r"(?:export\s+)?(?:function|const)\s+([A-Za-z0-9_]+)\s*(?:=\s*)?(?:\([^)]*\)|[^=]*)\s*(?:=>|\{)\s*(?:return\s+)?([A-Za-z0-9_.]+)\([^;\n{}]*\)",
            added_text,
        )
        if wrapper_match and not safe_context:
            findings.append(
                finding(
                    severity="opportunity",
                    category="yagni-diff-review",
                    rule_id="thin-wrapper-diff-review",
                    file=file_name,
                    line=first_added_line(file_diff, re.escape(wrapper_match.group(1))),
                    evidence=f"{wrapper_match.group(1)} delegates to {wrapper_match.group(2)}",
                    recommendation="Inline or delete this wrapper unless it adds policy, naming, compatibility, logging, typing, or test value.",
                    proof="Search call sites and keep one small check if behavior is non-trivial.",
                )
            )

        if safe_context:
            findings.append(
                finding(
                    severity="info",
                    category="safety-boundary",
                    rule_id="do-not-cut-safety-diff-without-proof",
                    file=file_name,
                    line=None,
                    evidence="diff touches security/validation/accessibility/data-loss terms",
                    recommendation="Less code is not the goal in this file until behavior proof exists.",
                    proof="Attach focused before/after tests for trust-boundary, data-loss, security, permission, or accessibility behavior.",
                )
            )
    return findings


def review_lines(findings: list[dict[str, Any]]) -> list[str]:
    lines: list[str] = []
    for item in findings:
        if item.get("severity") == "info":
            continue
        evidence = item.get("evidence", {})
        location = str(evidence.get("file", ""))
        if evidence.get("line"):
            location = f"{location}:L{evidence['line']}"
        tag = str(item.get("category", "")).split("-")[0] or "review"
        lines.append(f"{location}: {tag}: {item.get('recommendation')}")
    return lines


def build_report(args: argparse.Namespace) -> dict[str, Any]:
    root = Path(args.path).resolve()
    diff_path = Path(args.diff)
    if not diff_path.exists():
        raise SystemExit(f"lean-review: diff does not exist: {diff_path}")
    diff_text = diff_path.read_text(encoding="utf-8", errors="ignore")
    files = parse_unified_diff(diff_text)
    findings = scan_diff(root, files)
    precision = build_precision_review(findings)
    status = "pass" if not [item for item in findings if item.get("severity") in {"review", "opportunity"}] else "review"
    report: dict[str, Any] = {
        "schemaVersion": SCHEMA_VERSION,
        "tool": TOOL,
        "surface": SURFACE,
        "generatedAt": utc_now(),
        "status": status,
        "target": {"path": "." if args.shareable else str(root), "shareable": bool(args.shareable)},
        "diff": {"path": diff_path.name if args.shareable else str(diff_path), "filesChanged": len(files)},
        "sourceInfluence": {
            "name": "Ponytail",
            "url": "https://github.com/DietrichGebert/ponytail",
            "boundary": "ShipGuard implements a native diff review for unnecessary code. It does not vendor Ponytail code.",
        },
        "reviewLines": review_lines(findings),
        "precisionReview": precision,
        "findings": findings,
        "metrics": {
            "filesChanged": len(files),
            "addedLines": sum(len(item.get("added", [])) for item in files),
            "findings": len(findings),
            "reviewFindings": len([item for item in findings if item.get("severity") == "review"]),
            "opportunityFindings": len([item for item in findings if item.get("severity") == "opportunity"]),
            "infoFindings": len([item for item in findings if item.get("severity") == "info"]),
        },
        "nextActions": [
            "Start with reviewLines[0] or precisionReview.topActions[0].",
            "Delete or simplify only when search proof and a small runnable check preserve behavior.",
            "Use shipguard lean audit for whole-repo cleanup after the diff-specific review is handled.",
        ],
    }
    if args.shipguard_eval:
        report["scopeBoundary"] = (
            "This is ShipGuard product QA. The diff is an evaluation input for report usefulness, not authorization to edit a private target."
        )
        report["reportQualityQuestions"] = [
            "Does Lean Review give a current-diff delete/simplify list instead of a whole-repo inventory?",
            "Does it keep safety-boundary code out of automatic deletion?",
            "Does it make the first simplification action obvious enough for a solo developer?",
        ]
    return report


def render_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# ShipGuard Lean Review",
        "",
        f"- Status: {report['status']}",
        f"- Tool: `{report['tool']}`",
        f"- Target: `{report['target']['path']}`",
        f"- Diff files changed: {report['metrics']['filesChanged']}",
        f"- Added lines inspected: {report['metrics']['addedLines']}",
        "",
        "## Diff Review",
        "",
    ]
    if report["reviewLines"]:
        for item in report["reviewLines"]:
            lines.append(f"- {item}")
    else:
        lines.append("Lean already. Ship.")
    precision = report.get("precisionReview", {})
    summary = precision.get("summary", {})
    lines.extend(["", "## Precision Ledger", ""])
    lines.append(
        f"- Delete candidates: {summary.get('deleteCandidates', 0)}; "
        f"simplify candidates: {summary.get('simplifyCandidates', 0)}; "
        f"keep boundaries: {summary.get('keepBoundaries', 0)}; "
        f"proof-blocked candidates: {summary.get('proofBlockedCandidates', 0)}"
    )
    top_actions = precision.get("topActions", [])
    if top_actions:
        lines.extend(["", "| Rank | Location | Action | Proof |", "| ---: | --- | --- | --- |"])
        for action in top_actions:
            lines.append(
                f"| {action.get('rank', '-')} | {action.get('location', '')} | "
                f"{str(action.get('action', '')).replace('|', '\\|')} | "
                f"{str(action.get('proofRequired', '')).replace('|', '\\|')} |"
            )
    lines.extend(["", "## Findings", ""])
    if report["findings"]:
        lines.extend(["| Severity | Rule | Evidence | Recommendation | Proof |", "| --- | --- | --- | --- | --- |"])
        for item in report["findings"]:
            evidence = item["evidence"]
            location = str(evidence.get("file", ""))
            if evidence.get("line"):
                location = f"{location}:{evidence['line']}"
            lines.append(
                f"| {item['severity']} | `{item['ruleId']}` | {location}: {str(evidence.get('snippet', '')).replace('|', '\\|')} | "
                f"{str(item['recommendation']).replace('|', '\\|')} | {str(item['proofGuidance']).replace('|', '\\|')} |"
            )
    else:
        lines.append("No diff-specific lean findings were detected.")
    lines.extend(["", "## Source Influence", ""])
    lines.append(
        f"Native ShipGuard implementation influenced by {report['sourceInfluence']['name']} "
        f"({report['sourceInfluence']['url']}). {report['sourceInfluence']['boundary']}"
    )
    if report.get("scopeBoundary"):
        lines.extend(["", "## Scope Boundary", "", report["scopeBoundary"]])
    if report.get("reportQualityQuestions"):
        lines.extend(["", "## Report Quality Questions", ""])
        for question in report["reportQualityQuestions"]:
            lines.append(f"- {question}")
    lines.extend(["", "## Next Actions", ""])
    for action in report["nextActions"]:
        lines.append(f"- {action}")
    lines.append("")
    return "\n".join(lines)


def main() -> None:
    args = parse_args()
    report = build_report(args)
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    json_text = json.dumps(report, indent=2, sort_keys=True) + "\n"
    md_text = render_markdown(report)
    (out / "lean-review.json").write_text(json_text, encoding="utf-8")
    (out / "lean-review.md").write_text(md_text, encoding="utf-8")
    if args.json:
        print(json_text, end="")
    if args.markdown:
        print(md_text, end="")


if __name__ == "__main__":
    main()
