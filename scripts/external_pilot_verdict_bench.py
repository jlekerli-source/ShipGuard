#!/usr/bin/env python3
"""Score public-safe ShipGuard task traces for PilotBench usefulness."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import sys
from pathlib import Path
from typing import Any


TOOL = "shipguard pilot-bench"
SURFACE = "ShipGuard PilotBench"
SCHEMA_VERSION = 1
BENCHMARK_VERSION = 2
DEFAULT_FIXTURE_ROOT = Path("fixtures") / "external-pilot-verdict-bench"
PRIVATE_TOKEN_RE = re.compile(r"(?i)(/Users/|/private/tmp/|Ringly|Ilmify|Project Ilmify|sk-[A-Za-z0-9_-]{12,}|gh[pousr]_[A-Za-z0-9_]{12,})")


def utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def fail(message: str) -> None:
    print(f"pilot-bench: {message}", file=sys.stderr)
    raise SystemExit(1)


def read_json(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        fail(f"file not found: {path}")
    except json.JSONDecodeError as exc:
        fail(f"invalid JSON in {path}: {exc}")
    if not isinstance(data, dict):
        fail(f"expected JSON object in {path}")
    return data


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def path_label(path: Path, *, root: Path, shareable: bool) -> str:
    if shareable:
        try:
            return path.resolve().relative_to(root.resolve()).as_posix()
        except ValueError:
            return f"<trace-input>/{path.name}"
    return path.as_posix()


def value_at_path(data: Any, dotted: str) -> Any:
    current = data
    for part in dotted.split("."):
        if isinstance(current, dict):
            current = current.get(part)
        elif isinstance(current, list):
            try:
                current = current[int(part)]
            except (ValueError, IndexError):
                return None
        else:
            return None
    return current


def flatten_strings(value: Any) -> list[str]:
    if isinstance(value, str):
        return [value]
    if isinstance(value, dict):
        out: list[str] = []
        for child in value.values():
            out.extend(flatten_strings(child))
        return out
    if isinstance(value, list):
        out: list[str] = []
        for child in value:
            out.extend(flatten_strings(child))
        return out
    return []


def contains_text(value: Any, needle: str) -> bool:
    lowered = needle.lower()
    return any(lowered in text.lower() for text in flatten_strings(value))


def matching_items(values: list[str], expected: list[str]) -> list[str]:
    matches: list[str] = []
    for needle in expected:
        if any(needle.lower() in value.lower() for value in values):
            matches.append(needle)
    return matches


def trace_files(inputs: list[str], *, root: Path) -> list[Path]:
    if not inputs:
        inputs = [str(root / DEFAULT_FIXTURE_ROOT)]
    files: list[Path] = []
    for raw in inputs:
        path = Path(raw)
        if path.is_dir():
            if (path / "trace.json").is_file():
                files.append(path / "trace.json")
            else:
                files.extend(sorted(path.rglob("trace.json")))
        elif path.is_file():
            files.append(path)
        else:
            fail(f"trace input not found: {raw}")
    deduped: list[Path] = []
    seen: set[Path] = set()
    for path in files:
        resolved = path.resolve()
        if resolved not in seen:
            seen.add(resolved)
            deduped.append(path)
    if not deduped:
        fail("no trace.json files found")
    return deduped


def trace_from_loaded(loaded: dict[str, Any], path: Path) -> dict[str, Any]:
    if "task" in loaded or "verdict" in loaded:
        return loaded
    return {
        "traceId": loaded.get("taskId") or path.stem,
        "source": "assembled-report",
        "task": loaded if loaded.get("tool") == "shipguard prepare" else {},
        "verdict": loaded if loaded.get("tool") == "shipguard verify" else {},
        "labels": {},
    }


def dimension_result(
    dimension_id: str,
    label: str,
    score: int,
    evidence: str,
    *,
    missing: list[str] | None = None,
    recommendation: str = "",
) -> dict[str, Any]:
    status = "pass" if score >= 90 else "review" if score >= 70 else "blocked"
    return {
        "id": dimension_id,
        "label": label,
        "score": score,
        "status": status,
        "evidence": evidence,
        "missing": missing or [],
        "recommendation": recommendation,
    }


def score_trace(trace: dict[str, Any], path: Path, *, root: Path, shareable: bool, check_expectations: bool = True) -> dict[str, Any]:
    task = trace.get("task") if isinstance(trace.get("task"), dict) else {}
    verdict = trace.get("verdict") if isinstance(trace.get("verdict"), dict) else {}
    labels = trace.get("labels") if isinstance(trace.get("labels"), dict) else {}
    trace_id = str(trace.get("traceId") or task.get("taskId") or verdict.get("taskId") or path.stem)
    expected_owner = [str(item) for item in labels.get("expectedOwnerPatterns") or []]
    expected_forbidden = [str(item) for item in labels.get("expectedForbiddenPatterns") or []]
    required_proof = [str(item) for item in labels.get("requiredProofScopes") or []]
    unsupported_claims = [str(item) for item in labels.get("unsupportedClaims") or []]
    next_action_terms = [str(item) for item in labels.get("expectedNextActionContains") or []]
    private_terms = [str(item) for item in labels.get("forbiddenPrivateTerms") or []] or [
        "/Users/",
        "/private/tmp/",
        "Ringly",
        "Ilmify",
    ]

    authorized_values = [str(item) for item in task.get("authorizedFiles") or []]
    authorized_values.extend(str(item.get("pattern")) for item in task.get("authorizedScope") or [] if isinstance(item, dict))
    owner_matches = matching_items(authorized_values, expected_owner)
    owner_score = 100 if expected_owner and len(owner_matches) == len(expected_owner) else 75 if authorized_values else 0

    forbidden_values = [str(item) for item in task.get("protectedBoundaries") or []]
    forbidden_values.extend(str(item) for item in (verdict.get("scopeChecks") or {}).get("protectedBoundaries") or [])
    forbidden_matches = matching_items(forbidden_values, expected_forbidden)
    scope_boundary = task.get("scopeBoundary") if isinstance(task.get("scopeBoundary"), dict) else {}
    scope_score = 100 if forbidden_matches and scope_boundary.get("shipguardOnly") is True else 80 if forbidden_values else 30

    proof_text = "\n".join(flatten_strings(task.get("domainRiskPack")) + flatten_strings(verdict.get("validationCoverage")) + flatten_strings(verdict.get("notificationPermissionWorkflow")))
    proof_matches = [item for item in required_proof if item.lower() in proof_text.lower()]
    proof_score = 100 if required_proof and len(proof_matches) == len(required_proof) else 70 if proof_matches else 25

    claim_text = "\n".join(flatten_strings(verdict.get("claimChecks")) + flatten_strings(verdict.get("agentClaims")) + flatten_strings(task.get("agentClaims")))
    rejected_claims = verdict.get("claimChecks", {}).get("rejectedClaims") if isinstance(verdict.get("claimChecks"), dict) else []
    claim_matches = [claim for claim in unsupported_claims if contains_text(rejected_claims, claim)]
    claim_score = 100 if unsupported_claims and claim_matches else 80 if not unsupported_claims and verdict.get("claimChecks") else 45

    next_action = verdict.get("nextAction") if isinstance(verdict.get("nextAction"), dict) else task.get("nextAction") if isinstance(task.get("nextAction"), dict) else {}
    next_missing = [
        field
        for field in ("owner", "command", "expectedArtifact", "successCondition", "failureMeaning")
        if not str(next_action.get(field) or "").strip()
    ]
    missing_terms = [term for term in next_action_terms if not contains_text(next_action, term)]
    next_score = 100 if not next_missing and not missing_terms else 70 if not next_missing else 25

    redaction_payload = json.loads(json.dumps(trace))
    if isinstance(redaction_payload.get("labels"), dict):
        redaction_payload["labels"].pop("forbiddenPrivateTerms", None)
    serialized = json.dumps(redaction_payload, sort_keys=True)
    leaked_terms = [term for term in private_terms if term and term in serialized]
    regex_leak = bool(PRIVATE_TOKEN_RE.search(serialized))
    redaction_score = 100 if not leaked_terms and not regex_leak else 0

    expected_false_positive_max = int(labels.get("expectedFalsePositiveMax", 0) or 0)
    false_positive_markers = trace.get("falsePositiveFindings") or labels.get("knownFalsePositiveFindingIds") or []
    false_positive_count = len(false_positive_markers) if isinstance(false_positive_markers, list) else 0
    false_positive_score = 100 if false_positive_count <= expected_false_positive_max else 55

    events = trace.get("events") if isinstance(trace.get("events"), list) else []
    max_events = int(labels.get("firstUsefulVerdictMaxEvents", 3) or 3)
    useful_index = None
    for index, event in enumerate(events, start=1):
        if isinstance(event, dict) and (event.get("usefulVerdict") is True or event.get("type") in {"verdict", "next-action"}):
            useful_index = index
            break
    if useful_index is None and next_action:
        useful_index = 1
    first_useful_score = 100 if useful_index and useful_index <= max_events else 60 if useful_index else 20

    dimensions = [
        dimension_result(
            "ownerDetection",
            "Owner Detection",
            owner_score,
            f"{len(owner_matches)}/{len(expected_owner)} expected owner pattern(s) matched",
            missing=[item for item in expected_owner if item not in owner_matches],
            recommendation="Keep task traces explicit about owner files before Codex edits.",
        ),
        dimension_result(
            "scopePolicy",
            "Acceptable And Forbidden Scope",
            scope_score,
            f"{len(forbidden_matches)}/{len(expected_forbidden)} expected forbidden pattern(s) matched; shipguardOnly={scope_boundary.get('shipguardOnly')!r}",
            missing=[item for item in expected_forbidden if item not in forbidden_matches],
            recommendation="Declare authorized, review-only, and forbidden scope before verdicts are trusted.",
        ),
        dimension_result(
            "requiredProofCoverage",
            "Required Proof Coverage",
            proof_score,
            f"{len(proof_matches)}/{len(required_proof)} required proof scope(s) matched",
            missing=[item for item in required_proof if item not in proof_matches],
            recommendation="Name the exact proof lanes needed before claims can pass.",
        ),
        dimension_result(
            "claimChecking",
            "Claim Checking",
            claim_score,
            f"{len(claim_matches)}/{len(unsupported_claims)} unsupported claim phrase(s) checked",
            missing=[item for item in unsupported_claims if item not in claim_matches],
            recommendation="Reject or downgrade unsupported completion and release claims.",
        ),
        dimension_result(
            "redaction",
            "Redaction",
            redaction_score,
            "no private terms detected" if redaction_score == 100 else "private term or token-like value detected",
            missing=leaked_terms + (["token-like-pattern"] if regex_leak else []),
            recommendation="Keep private app names, local paths, screenshots, and tokens out of public pilot traces.",
        ),
        dimension_result(
            "nextActionCompleteness",
            "Exact Next Action",
            next_score,
            "next action is complete" if next_score == 100 else "next action missing required fields or expected terms",
            missing=next_missing + missing_terms,
            recommendation="Each review or block must name owner, command/manual proof, artifact, success condition, and failure meaning.",
        ),
        dimension_result(
            "falsePositiveRate",
            "False-Positive Rate",
            false_positive_score,
            f"{false_positive_count} known false positive(s), max {expected_false_positive_max}",
            missing=["false-positive-count-above-label"] if false_positive_score < 100 else [],
            recommendation="Track false positives separately from true verdict defects before tuning rules.",
        ),
        dimension_result(
            "firstUsefulVerdictTime",
            "First Useful Verdict Time",
            first_useful_score,
            f"first useful verdict at event {useful_index or 'missing'}, max {max_events}",
            missing=["first-useful-verdict-missing-or-late"] if first_useful_score < 100 else [],
            recommendation="A pilot trace should reach one useful next action quickly enough to help a solo developer.",
        ),
    ]
    score = round(sum(item["score"] for item in dimensions) / len(dimensions))
    status = "pass" if score >= 90 else "review" if score >= 70 else "blocked"
    findings = [
        {
            "severity": "high" if item["status"] == "blocked" else "review",
            "ruleId": f"pilot-{item['id']}",
            "dimension": item["id"],
            "evidence": item["evidence"],
            "recommendation": item["recommendation"],
            "missing": item["missing"],
        }
        for item in dimensions
        if item["status"] != "pass"
    ]
    expected_status = labels.get("expectedBenchStatus")
    expected_min_score = labels.get("expectedMinScore")
    expected_findings = [str(item) for item in labels.get("expectedFindingRuleIds") or []]
    expectation_checks = []
    if check_expectations and expected_status:
        expectation_checks.append(
            {
                "id": "expectedBenchStatus",
                "passed": status == expected_status,
                "evidence": f"status={status}, expected={expected_status}",
            }
        )
    if check_expectations and expected_min_score is not None:
        expectation_checks.append(
            {
                "id": "expectedMinScore",
                "passed": score >= int(expected_min_score),
                "evidence": f"score={score}, expected>={expected_min_score}",
            }
        )
    finding_ids = {item["ruleId"] for item in findings}
    for rule_id in expected_findings if check_expectations else []:
        expectation_checks.append(
            {
                "id": f"expectedFinding:{rule_id}",
                "passed": rule_id in finding_ids,
                "evidence": f"{rule_id} {'present' if rule_id in finding_ids else 'missing'}",
            }
        )
    return {
        "traceId": trace_id,
        "path": path_label(path, root=root, shareable=shareable),
        "source": str(trace.get("source") or "unknown"),
        "score": score,
        "status": status,
        "dimensions": dimensions,
        "findings": findings,
        "expectationChecks": expectation_checks,
        "expectationsPassed": all(item["passed"] for item in expectation_checks) if expectation_checks else True,
        "nextAction": next_action,
    }


def score_baseline_trace(trace: dict[str, Any], path: Path, *, root: Path, shareable: bool) -> dict[str, Any] | None:
    baseline = trace.get("baselineVerdict")
    if not isinstance(baseline, dict):
        return None
    baseline_trace = {
        **trace,
        "traceId": f"{trace.get('traceId') or path.stem}::baseline",
        "verdict": baseline,
        "events": trace.get("baselineEvents") if isinstance(trace.get("baselineEvents"), list) else [],
    }
    return score_trace(baseline_trace, path, root=root, shareable=shareable, check_expectations=False)


def dimension_score(trace: dict[str, Any], dimension_id: str) -> int:
    for item in trace.get("dimensions") or []:
        if item.get("id") == dimension_id:
            return int(item.get("score") or 0)
    return 0


def comparative_benchmark(
    scored_traces: list[dict[str, Any]],
    baseline_traces: list[dict[str, Any] | None],
    *,
    min_lift: int,
    required: bool,
) -> dict[str, Any] | None:
    pairs = [
        {"shipguard": scored, "baseline": baseline}
        for scored, baseline in zip(scored_traces, baseline_traces)
        if isinstance(baseline, dict)
    ]
    if not required and not pairs:
        return None
    comparisons: list[dict[str, Any]] = []
    for pair in pairs:
        shipguard_score = int(pair["shipguard"].get("score") or 0)
        baseline_score = int(pair["baseline"].get("score") or 0)
        lift = shipguard_score - baseline_score
        comparisons.append(
            {
                "traceId": pair["shipguard"].get("traceId"),
                "shipguardScore": shipguard_score,
                "baselineScore": baseline_score,
                "scoreLift": lift,
                "winner": "shipguard" if lift > 0 else "baseline" if lift < 0 else "tie",
                "dimensionLift": {
                    dimension_id: dimension_score(pair["shipguard"], dimension_id) - dimension_score(pair["baseline"], dimension_id)
                    for dimension_id in (
                        "ownerDetection",
                        "scopePolicy",
                        "requiredProofCoverage",
                        "claimChecking",
                        "redaction",
                        "nextActionCompleteness",
                        "falsePositiveRate",
                        "firstUsefulVerdictTime",
                    )
                },
                "baselineMissingDimensions": [
                    item.get("id")
                    for item in pair["baseline"].get("dimensions") or []
                    if item.get("status") != "pass"
                ],
                "shipguardMissingDimensions": [
                    item.get("id")
                    for item in pair["shipguard"].get("dimensions") or []
                    if item.get("status") != "pass"
                ],
            }
        )
    shipguard_average = round(sum(item["shipguardScore"] for item in comparisons) / len(comparisons)) if comparisons else 0
    baseline_average = round(sum(item["baselineScore"] for item in comparisons) / len(comparisons)) if comparisons else 0
    lift = shipguard_average - baseline_average
    win_count = sum(1 for item in comparisons if item["winner"] == "shipguard")
    win_rate = round((win_count / len(comparisons)) * 100) if comparisons else 0
    gates = [
        {
            "id": "hasPublicSafeBaselinePairs",
            "passed": bool(comparisons),
            "evidence": f"{len(comparisons)} comparative pair(s)",
        },
        {
            "id": "minimumScoreLift",
            "passed": lift >= min_lift,
            "evidence": f"score lift {lift}, required >= {min_lift}",
        },
        {
            "id": "shipguardWinsEveryTrace",
            "passed": bool(comparisons) and win_count == len(comparisons),
            "evidence": f"{win_count}/{len(comparisons)} trace(s) won",
        },
        {
            "id": "noShipGuardComparativeRegressions",
            "passed": all(not item["shipguardMissingDimensions"] for item in comparisons),
            "evidence": "ShipGuard verdict dimensions all pass" if comparisons else "no comparative pairs",
        },
    ]
    status = "pass" if all(item["passed"] for item in gates) else "blocked" if required else "review"
    return {
        "benchmarkVersion": BENCHMARK_VERSION,
        "status": status,
        "required": required,
        "pairCount": len(comparisons),
        "shipguardAverageScore": shipguard_average,
        "baselineAverageScore": baseline_average,
        "scoreLift": lift,
        "shipguardWinRate": win_rate,
        "minimumRequiredLift": min_lift,
        "qualityGates": gates,
        "comparisons": comparisons,
        "scopeBoundary": {
            "shipguardOnly": True,
            "targetAppsReadOnly": True,
            "privateAppsUsed": False,
            "purpose": "Compare ShipGuard verdict usefulness against public-safe baseline agent output; do not grade or modify target apps.",
        },
    }


def build_report(args: argparse.Namespace, *, root: Path) -> dict[str, Any]:
    files = trace_files(args.trace or [], root=root)
    loaded_traces = [trace_from_loaded(read_json(path), path) for path in files]
    traces = [score_trace(trace, path, root=root, shareable=args.shareable) for trace, path in zip(loaded_traces, files)]
    baseline_traces = [score_baseline_trace(trace, path, root=root, shareable=args.shareable) for trace, path in zip(loaded_traces, files)]
    benchmark = comparative_benchmark(
        traces,
        baseline_traces,
        min_lift=int(args.min_lift),
        required=bool(args.benchmark_v2),
    )
    expectation_failures = [
        {"traceId": trace["traceId"], "checks": [item for item in trace["expectationChecks"] if not item["passed"]]}
        for trace in traces
        if not trace["expectationsPassed"]
    ]
    average = round(sum(trace["score"] for trace in traces) / len(traces)) if traces else 0
    blocked = any(trace["status"] == "blocked" for trace in traces)
    review = any(trace["status"] == "review" for trace in traces)
    status = "blocked" if expectation_failures or blocked else "review" if review else "pass"
    if benchmark and benchmark["status"] == "blocked":
        status = "blocked"
    elif benchmark and benchmark["status"] == "review" and status == "pass":
        status = "review"
    findings = []
    for trace in traces:
        for finding in trace["findings"]:
            findings.append({**finding, "traceId": trace["traceId"], "tracePath": trace["path"]})
    priority = findings[0] if findings else None
    fixture_candidates = [
        {
            "candidateId": f"external-pilot-{trace['traceId']}",
            "fixtureType": "external-pilot-verdict-trace",
            "sourceTrace": trace["path"],
            "score": trace["score"],
            "status": trace["status"],
            "recommendedPublicFixturePath": "fixtures/external-pilot-verdict-bench/<trace-id>/trace.json",
        }
        for trace in traces
        if trace["status"] != "pass"
    ]
    report = {
        "schemaVersion": SCHEMA_VERSION,
        "tool": TOOL,
        "surface": SURFACE,
        "intent": "shipguard-product-qa",
        "status": status,
        "generatedAt": utc_now(),
        "traceCount": len(traces),
        "averageVerdictScore": average,
        "scopeBoundary": {
            "shipguardOnly": True,
            "targetAppsReadOnly": True,
            "purpose": "Score ShipGuard verdict usefulness from public-safe read-only traces; do not grade or modify target apps.",
            "privateTracePolicy": "Private app traces may be scored locally only after shareable redaction; repeated weaknesses must become public synthetic fixtures.",
        },
        "metrics": [
            "ownerDetection",
            "scopePolicy",
            "requiredProofCoverage",
            "claimChecking",
            "redaction",
            "nextActionCompleteness",
            "falsePositiveRate",
            "firstUsefulVerdictTime",
        ],
        "traces": traces,
        "findings": findings,
        "fixtureCandidates": fixture_candidates,
        "expectationFailures": expectation_failures,
        "priorityAction": {
            "kind": "fix-pilot-trace-rule",
            "summary": f"Fix {priority['ruleId']} in {priority['traceId']}",
            "recommendation": priority["recommendation"],
            "traceId": priority["traceId"],
            "ruleId": priority["ruleId"],
        }
        if priority
        else {
            "kind": "expand-pilot-coverage",
            "summary": "Add the next public-safe pilot trace from a real read-only observation.",
            "recommendation": "Convert repeated private-app weaknesses into synthetic trace fixtures before tuning ShipGuard behavior.",
        },
        "reportQualityQuestions": [
            "Did the pilot bench score owner detection, scope, proof, claims, redaction, next action, false positives, and first useful verdict time?",
            "If benchmark v2 is enabled, did ShipGuard beat the baseline agent verdict by a meaningful public-safe score lift?",
            "Did every private-app observation become a public-safe synthetic trace before changing ShipGuard rules?",
            "Can the bench tell whether a weak verdict is a ShipGuard defect without telling the developer to edit the target app?",
        ],
    }
    if benchmark:
        report["comparativeBenchmark"] = benchmark
    return report


def render_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# ShipGuard PilotBench",
        "",
        f"- Status: `{report['status']}`",
        f"- Traces: {report['traceCount']}",
        f"- Average verdict score: {report['averageVerdictScore']}/100",
        "- Purpose: score ShipGuard verdict usefulness, not target-app quality.",
        "",
        "## Metrics",
        "",
    ]
    for metric in report["metrics"]:
        lines.append(f"- `{metric}`")
    lines.extend(["", "## Traces", "", "| Score | Status | Trace | Source | Missing Dimensions |", "| ---: | --- | --- | --- | --- |"])
    for trace in report["traces"]:
        missing = ", ".join(item["id"] for item in trace["dimensions"] if item["status"] != "pass") or "-"
        lines.append(f"| {trace['score']} | {trace['status']} | `{trace['traceId']}` | {trace['source']} | {missing} |")
    lines.extend(["", "## Findings", ""])
    if report["findings"]:
        lines.extend(["| Severity | Rule | Trace | Evidence | Recommendation |", "| --- | --- | --- | --- | --- |"])
        for item in report["findings"]:
            lines.append(
                f"| {item['severity']} | `{item['ruleId']}` | `{item['traceId']}` | {item['evidence']} | {item['recommendation']} |"
            )
    else:
        lines.append("No pilot verdict findings.")
    lines.extend(["", "## Priority Action", ""])
    priority = report["priorityAction"]
    lines.append(f"- Kind: `{priority['kind']}`")
    lines.append(f"- Summary: {priority['summary']}")
    lines.append(f"- Recommendation: {priority['recommendation']}")
    lines.extend(["", "## Fixture Candidates", ""])
    if report["fixtureCandidates"]:
        for item in report["fixtureCandidates"]:
            lines.append(f"- `{item['candidateId']}` -> `{item['recommendedPublicFixturePath']}`")
    else:
        lines.append("No new fixture candidates.")
    benchmark = report.get("comparativeBenchmark") if isinstance(report.get("comparativeBenchmark"), dict) else None
    if benchmark:
        lines.extend(["", "## External Benchmark v2", ""])
        lines.append(f"- Status: `{benchmark['status']}`")
        lines.append(f"- Pairs: {benchmark['pairCount']}")
        lines.append(f"- ShipGuard average: {benchmark['shipguardAverageScore']}/100")
        lines.append(f"- Baseline average: {benchmark['baselineAverageScore']}/100")
        lines.append(f"- Score lift: {benchmark['scoreLift']} points")
        lines.append(f"- ShipGuard win rate: {benchmark['shipguardWinRate']}%")
        lines.extend(["", "| Trace | ShipGuard | Baseline | Lift | Winner | Baseline Missing |", "| --- | ---: | ---: | ---: | --- | --- |"])
        for item in benchmark["comparisons"]:
            missing = ", ".join(item["baselineMissingDimensions"]) or "-"
            lines.append(
                f"| `{item['traceId']}` | {item['shipguardScore']} | {item['baselineScore']} | {item['scoreLift']} | {item['winner']} | {missing} |"
            )
    lines.extend(["", "## Scope Boundary", ""])
    boundary = report["scopeBoundary"]
    lines.append(f"- ShipGuard only: `{str(boundary['shipguardOnly']).lower()}`")
    lines.append(f"- Target apps read-only: `{str(boundary['targetAppsReadOnly']).lower()}`")
    lines.append(f"- Private trace policy: {boundary['privateTracePolicy']}")
    lines.extend(["", "## Report Quality Questions", ""])
    for question in report["reportQualityQuestions"]:
        lines.append(f"- {question}")
    return "\n".join(lines) + "\n"


def write_outputs(report: dict[str, Any], out_dir: Path) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    json_path = out_dir / "pilot-bench.json"
    md_path = out_dir / "pilot-bench.md"
    write_json(json_path, report)
    md_path.write_text(render_markdown(report), encoding="utf-8")
    print(f"wrote: {json_path}")
    print(f"wrote: {md_path}")
    print(f"status: {report['status']}")


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Score ShipGuard PilotBench task traces.")
    parser.add_argument("--trace", action="append", help="Trace JSON file or directory containing trace.json files. Defaults to public fixtures.")
    parser.add_argument("--out", help="Output directory for pilot-bench.json and pilot-bench.md")
    parser.add_argument("--shareable", action="store_true", help="Omit local input paths from output.")
    parser.add_argument("--benchmark-v2", action="store_true", help="Require baselineVerdict pairs and emit External Benchmark v2 comparative scoring.")
    parser.add_argument("--min-lift", type=int, default=15, help="Minimum average ShipGuard score lift over baseline for --benchmark-v2.")
    parser.add_argument("--json", action="store_true", help="Print JSON to stdout.")
    parser.add_argument("--markdown", action="store_true", help="Print Markdown to stdout.")
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    root = Path.cwd()
    report = build_report(args, root=root)
    if args.out:
        write_outputs(report, Path(args.out))
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    if args.markdown:
        print(render_markdown(report), end="")
    return 2 if report["status"] == "blocked" else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
