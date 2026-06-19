#!/usr/bin/env python3
"""Shared concise result UX helpers for ShipGuard reports."""

from __future__ import annotations

from typing import Any


def normalize_result_status(status: object) -> str:
    text = str(status or "").strip().lower()
    if text in {"pass", "passed", "ok", "success"}:
        return "pass"
    if text in {"blocked", "block", "fail", "failed", "failure", "error"}:
        return "blocked"
    return "review"


def result_label(status: object) -> str:
    return normalize_result_status(status).upper()


def build_result_ux(
    *,
    status: object,
    summary: str,
    proof_source: str,
    why_it_matters: str,
    next_command: str,
    next_action_summary: str | None = None,
) -> dict[str, Any]:
    normalized = normalize_result_status(status)
    clean_summary = " ".join(str(summary or "").split()) or "Report completed."
    clean_proof = " ".join(str(proof_source or "").split()) or "report evidence"
    clean_why = " ".join(str(why_it_matters or "").split()) or "This keeps the report actionable without hiding proof."
    clean_next = " ".join(str(next_command or "").split()) or "Rerun the same ShipGuard command after the next change."
    clean_action = " ".join(str(next_action_summary or clean_next).split())
    return {
        "status": normalized,
        "sourceStatus": str(status or "").strip() or normalized,
        "verdict": f"{result_label(normalized)}: {clean_summary}",
        "proofSource": clean_proof,
        "whyItMatters": clean_why,
        "nextCommand": clean_next,
        "nextActionSummary": clean_action,
    }


def render_result_markdown(result_ux: dict[str, Any]) -> list[str]:
    return [
        "## Result",
        "",
        f"- Verdict: {result_ux.get('verdict') or 'REVIEW: Result unavailable.'}",
        f"- Proof source: {result_ux.get('proofSource') or 'report evidence'}",
        f"- Why it matters: {result_ux.get('whyItMatters') or 'This keeps the report actionable.'}",
        f"- Next command: `{result_ux.get('nextCommand') or 'Rerun the same ShipGuard command after the next change.'}`",
        f"- Next action: {result_ux.get('nextActionSummary') or result_ux.get('nextCommand') or 'Review the report evidence.'}",
        "",
    ]
