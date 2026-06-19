#!/usr/bin/env python3
"""Shared ShipGuard evidence receipt normalization."""

from __future__ import annotations

import datetime as dt
import hashlib
import json
from pathlib import Path
from typing import Any


SCHEMA_VERSION = "2.0"
CURRENT_SCHEMA_VALUES = {"2", "2.0", "v2", "shipguard.evidence.receipt.v2"}
VALIDATION_RECEIPT_TYPES = {"validation", "ci"}
STRUCTURED_RECEIPT_TYPES = {"validation", "runtime", "manual", "simulator", "device", "ci", "release"}


def parse_timestamp(value: Any) -> dt.datetime | None:
    if not value:
        return None
    try:
        text = str(value).replace("Z", "+00:00")
        parsed = dt.datetime.fromisoformat(text)
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=dt.timezone.utc)
        return parsed
    except ValueError:
        return None


def _sha256(content: bytes) -> str | None:
    return hashlib.sha256(content).hexdigest() if content else None


def _read(path: Path) -> bytes:
    return path.read_bytes() if path.is_file() else b""


def _base_entry(path: Path, content: bytes) -> dict[str, Any]:
    return {
        "path": path.as_posix(),
        "present": path.is_file(),
        "bytes": len(content),
        "sha256": _sha256(content),
        "schemaVersion": SCHEMA_VERSION,
    }


def _schema_value(value: Any) -> str | None:
    if value is None:
        return None
    return str(value).strip().lower()


def _receipt_type(parsed: dict[str, Any], *, is_current: bool) -> str:
    raw = str(parsed.get("receiptType") or parsed.get("proofKind") or "").strip().lower()
    if raw:
        return raw
    if is_current:
        return "validation" if parsed.get("command") else "manual"
    return "validation"


def _artifact_status(receipt_path: Path, parsed: dict[str, Any]) -> dict[str, Any]:
    artifact = parsed.get("artifact") if isinstance(parsed.get("artifact"), dict) else {}
    raw_path = str(artifact.get("path") or "").strip()
    artifact_path = Path(raw_path) if raw_path else None
    if artifact_path and not artifact_path.is_absolute():
        artifact_path = receipt_path.parent / artifact_path
    artifact_content = _read(artifact_path) if artifact_path else b""
    actual_sha = _sha256(artifact_content)
    expected_sha = artifact.get("sha256")
    expected_bytes = artifact.get("bytes")
    digest_matches = bool(actual_sha) and (
        expected_sha in (None, "") or str(expected_sha) == str(actual_sha)
    )
    try:
        bytes_match = expected_bytes in (None, "") or int(expected_bytes) == len(artifact_content)
    except (TypeError, ValueError):
        bytes_match = False
    return {
        "path": artifact.get("path"),
        "present": bool(artifact_path and artifact_path.is_file()),
        "bytes": len(artifact_content),
        "expectedBytes": expected_bytes,
        "bytesMatch": bool(bytes_match),
        "sha256": actual_sha,
        "expectedSha256": expected_sha,
        "digestMatches": bool(digest_matches),
    }


def _invalid_reasons(
    *,
    receipt_type: str,
    command: Any,
    exit_code: Any,
    status: str,
    artifact: dict[str, Any],
    is_validation_compatible: bool,
    unsupported_schema: bool,
    schema_raw: Any,
) -> list[str]:
    reasons: list[str] = []
    if unsupported_schema:
        reasons.append(f"unsupported schemaVersion {schema_raw}")
    if receipt_type not in STRUCTURED_RECEIPT_TYPES:
        reasons.append(f"unsupported receiptType {receipt_type}")
    if not is_validation_compatible:
        reasons.append(f"receiptType {receipt_type} is not compatible with validation command coverage")
    if is_validation_compatible:
        if not command:
            reasons.append("validation-compatible receipt is missing command")
        if exit_code != 0:
            reasons.append("exitCode is not 0")
        if status != "pass":
            reasons.append("status is not pass")
        if not artifact.get("present"):
            reasons.append("artifact is missing")
        elif not artifact.get("digestMatches") or not artifact.get("bytesMatch"):
            reasons.append("artifact digest or byte count does not match")
    return reasons


def _normalise_structured_receipt(path: Path, content: bytes, parsed: dict[str, Any]) -> dict[str, Any]:
    schema_raw = parsed.get("schemaVersion", parsed.get("schema_version"))
    schema_value = _schema_value(schema_raw)
    is_current = schema_value in CURRENT_SCHEMA_VALUES
    legacy = schema_value is None
    unsupported_schema = bool(schema_value and not is_current)
    receipt_type = _receipt_type(parsed, is_current=is_current)
    is_validation_compatible = receipt_type in VALIDATION_RECEIPT_TYPES
    artifact = _artifact_status(path, parsed)
    status = str(parsed.get("status") or "").lower()
    exit_code = parsed.get("exitCode")
    reasons = _invalid_reasons(
        receipt_type=receipt_type,
        command=parsed.get("command"),
        exit_code=exit_code,
        status=status,
        artifact=artifact,
        is_validation_compatible=is_validation_compatible,
        unsupported_schema=unsupported_schema,
        schema_raw=schema_raw,
    )
    compatibility_status = "current" if is_current else "legacy-compatible" if legacy else "unsupported-schema"
    if not is_validation_compatible or receipt_type not in STRUCTURED_RECEIPT_TYPES:
        compatibility_status = "downgraded"
    usable_for_validation = is_validation_compatible and not reasons
    receipt_status = "pass" if usable_for_validation else "invalid" if is_validation_compatible else "downgraded"
    public_reason = None if usable_for_validation else "; ".join(reasons)
    return {
        **_base_entry(path, content),
        "kind": "structured-validation" if is_validation_compatible else "structured-proof",
        "receiptId": parsed.get("receiptId") or path.stem,
        "receiptType": receipt_type,
        "validationId": parsed.get("validationId") or parsed.get("requirementId"),
        "requirementId": parsed.get("requirementId") or parsed.get("validationId"),
        "command": parsed.get("command"),
        "exitCode": exit_code,
        "status": parsed.get("status"),
        "receiptStatus": receipt_status,
        "usableForValidation": usable_for_validation,
        "startedAt": parsed.get("startedAt"),
        "completedAt": parsed.get("completedAt"),
        "repositoryCommit": parsed.get("repositoryCommit"),
        "environment": parsed.get("environment"),
        "proofType": parsed.get("proofType"),
        "scope": parsed.get("scope") if isinstance(parsed.get("scope"), list) else [],
        "proofScope": parsed.get("proofScope") if isinstance(parsed.get("proofScope"), list) else [],
        "coverage": parsed.get("coverage") if isinstance(parsed.get("coverage"), list) else [],
        "artifact": artifact,
        "compatibility": {
            "schemaVersion": SCHEMA_VERSION,
            "sourceSchemaVersion": schema_raw if schema_raw is not None else "legacy",
            "status": compatibility_status,
            "receiptType": receipt_type,
            "validationCompatible": is_validation_compatible,
            "warnings": reasons,
        },
        "reason": public_reason,
    }


def evidence_entries(paths: list[str]) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    entries: list[dict[str, Any]] = []
    warnings: list[str] = []
    for value in paths:
        path = Path(value)
        content = _read(path)
        if not path.is_file():
            entries.append(
                {
                    **_base_entry(path, content),
                    "kind": "missing",
                    "status": "missing",
                    "usableForValidation": False,
                    "receiptType": None,
                }
            )
            continue
        try:
            parsed = json.loads(content.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError):
            entries.append(
                {
                    **_base_entry(path, content),
                    "kind": "artifact-only",
                    "status": "unstructured",
                    "receiptType": None,
                    "usableForValidation": False,
                    "_textPreview": content[:4000].decode("utf-8", errors="ignore"),
                    "reason": "Plain evidence artifacts are review context only; validation coverage requires a structured JSON receipt.",
                }
            )
            continue
        if not isinstance(parsed, dict):
            entries.append(
                {
                    **_base_entry(path, content),
                    "kind": "artifact-only",
                    "status": "unstructured",
                    "receiptType": None,
                    "usableForValidation": False,
                    "reason": "JSON evidence must be an object to be interpreted as a ShipGuard evidence receipt.",
                }
            )
            continue
        schema_value = _schema_value(parsed.get("schemaVersion", parsed.get("schema_version")))
        is_current = schema_value in CURRENT_SCHEMA_VALUES
        if not parsed.get("command") and not is_current:
            entries.append(
                {
                    **_base_entry(path, content),
                    "kind": "artifact-only",
                    "status": "unstructured",
                    "receiptType": None,
                    "usableForValidation": False,
                    "reason": "JSON evidence without a command is review context only; validation coverage requires a structured command receipt.",
                }
            )
            continue
        entry = _normalise_structured_receipt(path, content, parsed)
        entries.append(entry)
        for warning in (entry.get("compatibility") or {}).get("warnings") or []:
            warnings.append(f"{entry.get('receiptId')}: {warning}")
    return entries, receipt_schema_summary(entries, compatibility_warnings=warnings)


def receipt_schema_summary(
    evidence: list[dict[str, Any]],
    *,
    compatibility_warnings: list[str] | None = None,
    invalid_receipts: list[dict[str, Any]] | None = None,
    task_generated_at: str | None = None,
) -> dict[str, Any]:
    present = [item for item in evidence if item.get("present")]
    current_count = sum(1 for item in present if (item.get("compatibility") or {}).get("status") == "current")
    legacy_count = sum(1 for item in present if (item.get("compatibility") or {}).get("status") == "legacy-compatible")
    downgraded_count = sum(1 for item in present if (item.get("compatibility") or {}).get("status") == "downgraded")
    unsupported_count = sum(1 for item in present if (item.get("compatibility") or {}).get("status") == "unsupported-schema")
    invalid_count = sum(1 for item in present if item.get("receiptStatus") == "invalid")
    task_time = parse_timestamp(task_generated_at)
    stale_count = 0
    if task_time:
        for item in present:
            completed = parse_timestamp(item.get("completedAt"))
            if completed and completed < task_time:
                stale_count += 1
    warnings = list(compatibility_warnings or [])
    for item in invalid_receipts or []:
        reason = str(item.get("reason") or "").strip()
        if reason:
            warnings.append(reason)
    return {
        "schemaVersion": SCHEMA_VERSION,
        "mode": "shared-evidence-receipts",
        "receiptCount": len(evidence),
        "presentCount": len(present),
        "v2Count": current_count,
        "legacyCount": legacy_count,
        "artifactOnlyCount": sum(1 for item in present if item.get("kind") == "artifact-only"),
        "missingCount": sum(1 for item in evidence if not item.get("present")),
        "invalidCount": invalid_count,
        "staleCount": stale_count,
        "downgradedCount": downgraded_count,
        "unsupportedSchemaCount": unsupported_count,
        "structuredProofCount": sum(1 for item in present if item.get("kind") == "structured-proof"),
        "structuredValidationCount": sum(1 for item in present if item.get("kind") == "structured-validation"),
        "compatibilityWarnings": sorted(set(warnings)),
    }
