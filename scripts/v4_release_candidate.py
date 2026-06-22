#!/usr/bin/env python3
"""Generate the ShipGuard v4 release-candidate readiness report."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shlex
import shutil
import subprocess
import sys
import tarfile
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:
    from shipguard_result import build_result_ux, render_result_markdown
except ModuleNotFoundError:  # pragma: no cover - direct script fallback
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from shipguard_result import build_result_ux, render_result_markdown

try:
    from release_package_hygiene import scan_tarball as scan_release_package_tarball
except ModuleNotFoundError:  # pragma: no cover - direct script fallback
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from release_package_hygiene import scan_tarball as scan_release_package_tarball


SURFACE = "ShipGuard V4 Release Candidate Readiness"
TOOL = "shipguard v4 release-candidate"
SCHEMA_VERSION = 1
PRIVATE_OR_SECRET_RE = re.compile(
    r"(?i)(/Users/|/private/tmp|/var/folders|\bRingly\b|\bIlmify\b|\bInweFi\b|gh[pousr]_[A-Za-z0-9_]{20,}|sk-[A-Za-z0-9_-]{20,}|Bearer\s+[A-Za-z0-9._~+/=-]{12,})"
)


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return ""


def contains_all(text: str, phrases: list[str]) -> bool:
    lower = text.lower()
    return all(phrase.lower() in lower for phrase in phrases)


def scrub_value(value: Any, replacements: dict[str, str]) -> Any:
    if isinstance(value, dict):
        return {key: scrub_value(child, replacements) for key, child in value.items()}
    if isinstance(value, list):
        return [scrub_value(child, replacements) for child in value]
    if isinstance(value, str):
        result = value
        for source, replacement in sorted(replacements.items(), key=lambda item: len(item[0]), reverse=True):
            result = result.replace(source, replacement)
        return result
    return value


def add_check(
    checks: list[dict[str, Any]],
    check_id: str,
    title: str,
    passed: bool,
    evidence: list[str],
    recommendation: str,
    required: bool = True,
) -> None:
    checks.append(
        {
            "id": check_id,
            "title": title,
            "status": "pass" if passed else "review",
            "required": required,
            "evidence": evidence,
            "recommendation": recommendation,
        }
    )


def load_json(path: Path) -> dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def short_output(value: str, limit: int = 1200) -> str:
    value = value.strip()
    if len(value) <= limit:
        return value
    return value[: limit - 3].rstrip() + "..."


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def normalize_release_tag(version: str) -> str:
    value = version.strip()
    if value.startswith("refs/tags/"):
        value = value.removeprefix("refs/tags/")
    return value if value.startswith("v") else f"v{value}"


def join_api_url(api_url: str, path: str) -> str:
    base = api_url.rstrip("/")
    suffix = "/" + path.lstrip("/")
    return base + suffix


def request_json(url: str, headers: dict[str, str], timeout: int = 60) -> dict[str, Any]:
    request = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(request, timeout=timeout) as response:
        body = response.read()
    try:
        payload = json.loads(body.decode("utf-8"))
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"GitHub release response was not JSON: {exc}") from exc
    if not isinstance(payload, dict):
        raise RuntimeError("GitHub release response was not a JSON object")
    return payload


def download_url_to_file(url: str, destination: Path, headers: dict[str, str], timeout: int = 120) -> None:
    request = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(request, timeout=timeout) as response:
        destination.parent.mkdir(parents=True, exist_ok=True)
        with destination.open("wb") as handle:
            shutil.copyfileobj(response, handle)


def safe_asset_name(name: str) -> str:
    candidate = Path(name).name
    if not candidate or candidate in {".", ".."}:
        raise RuntimeError(f"unsafe release asset name: {name!r}")
    return candidate


def is_forbidden_archive_member(name: str) -> bool:
    path = Path(name)
    return (
        "__MACOSX" in path.parts
        or any(part.startswith("._") for part in path.parts)
        or path.name == ".DS_Store"
        or path.name.endswith(".pyc")
        or path.name in {".git", ".cache", "DerivedData", "__pycache__"}
    )


def package_hygiene_command(tarballs: list[Path]) -> str:
    pieces = ["./bin/shipguard", "release-package", "hygiene", "--path", "."]
    for tarball in tarballs:
        pieces.extend(["--tarball", tarball.as_posix()])
    pieces.extend(["--out", "/tmp/shipguard-package-hygiene", "--shareable"])
    return " ".join(shlex.quote(piece) for piece in pieces)


def compact_hygiene_finding(finding: dict[str, Any]) -> dict[str, Any]:
    return {
        "severity": finding.get("severity"),
        "ruleId": finding.get("ruleId"),
        "tarball": finding.get("tarball"),
        "version": finding.get("version"),
        "member": finding.get("member"),
        "evidence": finding.get("evidence"),
        "recommendation": finding.get("recommendation"),
        "proofGuidance": finding.get("proofGuidance"),
    }


def build_package_hygiene_evidence(tarballs: list[Path], root: Path, shareable: bool) -> dict[str, Any]:
    scans = [scan_release_package_tarball(tarball, root, shareable) for tarball in tarballs if tarball.is_file()]
    findings = [finding for scan in scans for finding in scan.get("findings", [])]
    blocked = [finding for finding in findings if finding.get("severity") == "blocked"]
    review = [finding for finding in findings if finding.get("severity") == "review"]
    status = "blocked" if blocked else "review" if review else "pass" if scans else "not-run"
    first_finding = (blocked or review or [None])[0]
    return {
        "status": status,
        "tool": "shipguard release-package hygiene",
        "readOnly": True,
        "tarballsScanned": len(scans),
        "blockedFindingCount": len(blocked),
        "reviewFindingCount": len(review),
        "affectedVersions": sorted({finding["version"] for finding in findings if finding.get("version")}),
        "safeTarballs": [scan["name"] for scan in scans if scan.get("status") == "pass"],
        "firstFinding": compact_hygiene_finding(first_finding) if first_finding else None,
        "tarballSummaries": [
            {
                "name": scan.get("name"),
                "path": scan.get("path"),
                "version": scan.get("version"),
                "status": scan.get("status"),
                "memberCount": scan.get("memberCount"),
                "blockedFindingCount": len([finding for finding in scan.get("findings", []) if finding.get("severity") == "blocked"]),
                "reviewFindingCount": len([finding for finding in scan.get("findings", []) if finding.get("severity") == "review"]),
                "installRiskSummary": scan.get("installRiskSummary"),
            }
            for scan in scans
        ],
        "nextCommand": package_hygiene_command(tarballs),
    }


def attach_blocking_package_hygiene(proof: dict[str, Any], tarballs: list[Path], args: argparse.Namespace) -> None:
    hygiene = build_package_hygiene_evidence(tarballs, Path(args.path).expanduser().resolve(), bool(args.shareable))
    if hygiene.get("status") != "pass":
        proof["packageHygieneEvidence"] = hygiene
        if hygiene.get("nextCommand"):
            proof["nextCommand"] = hygiene["nextCommand"]


def package_hygiene_excerpt(evidence: Any) -> str:
    if not isinstance(evidence, dict):
        return ""
    first = evidence.get("firstFinding")
    if not isinstance(first, dict):
        return ""
    rule = first.get("ruleId") or "package-hygiene"
    tarball = first.get("tarball") or "package tarball"
    member = first.get("member") or "n/a"
    detail = first.get("evidence") or "unsafe archive member"
    blocked_count = evidence.get("blockedFindingCount")
    count_suffix = f"; {blocked_count} blocked finding(s)" if blocked_count is not None else ""
    return f"{rule} in {tarball}: {member} ({detail}){count_suffix}"


def safe_extract_tarball(tarball: Path, destination: Path) -> tuple[bool, str]:
    destination.mkdir(parents=True, exist_ok=True)
    destination_root = destination.resolve()
    try:
        with tarfile.open(tarball, "r:gz") as archive:
            for member in archive.getmembers():
                member_target = (destination_root / member.name).resolve()
                if not member_target.is_relative_to(destination_root):
                    return False, f"unsafe tarball member escapes destination: {member.name}"
                if member.issym() or member.islnk() or member.isdev():
                    return False, f"unsafe tarball member is a link or device: {member.name}"
                if is_forbidden_archive_member(member.name):
                    return False, f"unsafe tarball member is generated metadata/cache: {member.name}"
            archive.extractall(destination_root)
    except (tarfile.TarError, OSError) as exc:
        return False, f"tarball extraction failed: {exc}"
    return True, f"extracted {tarball.name}"


def find_package_root(extract_dir: Path, version: str) -> Path | None:
    expected = extract_dir / f"shipguard-v{version}"
    if (expected / "scripts" / "install.sh").is_file():
        return expected
    for child in (extract_dir.iterdir() if extract_dir.exists() else []):
        if child.is_dir() and (child / "scripts" / "install.sh").is_file():
            return child
    return None


def run_process(
    command: list[str],
    cwd: Path,
    timeout: int,
    env: dict[str, str] | None = None,
) -> dict[str, Any]:
    try:
        completed = subprocess.run(
            command,
            cwd=cwd,
            env=env,
            check=False,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
    except subprocess.TimeoutExpired as exc:
        return {
            "command": " ".join(command),
            "exitCode": "timeout",
            "stdout": short_output(exc.stdout or ""),
            "stderr": short_output(exc.stderr or ""),
        }
    return {
        "command": " ".join(command),
        "exitCode": completed.returncode,
        "stdout": short_output(completed.stdout),
        "stderr": short_output(completed.stderr),
    }


def is_forbidden_install_name(name: str) -> bool:
    return name.startswith("._")


def find_forbidden_install_paths(install_root: Path) -> list[str]:
    forbidden_names = {".git", "dist", ".DS_Store", ".cache", "DerivedData", "__pycache__"}
    forbidden: list[str] = []
    if not install_root.exists():
        return forbidden
    for current_root, dirs, files in os.walk(install_root):
        current = Path(current_root)
        for name in list(dirs):
            if name in forbidden_names or is_forbidden_install_name(name):
                forbidden.append((current / name).as_posix())
        for name in files:
            if name in forbidden_names or is_forbidden_install_name(name) or name.endswith(".pyc"):
                forbidden.append((current / name).as_posix())
    return forbidden


def build_fresh_install_package_proof(args: argparse.Namespace, version: str) -> dict[str, Any]:
    command_template = (
        "./bin/shipguard v4 release-candidate --path . --out /tmp/shipguard-v4-release-candidate "
        "--package-tarball <release-tarball> --shipguard-eval --shareable"
    )
    if not args.package_tarball:
        return {
            "status": "not-provided",
            "provided": False,
            "requiredForStableV4": True,
            "summary": "No release package tarball was supplied; stable v4 proof still needs a fresh install receipt from the package.",
            "nextCommand": command_template,
            "installCommand": "PREFIX=<fresh-prefix> <package>/scripts/install.sh",
            "validateCommand": "<fresh-prefix>/bin/shipguard validate",
        }

    tarball = Path(args.package_tarball).expanduser().resolve()
    install_prefix = (
        Path(args.fresh_install_prefix).expanduser().resolve()
        if args.fresh_install_prefix
        else Path(args.out).expanduser().resolve() / "fresh-install-prefix"
    )
    work_dir = (
        Path(args.fresh_install_work_dir).expanduser().resolve()
        if args.fresh_install_work_dir
        else Path(args.out).expanduser().resolve() / "fresh-install-work"
    )
    managed_prefix = args.fresh_install_prefix is None
    managed_work_dir = args.fresh_install_work_dir is None
    extract_dir = work_dir / "extracted"

    proof: dict[str, Any] = {
        "status": "blocked",
        "provided": True,
        "requiredForStableV4": True,
        "packageTarball": tarball.as_posix(),
        "installPrefix": install_prefix.as_posix(),
        "workDir": work_dir.as_posix(),
        "nextCommand": "./tests/v4_release_candidate_test.sh",
        "installCommand": "PREFIX=<fresh-prefix> <package>/scripts/install.sh",
        "validateCommand": "<fresh-prefix>/bin/shipguard validate",
    }
    if not tarball.is_file():
        proof["summary"] = "Release package tarball was not found."
        proof["error"] = f"package tarball not found: {tarball}"
        attach_fresh_install_proof_attachment(proof)
        return proof

    if install_prefix.exists() and not install_prefix.is_dir():
        proof["summary"] = "Fresh install prefix exists but is not a directory."
        proof["error"] = f"fresh install prefix is not a directory: {install_prefix}"
        attach_fresh_install_proof_attachment(proof)
        return proof
    if install_prefix.exists() and any(install_prefix.iterdir()):
        if managed_prefix:
            shutil.rmtree(install_prefix)
        else:
            proof["summary"] = "Fresh install prefix already exists and is not empty."
            proof["error"] = f"fresh install prefix must be empty: {install_prefix}"
            attach_fresh_install_proof_attachment(proof)
            return proof
    if work_dir.exists() and not work_dir.is_dir():
        if managed_work_dir:
            work_dir.unlink()
        else:
            proof["summary"] = "Fresh install work path exists but is not a directory."
            proof["error"] = f"fresh install work path is not a directory: {work_dir}"
            attach_fresh_install_proof_attachment(proof)
            return proof
    if work_dir.exists() and any(work_dir.iterdir()):
        if managed_work_dir:
            shutil.rmtree(work_dir)
        else:
            proof["summary"] = "Fresh install work directory already exists and is not empty."
            proof["error"] = f"fresh install work directory must be empty: {work_dir}"
            attach_fresh_install_proof_attachment(proof)
            return proof
    install_prefix.mkdir(parents=True, exist_ok=True)
    work_dir.mkdir(parents=True, exist_ok=True)

    extracted, extract_evidence = safe_extract_tarball(tarball, extract_dir)
    proof["extractStatus"] = "pass" if extracted else "blocked"
    proof["extractEvidence"] = extract_evidence
    if not extracted:
        attach_blocking_package_hygiene(proof, [tarball], args)
        proof["summary"] = "Release package tarball could not be safely extracted."
        attach_fresh_install_proof_attachment(proof)
        return proof

    package_root = find_package_root(extract_dir, version)
    if package_root is None:
        proof["summary"] = "Extracted package did not contain scripts/install.sh."
        proof["error"] = "package root not found"
        attach_fresh_install_proof_attachment(proof)
        return proof
    proof["packageRoot"] = package_root.as_posix()

    install_env = dict(os.environ, PREFIX=install_prefix.as_posix())
    install_result = run_process(["bash", str(package_root / "scripts" / "install.sh")], package_root, 120, install_env)
    proof["installResult"] = install_result
    if install_result["exitCode"] != 0:
        proof["summary"] = "Fresh package install failed."
        attach_fresh_install_proof_attachment(proof)
        return proof

    installed_bin = install_prefix / "bin" / "shipguard"
    installed_legacy_bin = install_prefix / "bin" / "codex-maintainer"
    installed_root = install_prefix / "lib" / "shipguard"
    proof["installedCli"] = installed_bin.as_posix()
    proof["installedLegacyCli"] = installed_legacy_bin.as_posix()
    proof["installedRoot"] = installed_root.as_posix()
    if not installed_bin.is_file():
        proof["summary"] = "Fresh install did not create the shipguard wrapper."
        proof["error"] = f"installed CLI missing: {installed_bin}"
        attach_fresh_install_proof_attachment(proof)
        return proof

    version_result = run_process([str(installed_bin), "version"], package_root, 30)
    legacy_version_result = run_process([str(installed_legacy_bin), "version"], package_root, 30) if installed_legacy_bin.is_file() else {"exitCode": "missing"}
    validate_result = run_process([str(installed_bin), "validate"], package_root, 120)
    proof["versionResult"] = version_result
    proof["legacyVersionResult"] = legacy_version_result
    proof["validateResult"] = validate_result
    proof["installedVersion"] = (version_result.get("stdout") or "").strip().splitlines()[0] if version_result.get("stdout") else ""
    proof["installedLegacyVersion"] = (
        (legacy_version_result.get("stdout") or "").strip().splitlines()[0] if legacy_version_result.get("stdout") else ""
    )
    forbidden_paths = find_forbidden_install_paths(installed_root)
    proof["forbiddenInstalledPathCount"] = len(forbidden_paths)
    proof["forbiddenInstalledPaths"] = forbidden_paths[:20]

    version_ok = version_result["exitCode"] == 0 and proof["installedVersion"] == version
    legacy_ok = legacy_version_result["exitCode"] == 0 and proof["installedLegacyVersion"] == version
    validate_ok = validate_result["exitCode"] == 0
    clean_ok = not forbidden_paths
    if version_ok and legacy_ok and validate_ok and clean_ok:
        proof["status"] = "pass"
        proof["summary"] = "Release package installed into a fresh prefix, reported the expected version, validated, and omitted generated/VCS paths."
    else:
        proof["summary"] = "Fresh package install proof did not pass every check."
        proof["versionMatches"] = version_ok
        proof["legacyVersionMatches"] = legacy_ok
        proof["validatePassed"] = validate_ok
        proof["installTreeClean"] = clean_ok
    attach_fresh_install_proof_attachment(proof)
    return proof


def attach_fresh_install_proof_attachment(proof: dict[str, Any]) -> None:
    if not proof.get("provided"):
        return
    missing_artifacts = [
        name
        for field, name in (
            ("versionResult", "shipguard-version"),
            ("legacyVersionResult", "codex-maintainer-version"),
            ("validateResult", "shipguard-validate"),
        )
        if not isinstance(proof.get(field), dict)
    ]
    proof["freshInstallProofAttachment"] = {
        "status": proof.get("status"),
        "packageTarball": proof.get("packageTarball", ""),
        "installPrefix": proof.get("installPrefix", ""),
        "workDir": proof.get("workDir", ""),
        "packageRoot": proof.get("packageRoot", ""),
        "installedRoot": proof.get("installedRoot", ""),
        "installedVersion": proof.get("installedVersion", ""),
        "installedLegacyVersion": proof.get("installedLegacyVersion", ""),
        "versionExitCode": (proof.get("versionResult") or {}).get("exitCode") if isinstance(proof.get("versionResult"), dict) else None,
        "legacyVersionExitCode": (proof.get("legacyVersionResult") or {}).get("exitCode") if isinstance(proof.get("legacyVersionResult"), dict) else None,
        "validateExitCode": (proof.get("validateResult") or {}).get("exitCode") if isinstance(proof.get("validateResult"), dict) else None,
        "forbiddenInstalledPathCount": proof.get("forbiddenInstalledPathCount"),
        "forbiddenInstalledPaths": proof.get("forbiddenInstalledPaths", []),
        "missingProofArtifacts": missing_artifacts,
        "nextCommand": proof.get("nextCommand"),
        "proofBoundary": {
            "freshInstallRequiredForStableV4": True,
            "cleanPrefixInstallRequired": True,
            "shipguardValidateRequired": True,
            "legacyAliasVersionRequired": True,
            "generatedCacheVcsPathsForbidden": True,
            "sourceOnlyProofCounts": False,
            "fixtureProofCountsAsStableV4PublicationProof": False,
        },
    }


def package_version(package_root: Path) -> str:
    return read_text(package_root / "VERSION").strip() or "unknown"


def prepare_empty_work_paths(
    proof: dict[str, Any],
    prefix: Path,
    work_dir: Path,
    managed_prefix: bool,
    managed_work_dir: bool,
    prefix_label: str,
    work_label: str,
) -> bool:
    if prefix.exists() and not prefix.is_dir():
        proof["summary"] = f"{prefix_label} exists but is not a directory."
        proof["error"] = f"{prefix_label} is not a directory: {prefix}"
        return False
    if prefix.exists() and any(prefix.iterdir()):
        if managed_prefix:
            shutil.rmtree(prefix)
        else:
            proof["summary"] = f"{prefix_label} already exists and is not empty."
            proof["error"] = f"{prefix_label} must be empty: {prefix}"
            return False
    if work_dir.exists() and not work_dir.is_dir():
        if managed_work_dir:
            work_dir.unlink()
        else:
            proof["summary"] = f"{work_label} exists but is not a directory."
            proof["error"] = f"{work_label} is not a directory: {work_dir}"
            return False
    if work_dir.exists() and any(work_dir.iterdir()):
        if managed_work_dir:
            shutil.rmtree(work_dir)
        else:
            proof["summary"] = f"{work_label} already exists and is not empty."
            proof["error"] = f"{work_label} must be empty: {work_dir}"
            return False
    prefix.mkdir(parents=True, exist_ok=True)
    work_dir.mkdir(parents=True, exist_ok=True)
    return True


def build_upgrade_package_proof(args: argparse.Namespace, version: str) -> dict[str, Any]:
    command_template = (
        "./bin/shipguard v4 release-candidate --path . --out /tmp/shipguard-v4-release-candidate "
        "--package-tarball <release-tarball> --upgrade-from-tarball <previous-release-tarball> "
        "--shipguard-eval --shareable"
    )
    if not args.package_tarball or not args.upgrade_from_tarball:
        return {
            "status": "not-provided",
            "provided": False,
            "requiredForStableV4": True,
            "summary": "No previous release tarball was supplied; stable v4 proof still needs an upgrade receipt from an existing install to the candidate package.",
            "nextCommand": command_template,
            "upgradeCommand": "PREFIX=<upgrade-prefix> <previous-package>/scripts/install.sh && PREFIX=<same-prefix> <candidate-package>/scripts/install.sh",
            "validateCommand": "<upgrade-prefix>/bin/shipguard validate",
        }

    candidate_tarball = Path(args.package_tarball).expanduser().resolve()
    previous_tarball = Path(args.upgrade_from_tarball).expanduser().resolve()
    upgrade_prefix = (
        Path(args.upgrade_prefix).expanduser().resolve()
        if args.upgrade_prefix
        else Path(args.out).expanduser().resolve() / "upgrade-prefix"
    )
    work_dir = (
        Path(args.upgrade_work_dir).expanduser().resolve()
        if args.upgrade_work_dir
        else Path(args.out).expanduser().resolve() / "upgrade-work"
    )
    managed_prefix = args.upgrade_prefix is None
    managed_work_dir = args.upgrade_work_dir is None
    previous_extract_dir = work_dir / "previous"
    candidate_extract_dir = work_dir / "candidate"

    proof: dict[str, Any] = {
        "status": "blocked",
        "provided": True,
        "requiredForStableV4": True,
        "previousTarball": previous_tarball.as_posix(),
        "candidateTarball": candidate_tarball.as_posix(),
        "upgradePrefix": upgrade_prefix.as_posix(),
        "workDir": work_dir.as_posix(),
        "nextCommand": "./tests/v4_release_candidate_test.sh",
        "upgradeCommand": "PREFIX=<upgrade-prefix> <previous-package>/scripts/install.sh && PREFIX=<same-prefix> <candidate-package>/scripts/install.sh",
        "validateCommand": "<upgrade-prefix>/bin/shipguard validate",
    }
    if not previous_tarball.is_file():
        proof["summary"] = "Previous release package tarball was not found."
        proof["error"] = f"previous release tarball not found: {previous_tarball}"
        attach_upgrade_package_proof_attachment(proof)
        return proof
    if not candidate_tarball.is_file():
        proof["summary"] = "Candidate release package tarball was not found."
        proof["error"] = f"candidate release tarball not found: {candidate_tarball}"
        attach_upgrade_package_proof_attachment(proof)
        return proof
    if not prepare_empty_work_paths(
        proof,
        upgrade_prefix,
        work_dir,
        managed_prefix,
        managed_work_dir,
        "upgrade prefix",
        "upgrade work directory",
    ):
        attach_upgrade_package_proof_attachment(proof)
        return proof

    previous_extracted, previous_extract_evidence = safe_extract_tarball(previous_tarball, previous_extract_dir)
    proof["previousExtractStatus"] = "pass" if previous_extracted else "blocked"
    proof["previousExtractEvidence"] = previous_extract_evidence
    if not previous_extracted:
        attach_blocking_package_hygiene(proof, [previous_tarball, candidate_tarball], args)
        proof["summary"] = "Previous release package tarball could not be safely extracted."
        attach_upgrade_package_proof_attachment(proof)
        return proof
    candidate_extracted, candidate_extract_evidence = safe_extract_tarball(candidate_tarball, candidate_extract_dir)
    proof["candidateExtractStatus"] = "pass" if candidate_extracted else "blocked"
    proof["candidateExtractEvidence"] = candidate_extract_evidence
    if not candidate_extracted:
        attach_blocking_package_hygiene(proof, [previous_tarball, candidate_tarball], args)
        proof["summary"] = "Candidate release package tarball could not be safely extracted."
        attach_upgrade_package_proof_attachment(proof)
        return proof

    previous_root = find_package_root(previous_extract_dir, version)
    candidate_root = find_package_root(candidate_extract_dir, version)
    if previous_root is None:
        proof["summary"] = "Previous package did not contain scripts/install.sh."
        proof["error"] = "previous package root not found"
        attach_upgrade_package_proof_attachment(proof)
        return proof
    if candidate_root is None:
        proof["summary"] = "Candidate package did not contain scripts/install.sh."
        proof["error"] = "candidate package root not found"
        attach_upgrade_package_proof_attachment(proof)
        return proof
    previous_version = package_version(previous_root)
    proof["previousPackageRoot"] = previous_root.as_posix()
    proof["candidatePackageRoot"] = candidate_root.as_posix()
    proof["previousPackageVersion"] = previous_version
    proof["candidatePackageVersion"] = package_version(candidate_root)

    install_env = dict(os.environ, PREFIX=upgrade_prefix.as_posix())
    previous_install_result = run_process(["bash", str(previous_root / "scripts" / "install.sh")], previous_root, 120, install_env)
    proof["previousInstallResult"] = previous_install_result
    if previous_install_result["exitCode"] != 0:
        proof["summary"] = "Previous package install failed before the upgrade."
        attach_upgrade_package_proof_attachment(proof)
        return proof

    installed_bin = upgrade_prefix / "bin" / "shipguard"
    installed_legacy_bin = upgrade_prefix / "bin" / "codex-maintainer"
    previous_version_result = run_process([str(installed_bin), "version"], previous_root, 30)
    previous_legacy_version_result = (
        run_process([str(installed_legacy_bin), "version"], previous_root, 30) if installed_legacy_bin.is_file() else {"exitCode": "missing"}
    )
    proof["previousVersionResult"] = previous_version_result
    proof["previousLegacyVersionResult"] = previous_legacy_version_result
    proof["previousInstalledVersion"] = (previous_version_result.get("stdout") or "").strip().splitlines()[0] if previous_version_result.get("stdout") else ""
    proof["previousInstalledLegacyVersion"] = (
        (previous_legacy_version_result.get("stdout") or "").strip().splitlines()[0] if previous_legacy_version_result.get("stdout") else ""
    )

    candidate_install_result = run_process(["bash", str(candidate_root / "scripts" / "install.sh")], candidate_root, 120, install_env)
    proof["candidateInstallResult"] = candidate_install_result
    if candidate_install_result["exitCode"] != 0:
        proof["summary"] = "Candidate package install failed during upgrade."
        attach_upgrade_package_proof_attachment(proof)
        return proof

    installed_root = upgrade_prefix / "lib" / "shipguard"
    upgraded_version_result = run_process([str(installed_bin), "version"], candidate_root, 30)
    upgraded_legacy_version_result = (
        run_process([str(installed_legacy_bin), "version"], candidate_root, 30) if installed_legacy_bin.is_file() else {"exitCode": "missing"}
    )
    validate_result = run_process([str(installed_bin), "validate"], candidate_root, 120)
    forbidden_paths = find_forbidden_install_paths(installed_root)
    proof.update(
        {
            "installedRoot": installed_root.as_posix(),
            "upgradedVersionResult": upgraded_version_result,
            "upgradedLegacyVersionResult": upgraded_legacy_version_result,
            "validateResult": validate_result,
            "upgradedVersion": (upgraded_version_result.get("stdout") or "").strip().splitlines()[0] if upgraded_version_result.get("stdout") else "",
            "upgradedLegacyVersion": (
                (upgraded_legacy_version_result.get("stdout") or "").strip().splitlines()[0]
                if upgraded_legacy_version_result.get("stdout")
                else ""
            ),
            "forbiddenInstalledPathCount": len(forbidden_paths),
            "forbiddenInstalledPaths": forbidden_paths[:20],
        }
    )

    previous_version_ok = previous_version_result["exitCode"] == 0 and proof["previousInstalledVersion"] == previous_version
    previous_legacy_ok = previous_legacy_version_result["exitCode"] == 0 and proof["previousInstalledLegacyVersion"] == previous_version
    upgraded_version_ok = upgraded_version_result["exitCode"] == 0 and proof["upgradedVersion"] == version
    upgraded_legacy_ok = upgraded_legacy_version_result["exitCode"] == 0 and proof["upgradedLegacyVersion"] == version
    validate_ok = validate_result["exitCode"] == 0
    clean_ok = not forbidden_paths
    if previous_version_ok and previous_legacy_ok and upgraded_version_ok and upgraded_legacy_ok and validate_ok and clean_ok:
        proof["status"] = "pass"
        proof["summary"] = "Previous package installed, candidate package upgraded the same prefix, version checks passed, validation passed, and the installed tree was clean."
    else:
        proof["summary"] = "Upgrade package proof did not pass every check."
        proof["previousVersionMatches"] = previous_version_ok
        proof["previousLegacyVersionMatches"] = previous_legacy_ok
        proof["upgradedVersionMatches"] = upgraded_version_ok
        proof["upgradedLegacyVersionMatches"] = upgraded_legacy_ok
        proof["validatePassed"] = validate_ok
        proof["installTreeClean"] = clean_ok
    attach_upgrade_package_proof_attachment(proof)
    return proof


def attach_upgrade_package_proof_attachment(proof: dict[str, Any]) -> None:
    if not proof.get("provided"):
        return
    missing_artifacts = [
        name
        for field, name in (
            ("previousVersionResult", "previous-shipguard-version"),
            ("previousLegacyVersionResult", "previous-codex-maintainer-version"),
            ("upgradedVersionResult", "upgraded-shipguard-version"),
            ("upgradedLegacyVersionResult", "upgraded-codex-maintainer-version"),
            ("validateResult", "shipguard-validate"),
        )
        if not isinstance(proof.get(field), dict)
    ]
    proof["upgradeProofAttachment"] = {
        "status": proof.get("status"),
        "previousTarball": proof.get("previousTarball", ""),
        "candidateTarball": proof.get("candidateTarball", ""),
        "upgradePrefix": proof.get("upgradePrefix", ""),
        "workDir": proof.get("workDir", ""),
        "previousPackageRoot": proof.get("previousPackageRoot", ""),
        "candidatePackageRoot": proof.get("candidatePackageRoot", ""),
        "installedRoot": proof.get("installedRoot", ""),
        "previousPackageVersion": proof.get("previousPackageVersion", ""),
        "candidatePackageVersion": proof.get("candidatePackageVersion", ""),
        "previousInstalledVersion": proof.get("previousInstalledVersion", ""),
        "previousInstalledLegacyVersion": proof.get("previousInstalledLegacyVersion", ""),
        "upgradedVersion": proof.get("upgradedVersion", ""),
        "upgradedLegacyVersion": proof.get("upgradedLegacyVersion", ""),
        "previousVersionExitCode": (proof.get("previousVersionResult") or {}).get("exitCode") if isinstance(proof.get("previousVersionResult"), dict) else None,
        "previousLegacyVersionExitCode": (proof.get("previousLegacyVersionResult") or {}).get("exitCode") if isinstance(proof.get("previousLegacyVersionResult"), dict) else None,
        "upgradedVersionExitCode": (proof.get("upgradedVersionResult") or {}).get("exitCode") if isinstance(proof.get("upgradedVersionResult"), dict) else None,
        "upgradedLegacyVersionExitCode": (proof.get("upgradedLegacyVersionResult") or {}).get("exitCode") if isinstance(proof.get("upgradedLegacyVersionResult"), dict) else None,
        "validateExitCode": (proof.get("validateResult") or {}).get("exitCode") if isinstance(proof.get("validateResult"), dict) else None,
        "forbiddenInstalledPathCount": proof.get("forbiddenInstalledPathCount"),
        "forbiddenInstalledPaths": proof.get("forbiddenInstalledPaths", []),
        "missingProofArtifacts": missing_artifacts,
        "nextCommand": proof.get("nextCommand"),
        "proofBoundary": {
            "samePrefixUpgradeRequiredForStableV4": True,
            "previousPackageInstallRequired": True,
            "candidatePackageInstallRequired": True,
            "versionChecksRequired": True,
            "shipguardValidateRequired": True,
            "cleanInstalledTreeRequired": True,
            "sourceOnlyProofCounts": False,
            "fixtureProofCountsAsStableV4PublicationProof": False,
        },
    }


def build_rollback_package_proof(args: argparse.Namespace, version: str) -> dict[str, Any]:
    command_template = (
        "./bin/shipguard v4 release-candidate --path . --out /tmp/shipguard-v4-release-candidate "
        "--package-tarball <release-tarball> --shipguard-eval --shareable"
    )
    if not args.package_tarball:
        return {
            "status": "not-provided",
            "provided": False,
            "requiredForStableV4": True,
            "summary": "No release package tarball was supplied; stable v4 proof still needs a rollback cleanup receipt for temporary package state.",
            "nextCommand": command_template,
            "rollbackCommand": "rm -rf <rollback-prefix>/bin/shipguard <rollback-prefix>/bin/codex-maintainer <rollback-prefix>/lib/shipguard",
        }

    tarball = Path(args.package_tarball).expanduser().resolve()
    rollback_prefix = (
        Path(args.rollback_prefix).expanduser().resolve()
        if args.rollback_prefix
        else Path(args.out).expanduser().resolve() / "rollback-prefix"
    )
    work_dir = (
        Path(args.rollback_work_dir).expanduser().resolve()
        if args.rollback_work_dir
        else Path(args.out).expanduser().resolve() / "rollback-work"
    )
    managed_prefix = args.rollback_prefix is None
    managed_work_dir = args.rollback_work_dir is None
    extract_dir = work_dir / "extracted"

    proof: dict[str, Any] = {
        "status": "blocked",
        "provided": True,
        "requiredForStableV4": True,
        "packageTarball": tarball.as_posix(),
        "rollbackPrefix": rollback_prefix.as_posix(),
        "workDir": work_dir.as_posix(),
        "nextCommand": "./tests/v4_release_candidate_test.sh",
        "rollbackCommand": "rm -rf <rollback-prefix>/bin/shipguard <rollback-prefix>/bin/codex-maintainer <rollback-prefix>/lib/shipguard",
    }
    if not tarball.is_file():
        proof["summary"] = "Release package tarball was not found for rollback proof."
        proof["error"] = f"package tarball not found: {tarball}"
        attach_rollback_package_proof_attachment(proof)
        return proof
    if not prepare_empty_work_paths(
        proof,
        rollback_prefix,
        work_dir,
        managed_prefix,
        managed_work_dir,
        "rollback prefix",
        "rollback work directory",
    ):
        attach_rollback_package_proof_attachment(proof)
        return proof

    extracted, extract_evidence = safe_extract_tarball(tarball, extract_dir)
    proof["extractStatus"] = "pass" if extracted else "blocked"
    proof["extractEvidence"] = extract_evidence
    if not extracted:
        attach_blocking_package_hygiene(proof, [tarball], args)
        proof["summary"] = "Release package tarball could not be safely extracted for rollback proof."
        attach_rollback_package_proof_attachment(proof)
        return proof

    package_root = find_package_root(extract_dir, version)
    if package_root is None:
        proof["summary"] = "Extracted package did not contain scripts/install.sh for rollback proof."
        proof["error"] = "package root not found"
        attach_rollback_package_proof_attachment(proof)
        return proof
    proof["packageRoot"] = package_root.as_posix()

    install_env = dict(os.environ, PREFIX=rollback_prefix.as_posix())
    install_result = run_process(["bash", str(package_root / "scripts" / "install.sh")], package_root, 120, install_env)
    proof["installResult"] = install_result
    if install_result["exitCode"] != 0:
        proof["summary"] = "Package install failed before rollback cleanup."
        attach_rollback_package_proof_attachment(proof)
        return proof

    installed_bin = rollback_prefix / "bin" / "shipguard"
    installed_legacy_bin = rollback_prefix / "bin" / "codex-maintainer"
    installed_root = rollback_prefix / "lib" / "shipguard"
    version_result = run_process([str(installed_bin), "version"], package_root, 30)
    proof["versionResult"] = version_result
    proof["installedVersion"] = (version_result.get("stdout") or "").strip().splitlines()[0] if version_result.get("stdout") else ""
    cleanup_paths = [installed_bin, installed_legacy_bin, installed_root]
    removed_paths: list[str] = []
    for path in cleanup_paths:
        if path.is_dir():
            shutil.rmtree(path)
            removed_paths.append(path.as_posix())
        elif path.exists():
            path.unlink()
            removed_paths.append(path.as_posix())
    remaining_paths = [path.as_posix() for path in cleanup_paths if path.exists()]
    proof["installedRoot"] = installed_root.as_posix()
    proof["removedPathCount"] = len(removed_paths)
    proof["removedPaths"] = removed_paths
    proof["remainingPathCount"] = len(remaining_paths)
    proof["remainingPaths"] = remaining_paths

    version_ok = version_result["exitCode"] == 0 and proof["installedVersion"] == version
    cleanup_ok = not remaining_paths and len(removed_paths) == len(cleanup_paths)
    if version_ok and cleanup_ok:
        proof["status"] = "pass"
        proof["summary"] = "Candidate package installed into a temporary prefix and known ShipGuard package state was removed cleanly for rollback."
    else:
        proof["summary"] = "Rollback cleanup proof did not pass every check."
        proof["versionMatches"] = version_ok
        proof["cleanupComplete"] = cleanup_ok
    attach_rollback_package_proof_attachment(proof)
    return proof


def attach_rollback_package_proof_attachment(proof: dict[str, Any]) -> None:
    if not proof.get("provided"):
        return
    missing_artifacts = [
        name
        for field, name in (
            ("versionResult", "shipguard-version"),
            ("removedPaths", "removed-package-paths"),
            ("remainingPaths", "remaining-package-paths"),
        )
        if field not in proof
    ]
    proof["rollbackProofAttachment"] = {
        "status": proof.get("status"),
        "packageTarball": proof.get("packageTarball", ""),
        "rollbackPrefix": proof.get("rollbackPrefix", ""),
        "workDir": proof.get("workDir", ""),
        "packageRoot": proof.get("packageRoot", ""),
        "installedRoot": proof.get("installedRoot", ""),
        "installedVersion": proof.get("installedVersion", ""),
        "versionExitCode": (proof.get("versionResult") or {}).get("exitCode") if isinstance(proof.get("versionResult"), dict) else None,
        "removedPathCount": proof.get("removedPathCount"),
        "removedPaths": proof.get("removedPaths", []),
        "remainingPathCount": proof.get("remainingPathCount"),
        "remainingPaths": proof.get("remainingPaths", []),
        "missingProofArtifacts": missing_artifacts,
        "nextCommand": proof.get("nextCommand"),
        "proofBoundary": {
            "rollbackCleanupRequiredForStableV4": True,
            "temporaryPrefixInstallRequired": True,
            "versionCheckRequired": True,
            "knownPackageStateRemovalRequired": True,
            "sourceOnlyProofCounts": False,
            "fixtureProofCountsAsStableV4PublicationProof": False,
        },
    }


def build_github_release_asset_download_proof(args: argparse.Namespace, version: str) -> dict[str, Any]:
    release_version = args.release_version or version
    release_tag = normalize_release_tag(release_version)
    command_template = (
        "./bin/shipguard v4 release-candidate --path . --out /tmp/shipguard-v4-release-candidate "
        "--download-release-assets --github-release-repo <owner/repo> --release-version <version> --shipguard-eval --shareable"
    )
    if not args.download_release_assets:
        return {
            "status": "not-requested",
            "requested": False,
            "requiredForStableV4": False,
            "summary": "Native GitHub release asset download was not requested; LaunchKey will use --release-assets when supplied.",
            "nextCommand": command_template,
        }

    download_dir = (
        Path(args.download_release_assets_dir).expanduser().resolve()
        if args.download_release_assets_dir
        else Path(args.release_assets).expanduser().resolve()
        if args.release_assets
        else Path(args.out).expanduser().resolve() / "downloaded-release-assets"
    )
    api_url = args.github_api_url.rstrip("/")
    proof: dict[str, Any] = {
        "status": "blocked",
        "requested": True,
        "requiredForStableV4": False,
        "repo": args.github_release_repo or "",
        "version": release_version,
        "tag": release_tag,
        "apiUrl": api_url,
        "downloadDir": download_dir.as_posix(),
        "nextCommand": command_template,
        "downloadedAssets": [],
    }
    if not args.github_release_repo:
        proof["summary"] = "GitHub release asset download was requested, but no repository was supplied."
        proof["error"] = "missing --github-release-repo <owner/repo>"
        attach_github_release_asset_download_blocking_proof(proof)
        return proof
    if "/" not in args.github_release_repo:
        proof["summary"] = "GitHub release repository must use owner/repo syntax."
        proof["error"] = f"invalid --github-release-repo value: {args.github_release_repo}"
        attach_github_release_asset_download_blocking_proof(proof)
        return proof
    if download_dir.exists() and not download_dir.is_dir():
        proof["summary"] = "GitHub release download destination exists but is not a directory."
        proof["error"] = f"download destination is not a directory: {download_dir}"
        attach_github_release_asset_download_blocking_proof(proof)
        return proof
    if download_dir.exists() and any(download_dir.iterdir()):
        proof["summary"] = "GitHub release download destination already exists and is not empty."
        proof["error"] = f"download destination must be empty: {download_dir}"
        attach_github_release_asset_download_blocking_proof(proof)
        return proof

    token = os.environ.get(args.github_token_env or "")
    api_headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "shipguard-launchkey",
    }
    asset_headers = {
        "Accept": "application/octet-stream",
        "User-Agent": "shipguard-launchkey",
    }
    if token:
        api_headers["Authorization"] = f"Bearer {token}"
        asset_headers["Authorization"] = f"Bearer {token}"

    release_endpoint = join_api_url(api_url, f"/repos/{args.github_release_repo}/releases/tags/{release_tag}")
    proof["releaseEndpoint"] = release_endpoint
    try:
        release = request_json(release_endpoint, api_headers)
        assets = release.get("assets")
        if not isinstance(assets, list) or not assets:
            proof["summary"] = "GitHub release has no downloadable assets."
            proof["error"] = "release asset list was empty"
            proof["releaseUrl"] = release.get("html_url") or ""
            attach_github_release_asset_download_blocking_proof(proof)
            return proof
        download_dir.mkdir(parents=True, exist_ok=True)
        downloaded_assets: list[dict[str, Any]] = []
        for asset in assets:
            if not isinstance(asset, dict):
                continue
            name = safe_asset_name(str(asset.get("name") or ""))
            source_url = str(asset.get("browser_download_url") or asset.get("url") or "")
            if not source_url:
                raise RuntimeError(f"asset {name} has no download URL")
            destination = download_dir / name
            download_url_to_file(source_url, destination, asset_headers)
            downloaded_assets.append(
                {
                    "name": name,
                    "size": destination.stat().st_size,
                    "sha256": sha256_file(destination),
                    "source": source_url,
                    "path": destination.as_posix(),
                }
            )
        if not downloaded_assets:
            proof["summary"] = "GitHub release asset response did not contain usable assets."
            proof["error"] = "no usable asset objects were downloaded"
            proof["releaseUrl"] = release.get("html_url") or ""
            attach_github_release_asset_download_blocking_proof(proof)
            return proof
        proof.update(
            {
                "status": "pass",
                "summary": "GitHub release assets were downloaded into a local LaunchKey proof directory.",
                "releaseUrl": release.get("html_url") or "",
                "assetCount": len(downloaded_assets),
                "downloadedAssets": downloaded_assets,
            }
        )
        attach_github_release_asset_download_proof_attachment(proof)
    except (OSError, RuntimeError, urllib.error.URLError, urllib.error.HTTPError) as exc:
        if download_dir.exists():
            shutil.rmtree(download_dir, ignore_errors=True)
        proof["summary"] = "GitHub release asset download failed."
        proof["error"] = short_output(str(exc), 500)
    if proof.get("status") != "pass":
        attach_github_release_asset_download_blocking_proof(proof)
    return proof


def attach_github_release_asset_download_proof_attachment(proof: dict[str, Any]) -> None:
    if not proof.get("requested") or proof.get("status") != "pass":
        return
    downloaded_assets = [item for item in proof.get("downloadedAssets", []) if isinstance(item, dict)]
    proof["downloadProofAttachment"] = {
        "status": proof.get("status"),
        "repo": proof.get("repo", ""),
        "version": proof.get("version", ""),
        "tag": proof.get("tag", ""),
        "apiUrl": proof.get("apiUrl", ""),
        "releaseEndpoint": proof.get("releaseEndpoint", ""),
        "releaseUrl": proof.get("releaseUrl", ""),
        "downloadDir": proof.get("downloadDir", ""),
        "assetCount": proof.get("assetCount"),
        "downloadedAssetNames": [
            str(item.get("name") or "")
            for item in downloaded_assets
            if item.get("name")
        ],
        "downloadedAssetDigests": [
            {
                "name": str(item.get("name") or ""),
                "sha256": str(item.get("sha256") or ""),
            }
            for item in downloaded_assets
            if item.get("name")
        ],
        "nextCommand": proof.get("nextCommand"),
        "proofBoundary": {
            "githubReleaseRepoRequired": True,
            "releaseTagRequired": True,
            "assetDownloadRequired": True,
            "sha256RecordedForDownloadedAssets": True,
            "releaseConsumeStillRequiredForStableV4": True,
            "sourceOnlyProofCounts": False,
            "fixtureProofCountsAsStableV4PublicationProof": False,
        },
    }


def attach_github_release_asset_download_blocking_proof(proof: dict[str, Any]) -> None:
    if not proof.get("requested") or proof.get("status") == "pass":
        return
    proof["downloadBlockingProof"] = {
        "status": proof.get("status"),
        "repo": proof.get("repo", ""),
        "tag": proof.get("tag", ""),
        "apiUrl": proof.get("apiUrl", ""),
        "releaseEndpoint": proof.get("releaseEndpoint", ""),
        "releaseUrl": proof.get("releaseUrl", ""),
        "downloadDir": proof.get("downloadDir", ""),
        "assetCount": proof.get("assetCount"),
        "downloadedAssetNames": [
            str(item.get("name") or "")
            for item in proof.get("downloadedAssets", [])
            if isinstance(item, dict) and item.get("name")
        ],
        "summary": proof.get("summary", ""),
        "error": proof.get("error", ""),
        "nextCommand": proof.get("nextCommand"),
        "proofBoundary": {
            "githubReleaseRepoRequired": True,
            "ownerRepoSyntaxRequired": True,
            "emptyDownloadDestinationRequired": True,
            "releaseAssetsRequired": True,
            "sourceOnlyProofCounts": False,
            "fixtureProofCountsAsStableV4PublicationProof": False,
        },
    }


def build_published_release_asset_proof(
    args: argparse.Namespace,
    root: Path,
    version: str,
    github_release_asset_download_proof: dict[str, Any],
) -> dict[str, Any]:
    command_template = (
        "./bin/shipguard v4 release-candidate --path . --out /tmp/shipguard-v4-release-candidate "
        "--release-assets <downloaded-assets-dir> --release-version <version> --shipguard-eval --shareable"
    )
    consume_command_template = (
        "./bin/shipguard release-consume verify --dir <downloaded-assets-dir> "
        "--out <consume-dir> --version <version>"
    )
    if github_release_asset_download_proof.get("requested") and github_release_asset_download_proof.get("status") != "pass":
        proof = {
            "status": "blocked",
            "provided": True,
            "requiredForStableV4": True,
            "downloadSource": "github-release-assets",
            "summary": "GitHub release assets could not be downloaded, so consumer-side release asset verification did not run.",
            "nextCommand": github_release_asset_download_proof.get("nextCommand") or command_template,
            "consumeCommand": consume_command_template,
            "downloadProofStatus": github_release_asset_download_proof.get("status"),
            "error": github_release_asset_download_proof.get("error", ""),
        }
        attach_release_asset_proof_attachment(proof)
        return proof

    effective_release_assets = (
        github_release_asset_download_proof.get("downloadDir")
        if github_release_asset_download_proof.get("status") == "pass"
        else args.release_assets
    )
    if not effective_release_assets:
        return {
            "status": "not-provided",
            "provided": False,
            "requiredForStableV4": True,
            "summary": "No downloaded release assets were supplied; stable v4 proof still needs consumer-side release asset verification.",
            "nextCommand": command_template,
            "consumeCommand": consume_command_template,
        }

    assets_dir = Path(str(effective_release_assets)).expanduser().resolve()
    consume_out = (
        Path(args.release_consume_out).expanduser().resolve()
        if args.release_consume_out
        else Path(args.out).expanduser().resolve() / "release-consume"
    )
    release_version = args.release_version or version
    command = [
        str(root / "bin" / "shipguard"),
        "release-consume",
        "verify",
        "--dir",
        str(assets_dir),
        "--out",
        str(consume_out),
        "--version",
        release_version,
    ]

    proof: dict[str, Any] = {
        "status": "blocked",
        "provided": True,
        "requiredForStableV4": True,
        "assetsDir": assets_dir.as_posix(),
        "consumeOut": consume_out.as_posix(),
        "version": release_version,
        "downloadSource": "github-release-assets" if github_release_asset_download_proof.get("status") == "pass" else "supplied-directory",
        "downloadProofStatus": github_release_asset_download_proof.get("status"),
        "command": " ".join(command),
        "commandTemplate": consume_command_template,
        "nextCommand": "./tests/v4_release_candidate_test.sh",
        "consumerReport": "consumer-report.json",
        "assetDigestMatrix": "asset-digests.json",
    }
    if not assets_dir.exists():
        proof["summary"] = "Downloaded release assets directory was not found."
        proof["error"] = f"release assets directory not found: {assets_dir}"
        attach_release_asset_proof_attachment(proof)
        return proof
    if not (root / "bin" / "shipguard").exists():
        proof["summary"] = "ShipGuard CLI was not found in the inspected checkout."
        proof["error"] = "bin/shipguard not found"
        attach_release_asset_proof_attachment(proof)
        return proof

    try:
        completed = subprocess.run(
            command,
            cwd=root,
            check=False,
            capture_output=True,
            text=True,
            timeout=120,
        )
    except subprocess.TimeoutExpired as exc:
        proof["summary"] = "Consumer-side release asset verification timed out."
        proof["exitCode"] = "timeout"
        proof["stdout"] = short_output(exc.stdout or "")
        proof["stderr"] = short_output(exc.stderr or "")
        attach_release_asset_proof_attachment(proof)
        return proof

    consumer_report = load_json(consume_out / "consumer-report.json")
    digest_report = load_json(consume_out / "asset-digests.json")
    consumer_status = consumer_report.get("status")
    consumer_summary = consumer_report.get("summary") if isinstance(consumer_report.get("summary"), dict) else {}
    published_summary = consumer_report.get("published") if isinstance(consumer_report.get("published"), dict) else {}
    proof.update(
        {
            "exitCode": completed.returncode,
            "stdout": short_output(completed.stdout),
            "stderr": short_output(completed.stderr),
            "consumerReportStatus": consumer_status or "missing",
            "consumerReportPath": (consume_out / "consumer-report.json").as_posix(),
            "assetDigestMatrixPath": (consume_out / "asset-digests.json").as_posix(),
            "artifactSha256": consumer_report.get("artifact_sha256") or consumer_report.get("artifact", {}).get("sha256"),
            "replayStatus": consumer_report.get("replay_status") or consumer_summary.get("replay_status"),
            "attestationStatus": consumer_report.get("attestation_status") or consumer_summary.get("attestation_status"),
            "publishedReplayCrosscheck": consumer_report.get("published_assets", {}).get("replay_report") or published_summary.get("replay_report"),
            "publishedAttestationCrosscheck": consumer_report.get("published_assets", {}).get("attestation") or published_summary.get("attestation"),
            "publishedBadgeCrosscheck": consumer_report.get("published_assets", {}).get("attestation_badge") or published_summary.get("attestation_badge"),
            "assetCount": len(digest_report.get("assets", [])) if isinstance(digest_report.get("assets"), list) else None,
        }
    )
    if completed.returncode == 0 and consumer_status == "pass":
        proof["status"] = "pass"
        proof["summary"] = "Supplied downloaded release assets passed consumer-side verification."
    else:
        proof["summary"] = "Supplied downloaded release assets did not pass consumer-side verification."
    attach_release_asset_proof_attachment(proof)
    return proof


def attach_release_asset_proof_attachment(proof: dict[str, Any]) -> None:
    if not proof.get("provided"):
        return
    missing_artifacts = [
        name
        for field, name in (
            ("consumerReportPath", "consumer-report.json"),
            ("assetDigestMatrixPath", "asset-digests.json"),
        )
        if not proof.get(field)
    ]
    proof["releaseAssetProofAttachment"] = {
        "status": proof.get("status"),
        "downloadSource": proof.get("downloadSource"),
        "downloadProofStatus": proof.get("downloadProofStatus"),
        "assetsDir": proof.get("assetsDir", ""),
        "consumeOut": proof.get("consumeOut", ""),
        "consumerReportPath": proof.get("consumerReportPath", ""),
        "assetDigestMatrixPath": proof.get("assetDigestMatrixPath", ""),
        "artifactSha256": proof.get("artifactSha256", ""),
        "consumerReportStatus": proof.get("consumerReportStatus", ""),
        "replayStatus": proof.get("replayStatus", ""),
        "attestationStatus": proof.get("attestationStatus", ""),
        "publishedReplayCrosscheck": proof.get("publishedReplayCrosscheck", ""),
        "publishedAttestationCrosscheck": proof.get("publishedAttestationCrosscheck", ""),
        "publishedBadgeCrosscheck": proof.get("publishedBadgeCrosscheck", ""),
        "assetCount": proof.get("assetCount"),
        "missingProofArtifacts": missing_artifacts,
        "consumeCommand": proof.get("consumeCommand"),
        "nextCommand": proof.get("consumeCommand") or proof.get("nextCommand"),
        "proofBoundary": {
            "downloadedOrSuppliedReleaseAssetsRequired": True,
            "releaseConsumeVerificationRequired": True,
            "assetDigestMatrixRequired": True,
            "sourceOnlyProofCounts": False,
            "fixtureProofCountsAsStableV4PublicationProof": False,
        },
    }


def collect_external_adoption_evidence_files(raw_paths: list[str]) -> tuple[list[Path], list[str]]:
    files: list[Path] = []
    errors: list[str] = []
    for raw in raw_paths:
        path = Path(raw).expanduser().resolve()
        if not path.exists():
            errors.append(f"external adoption evidence path not found: {path}")
            continue
        if path.is_file():
            if path.suffix.lower() == ".json":
                files.append(path)
            else:
                errors.append(f"external adoption evidence must be JSON: {path}")
            continue
        if path.is_dir():
            found = sorted(path.rglob("*.json"))
            if found:
                files.extend(found)
            else:
                errors.append(f"external adoption evidence directory has no JSON records: {path}")
            continue
        errors.append(f"external adoption evidence path is unsupported: {path}")
    return files, errors


def evaluate_external_adoption_record(path: Path) -> dict[str, Any]:
    record: dict[str, Any] = {
        "path": path.as_posix(),
        "status": "blocked",
        "stableV4Eligible": False,
        "missingFields": [],
        "errors": [],
    }
    raw_text = read_text(path)
    if PRIVATE_OR_SECRET_RE.search(raw_text):
        record["errors"].append("record contains local/private app paths, app identifiers, or token-like text")
    data = load_json(path)
    if not data:
        record["errors"].append("record is not a JSON object")
        return record

    required_fields = [
        "schemaVersion",
        "evidenceType",
        "evidenceClass",
        "actorRelationship",
        "generatedAt",
        "status",
        "privateDataRedacted",
        "commands",
        "artifacts",
        "outcome",
        "nonClaims",
    ]
    for field in required_fields:
        if field not in data:
            record["missingFields"].append(field)
    commands = data.get("commands") if isinstance(data.get("commands"), list) else []
    artifacts = data.get("artifacts") if isinstance(data.get("artifacts"), list) else []
    non_claims = data.get("nonClaims") if isinstance(data.get("nonClaims"), list) else []
    evidence_class = str(data.get("evidenceClass") or "")
    actor_relationship = str(data.get("actorRelationship") or "")
    fixture_synthetic = bool(data.get("fixtureSynthetic"))

    if data.get("status") != "pass":
        record["errors"].append("record status must be pass")
    if data.get("privateDataRedacted") is not True:
        record["errors"].append("privateDataRedacted must be true")
    if not any("shipguard" in str(command) for command in commands):
        record["errors"].append("commands must include at least one ShipGuard command")
    if not artifacts:
        record["errors"].append("artifacts must name at least one reviewed artifact")
    if not non_claims:
        record["errors"].append("nonClaims must state what this evidence does not prove")
    if actor_relationship != "independent":
        record["errors"].append("actorRelationship must be independent for stable-v4 adoption evidence")

    record.update(
        {
            "schemaVersion": data.get("schemaVersion"),
            "evidenceType": data.get("evidenceType"),
            "evidenceClass": evidence_class,
            "actorRelationship": actor_relationship,
            "generatedAt": data.get("generatedAt"),
            "source": data.get("source", ""),
            "actor": data.get("actor", ""),
            "commandCount": len(commands),
            "artifactCount": len(artifacts),
            "outcome": data.get("outcome", ""),
            "fixtureSynthetic": fixture_synthetic,
        }
    )
    if record["missingFields"] or record["errors"]:
        return record

    stable_eligible = (
        evidence_class in {"public-external", "private-redacted-external"}
        and actor_relationship == "independent"
        and not fixture_synthetic
        and (data.get("consentToShare") is True or data.get("shareableSummaryOnly") is True)
    )
    record["status"] = "pass"
    record["stableV4Eligible"] = stable_eligible
    if not stable_eligible:
        record["stableV4Reason"] = (
            "Record is structurally valid but not stable-v4 eligible; use real independent public-external or private-redacted-external evidence."
        )
    return record


def build_external_adoption_evidence_proof(args: argparse.Namespace) -> dict[str, Any]:
    command_template = (
        "./bin/shipguard v4 release-candidate --path . --out /tmp/shipguard-v4-release-candidate "
        "--external-adoption-evidence <evidence-json-or-dir> --shipguard-eval --shareable"
    )
    evidence_inputs = list(args.external_adoption_evidence or [])
    if not evidence_inputs:
        return {
            "status": "not-provided",
            "provided": False,
            "requiredForStableV4": True,
            "stableV4GateStatus": "not-provided",
            "summary": "No external adoption evidence was supplied; stable v4 proof still needs independent user or maintainer evidence outside the ShipGuard maintainer loop.",
            "nextCommand": command_template,
            "evidenceContract": "Provide JSON records with evidenceType, evidenceClass, independent actorRelationship, status=pass, redaction, commands, artifacts, outcome, and nonClaims.",
        }

    files, collection_errors = collect_external_adoption_evidence_files(evidence_inputs)
    records = [evaluate_external_adoption_record(path) for path in files]
    invalid_records = [record for record in records if record.get("status") != "pass"]
    stable_records = [record for record in records if record.get("stableV4Eligible")]
    proof: dict[str, Any] = {
        "status": "blocked",
        "provided": True,
        "requiredForStableV4": True,
        "stableV4GateStatus": "blocked",
        "summary": "External adoption evidence was supplied but did not pass the evidence contract.",
        "nextCommand": command_template,
        "evidenceInputs": [Path(raw).expanduser().resolve().as_posix() for raw in evidence_inputs],
        "evidenceRecordCount": len(records),
        "validRecordCount": len(records) - len(invalid_records),
        "invalidRecordCount": len(invalid_records),
        "stableV4EligibleEvidenceCount": len(stable_records),
        "collectionErrors": collection_errors,
        "records": records,
    }
    if collection_errors or not files:
        proof["error"] = collection_errors[0] if collection_errors else "no external adoption evidence records found"
        return proof
    if invalid_records:
        first = invalid_records[0]
        proof["error"] = "; ".join(first.get("missingFields", []) + first.get("errors", []))
        return proof
    proof["status"] = "pass"
    if stable_records:
        proof["stableV4GateStatus"] = "pass"
        proof["summary"] = "External adoption evidence passed the structural contract and includes stable-v4 eligible independent evidence."
    else:
        proof["stableV4GateStatus"] = "review"
        proof["summary"] = "External adoption evidence is structurally valid, but none of the records are stable-v4 eligible independent evidence."
        proof["nextAction"] = "Attach real public-external or private-redacted-external adoption evidence before any stable-v4 release claim."
    return proof


SECURITY_SCOPE_REQUIRED = {
    "cli",
    "plugin",
    "github-actions",
    "release-proof",
    "package-install",
    "redaction-privacy",
}


def collect_security_review_evidence_files(raw_paths: list[str]) -> tuple[list[Path], list[str]]:
    files: list[Path] = []
    errors: list[str] = []
    for raw in raw_paths:
        path = Path(raw).expanduser().resolve()
        if not path.exists():
            errors.append(f"security review evidence path not found: {path}")
            continue
        if path.is_file():
            if path.suffix.lower() == ".json":
                files.append(path)
            else:
                errors.append(f"security review evidence must be JSON: {path}")
            continue
        if path.is_dir():
            found = sorted(path.rglob("*.json"))
            if found:
                files.extend(found)
            else:
                errors.append(f"security review evidence directory has no JSON records: {path}")
            continue
        errors.append(f"security review evidence path is unsupported: {path}")
    return files, errors


def security_scope_values(scope: Any) -> set[str]:
    if isinstance(scope, list):
        return {str(item) for item in scope}
    if isinstance(scope, dict):
        raw = scope.get("areas") or scope.get("surfaces") or scope.get("scope")
        if isinstance(raw, list):
            return {str(item) for item in raw}
    return set()


def finding_count(summary: Any, key: str) -> int | None:
    if not isinstance(summary, dict):
        return None
    value = summary.get(key)
    if isinstance(value, bool):
        return None
    if isinstance(value, int):
        return value
    return None


def evaluate_security_review_record(path: Path) -> dict[str, Any]:
    record: dict[str, Any] = {
        "path": path.as_posix(),
        "status": "blocked",
        "stableV4Eligible": False,
        "missingFields": [],
        "errors": [],
    }
    raw_text = read_text(path)
    if PRIVATE_OR_SECRET_RE.search(raw_text):
        record["errors"].append("record contains local/private app paths, app identifiers, or token-like text")
    data = load_json(path)
    if not data:
        record["errors"].append("record is not a JSON object")
        return record

    required_fields = [
        "schemaVersion",
        "evidenceType",
        "evidenceClass",
        "reviewerRelationship",
        "generatedAt",
        "status",
        "privateDataRedacted",
        "scope",
        "methodology",
        "commands",
        "artifacts",
        "findingsSummary",
        "nonClaims",
    ]
    for field in required_fields:
        if field not in data:
            record["missingFields"].append(field)

    commands = data.get("commands") if isinstance(data.get("commands"), list) else []
    artifacts = data.get("artifacts") if isinstance(data.get("artifacts"), list) else []
    methodology = data.get("methodology") if isinstance(data.get("methodology"), list) else []
    non_claims = data.get("nonClaims") if isinstance(data.get("nonClaims"), list) else []
    scope_values = security_scope_values(data.get("scope"))
    findings_summary = data.get("findingsSummary") if isinstance(data.get("findingsSummary"), dict) else {}
    critical_open = finding_count(findings_summary, "criticalOpen")
    high_open = finding_count(findings_summary, "highOpen")
    evidence_class = str(data.get("evidenceClass") or "")
    reviewer_relationship = str(data.get("reviewerRelationship") or "")
    fixture_synthetic = bool(data.get("fixtureSynthetic"))
    missing_scope = sorted(SECURITY_SCOPE_REQUIRED - scope_values)

    if data.get("status") != "pass":
        record["errors"].append("record status must be pass")
    if data.get("privateDataRedacted") is not True:
        record["errors"].append("privateDataRedacted must be true")
    if not scope_values:
        record["errors"].append("scope must list reviewed ShipGuard security surfaces")
    if not methodology:
        record["errors"].append("methodology must name review methods")
    if not any("shipguard" in str(command).lower() for command in commands):
        record["errors"].append("commands must include at least one ShipGuard command")
    if not artifacts:
        record["errors"].append("artifacts must name at least one reviewed artifact")
    if not non_claims:
        record["errors"].append("nonClaims must state what this evidence does not prove")
    if critical_open is None:
        record["errors"].append("findingsSummary.criticalOpen must be an integer")
    if high_open is None:
        record["errors"].append("findingsSummary.highOpen must be an integer")
    if isinstance(critical_open, int) and critical_open > 0:
        record["errors"].append("criticalOpen must be 0 for stable-v4 security evidence")
    if isinstance(high_open, int) and high_open > 0:
        record["errors"].append("highOpen must be 0 for stable-v4 security evidence")

    record.update(
        {
            "schemaVersion": data.get("schemaVersion"),
            "evidenceType": data.get("evidenceType"),
            "evidenceClass": evidence_class,
            "reviewerRelationship": reviewer_relationship,
            "generatedAt": data.get("generatedAt"),
            "source": data.get("source", ""),
            "reviewer": data.get("reviewer", ""),
            "scope": sorted(scope_values),
            "missingStableScope": missing_scope,
            "methodologyCount": len(methodology),
            "commandCount": len(commands),
            "artifactCount": len(artifacts),
            "criticalOpen": critical_open,
            "highOpen": high_open,
            "outcome": data.get("outcome", ""),
            "fixtureSynthetic": fixture_synthetic,
        }
    )
    if record["missingFields"] or record["errors"]:
        return record

    stable_eligible = (
        evidence_class in {"public-security-review", "private-redacted-security-review"}
        and reviewer_relationship in {"independent", "maintainer-security-review"}
        and not fixture_synthetic
        and not missing_scope
        and critical_open == 0
        and high_open == 0
        and (data.get("consentToShare") is True or data.get("shareableSummaryOnly") is True)
    )
    record["status"] = "pass"
    record["stableV4Eligible"] = stable_eligible
    if not stable_eligible:
        record["stableV4Reason"] = (
            "Record is structurally valid but not stable-v4 eligible; use real public-security-review or private-redacted-security-review evidence with required scope coverage and no open critical/high findings."
        )
    return record


def build_security_review_evidence_proof(args: argparse.Namespace) -> dict[str, Any]:
    command_template = (
        "./bin/shipguard v4 release-candidate --path . --out /tmp/shipguard-v4-release-candidate "
        "--security-review-evidence <evidence-json-or-dir> --shipguard-eval --shareable"
    )
    evidence_inputs = list(args.security_review_evidence or [])
    if not evidence_inputs:
        return {
            "status": "not-provided",
            "provided": False,
            "requiredForStableV4": True,
            "stableV4GateStatus": "not-provided",
            "summary": "No final security review evidence was supplied; stable v4 proof still needs reviewed security evidence for CLI, plugin, GitHub Actions, release proof, package install, and redaction/privacy surfaces.",
            "nextCommand": command_template,
            "requiredScope": sorted(SECURITY_SCOPE_REQUIRED),
            "evidenceContract": "Provide JSON records with evidenceType, evidenceClass, reviewerRelationship, status=pass, redaction, scope, methodology, commands, artifacts, findingsSummary.criticalOpen=0, findingsSummary.highOpen=0, and nonClaims.",
        }

    files, collection_errors = collect_security_review_evidence_files(evidence_inputs)
    records = [evaluate_security_review_record(path) for path in files]
    invalid_records = [record for record in records if record.get("status") != "pass"]
    stable_records = [record for record in records if record.get("stableV4Eligible")]
    proof: dict[str, Any] = {
        "status": "blocked",
        "provided": True,
        "requiredForStableV4": True,
        "stableV4GateStatus": "blocked",
        "summary": "Security review evidence was supplied but did not pass the evidence contract.",
        "nextCommand": command_template,
        "requiredScope": sorted(SECURITY_SCOPE_REQUIRED),
        "evidenceInputs": [Path(raw).expanduser().resolve().as_posix() for raw in evidence_inputs],
        "evidenceRecordCount": len(records),
        "validRecordCount": len(records) - len(invalid_records),
        "invalidRecordCount": len(invalid_records),
        "stableV4EligibleEvidenceCount": len(stable_records),
        "collectionErrors": collection_errors,
        "records": records,
    }
    if collection_errors or not files:
        proof["error"] = collection_errors[0] if collection_errors else "no security review evidence records found"
        return proof
    if invalid_records:
        first = invalid_records[0]
        proof["error"] = "; ".join(first.get("missingFields", []) + first.get("errors", []))
        return proof
    proof["status"] = "pass"
    if stable_records:
        proof["stableV4GateStatus"] = "pass"
        proof["summary"] = "Security review evidence passed the structural contract and includes stable-v4 eligible review evidence."
    else:
        proof["stableV4GateStatus"] = "review"
        proof["summary"] = "Security review evidence is structurally valid, but none of the records are stable-v4 eligible review evidence."
        proof["nextAction"] = "Attach real public-security-review or private-redacted-security-review evidence before any stable-v4 release claim."
    return proof


def failed_process_excerpt(proof: dict[str, Any]) -> str:
    for key in (
        "validateResult",
        "installResult",
        "previousInstallResult",
        "candidateInstallResult",
        "versionResult",
        "legacyVersionResult",
        "previousVersionResult",
        "upgradedVersionResult",
    ):
        result = proof.get(key)
        if not isinstance(result, dict):
            continue
        exit_code = result.get("exitCode")
        if exit_code in (0, None):
            continue
        stderr = short_output(str(result.get("stderr") or ""), 280)
        stdout = short_output(str(result.get("stdout") or ""), 280)
        detail = stderr or stdout
        if detail:
            return detail
    hygiene = package_hygiene_excerpt(proof.get("packageHygieneEvidence"))
    if hygiene:
        return short_output(hygiene, 280)
    for evidence_key, status_key in (
        ("extractEvidence", "extractStatus"),
        ("previousExtractEvidence", "previousExtractStatus"),
        ("candidateExtractEvidence", "candidateExtractStatus"),
    ):
        evidence = proof.get(evidence_key)
        if evidence and proof.get(status_key) == "blocked":
            return short_output(str(evidence), 280)
    error = proof.get("error")
    if error:
        return short_output(str(error), 280)
    return ""


def blocking_next_command(proof: dict[str, Any], default: str) -> str:
    hygiene = proof.get("packageHygieneEvidence")
    if isinstance(hygiene, dict) and hygiene.get("status") in {"blocked", "review"} and hygiene.get("nextCommand"):
        return str(hygiene["nextCommand"])
    return default


def build_blocking_proof_detail(
    fresh_install_package_proof: dict[str, Any],
    upgrade_package_proof: dict[str, Any],
    rollback_package_proof: dict[str, Any],
    github_release_asset_download_proof: dict[str, Any],
    published_release_asset_proof: dict[str, Any],
    external_adoption_evidence_proof: dict[str, Any],
    security_review_evidence_proof: dict[str, Any],
) -> dict[str, Any] | None:
    candidates = [
        (
            "freshInstallPackageProof",
            fresh_install_package_proof,
            "Supplied release package failed fresh-install validation.",
            "Rebuild the release package with ./scripts/package_release.sh, verify it with ./tests/package_release_test.sh, then rerun LaunchKey against the rebuilt package or downloaded assets.",
            "./scripts/package_release.sh && ./tests/package_release_test.sh",
            "supplied release package fresh-install receipt",
        ),
        (
            "upgradePackageProof",
            upgrade_package_proof,
            "Supplied previous/candidate package pair failed same-prefix upgrade validation.",
            "Rebuild the package pair, verify package release tests, then rerun LaunchKey with --upgrade-from-tarball against the previous release tarball.",
            "./scripts/package_release.sh && ./tests/package_release_test.sh && ./tests/v4_release_candidate_test.sh",
            "same-prefix package upgrade receipt",
        ),
        (
            "rollbackPackageProof",
            rollback_package_proof,
            "Supplied release package failed rollback cleanup proof.",
            "Fix package install/uninstall cleanup so the wrapper binaries and lib/shipguard tree can be removed without leaving package state behind.",
            "./tests/v4_release_candidate_test.sh",
            "rollback cleanup receipt",
        ),
        (
            "githubReleaseAssetDownloadProof",
            github_release_asset_download_proof,
            "GitHub release asset download failed.",
            "Fix the GitHub release repo, tag, API access, or empty destination, then rerun LaunchKey with native release-asset download.",
            github_release_asset_download_proof.get(
                "nextCommand",
                "./bin/shipguard v4 release-candidate --path . --out /tmp/shipguard-v4-release-candidate --download-release-assets --github-release-repo <owner/repo> --release-version <version> --shipguard-eval --shareable",
            ),
            "GitHub release asset download receipt",
        ),
        (
            "publishedReleaseAssetProof",
            published_release_asset_proof,
            "Downloaded release assets failed consumer-side verification.",
            "Redownload the release assets, verify release-consume locally, and only reuse the assets after manifest, tarball SHA-256, replay, and attestation all pass.",
            published_release_asset_proof.get("consumeCommand", "./bin/shipguard release-consume verify --dir <downloaded-assets-dir> --out <consume-dir> --version <version>"),
            "downloaded release asset consumer receipt",
        ),
        (
            "externalAdoptionEvidenceProof",
            external_adoption_evidence_proof,
            "External adoption evidence failed the stable-v4 evidence contract.",
            "Fix or replace the adoption evidence record, then rerun LaunchKey with --external-adoption-evidence.",
            external_adoption_evidence_proof.get("nextCommand", "./bin/shipguard v4 release-candidate --path . --out /tmp/shipguard-v4-release-candidate --external-adoption-evidence <evidence-json-or-dir> --shipguard-eval --shareable"),
            "external adoption evidence receipt",
        ),
        (
            "securityReviewEvidenceProof",
            security_review_evidence_proof,
            "Security review evidence failed the stable-v4 evidence contract.",
            "Fix or replace the security review evidence record, then rerun LaunchKey with --security-review-evidence.",
            security_review_evidence_proof.get("nextCommand", "./bin/shipguard v4 release-candidate --path . --out /tmp/shipguard-v4-release-candidate --security-review-evidence <evidence-json-or-dir> --shipguard-eval --shareable"),
            "security review evidence receipt",
        ),
    ]
    for receipt, proof, headline, remedy, next_command, proof_source in candidates:
        proof_participated = bool(proof.get("provided") or proof.get("requested"))
        if not proof_participated or proof.get("status") == "pass":
            continue
        if proof.get("status") in {"not-provided", "not-requested"}:
            continue
        failure_evidence = failed_process_excerpt(proof)
        failure = proof.get("summary") or headline
        chosen_next_command = blocking_next_command(proof, next_command)
        return {
            "receipt": receipt,
            "status": proof.get("status"),
            "summary": headline,
            "failure": failure,
            "failureEvidence": failure_evidence,
            "nextAction": remedy,
            "nextCommand": chosen_next_command,
            "proofSource": proof_source,
        }
    return None


def build_report(args: argparse.Namespace) -> dict[str, Any]:
    root = Path(args.path).expanduser().resolve()
    home = Path.home().resolve()

    version = read_text(root / "VERSION").strip() or "unknown"
    bin_text = read_text(root / "bin" / "shipguard")
    cli_text = read_text(root / "docs" / "cli.md")
    matrix_text = read_text(root / "docs" / "command-matrix.md")
    rc_doc_text = read_text(root / "docs" / "v4-release-candidate.md")
    schema_doc_text = read_text(root / "docs" / "v4-schema-freeze.md")
    release_consume_doc_text = read_text(root / "docs" / "release-consume.md")
    release_proof_doc_text = read_text(root / "docs" / "release-proof.md")
    install_text = read_text(root / "scripts" / "install.sh")
    package_text = read_text(root / "scripts" / "package_release.sh")
    package_test_text = read_text(root / "tests" / "package_release_test.sh")
    gauntlet_text = read_text(root / "scripts" / "tool_value_gauntlet.py")
    report_quality_text = read_text(root / "scripts" / "ios_report_quality.py")
    self_audit_text = read_text(root / "scripts" / "self_audit.sh")
    plugin_text = read_text(root / "plugins" / "ios-shipguard" / "skills" / "ios-shipguard" / "SKILL.md")
    changelog_text = read_text(root / "CHANGELOG.md")

    fresh_install_package_proof = build_fresh_install_package_proof(args, version)
    upgrade_package_proof = build_upgrade_package_proof(args, version)
    rollback_package_proof = build_rollback_package_proof(args, version)
    github_release_asset_download_proof = build_github_release_asset_download_proof(args, version)
    published_release_asset_proof = build_published_release_asset_proof(args, root, version, github_release_asset_download_proof)
    external_adoption_evidence_proof = build_external_adoption_evidence_proof(args)
    security_review_evidence_proof = build_security_review_evidence_proof(args)

    checks: list[dict[str, Any]] = []
    add_check(
        checks,
        "release-candidate-command-routed",
        "CLI route is public",
        "release-candidate" in bin_text and TOOL in cli_text,
        ["bin/shipguard", "docs/cli.md"],
        "Route `shipguard v4 release-candidate` through the public CLI and CLI docs.",
    )
    add_check(
        checks,
        "release-candidate-contract-documented",
        "Release-candidate contract is documented",
        contains_all(
            rc_doc_text,
            [
                "fresh install",
                "upgrade",
                "uninstall",
                "release proof consumption",
                "external adoption packet",
                "plugin refresh proof",
            ],
        ),
        ["docs/v4-release-candidate.md"],
        "Document the install, upgrade, uninstall, release-consume, adoption, and plugin-refresh proof contract.",
    )
    add_check(
        checks,
        "fresh-install-proof-present",
        "Fresh install proof path is present",
        contains_all(install_text + package_test_text, ["install", "prefix"])
        and "adoptionReceipts" in gauntlet_text
        and "fresh-user adoption" in gauntlet_text,
        ["scripts/install.sh", "tests/package_release_test.sh", "scripts/tool_value_gauntlet.py"],
        "Keep a runnable fresh-package install proof so a new user can validate ShipGuard without maintainer context.",
    )
    if fresh_install_package_proof["provided"]:
        add_check(
            checks,
            "fresh-install-package-verified",
            "Supplied package tarball passes fresh install proof",
            fresh_install_package_proof["status"] == "pass",
            ["package tarball", "scripts/install.sh", "installed shipguard validate"],
            "Attach a real fresh-install receipt from the release package before using release-candidate readiness as stable-v4 evidence.",
        )
    add_check(
        checks,
        "upgrade-proof-present",
        "Upgrade proof path is present",
        "upgrade" in rc_doc_text.lower() and contains_all(package_test_text, ["package_name", "install.sh", "version"]),
        ["docs/v4-release-candidate.md", "tests/package_release_test.sh"],
        "Make the release candidate report point at concrete upgrade verification instead of only saying upgrades are supported.",
    )
    if upgrade_package_proof["provided"]:
        add_check(
            checks,
            "upgrade-package-verified",
            "Supplied previous package upgrades to the candidate package",
            upgrade_package_proof["status"] == "pass",
            ["previous release tarball", "candidate package tarball", "same-prefix upgrade", "installed shipguard validate"],
            "Attach a real upgrade receipt from a previous release package before using release-candidate readiness as stable-v4 evidence.",
        )
    add_check(
        checks,
        "uninstall-proof-present",
        "Uninstall proof path is present",
        "uninstall" in rc_doc_text.lower() and ("rm -rf" in rc_doc_text or "remove" in rc_doc_text.lower()),
        ["docs/v4-release-candidate.md"],
        "Keep uninstall proof explicit so ShipGuard does not leave hidden state as an adoption blocker.",
    )
    if rollback_package_proof["provided"]:
        add_check(
            checks,
            "rollback-package-verified",
            "Supplied package rollback cleanup proof passes",
            rollback_package_proof["status"] == "pass",
            ["candidate package tarball", "temporary install prefix", "rollback cleanup"],
            "Attach a real rollback cleanup receipt so temporary package state can be removed without hidden ShipGuard leftovers.",
        )
    add_check(
        checks,
        "release-proof-consumption-present",
        "Release proof consumption is present",
        "release-consume verify" in release_consume_doc_text and "release-proof build" in release_proof_doc_text,
        ["docs/release-consume.md", "docs/release-proof.md"],
        "Require consumer-side release proof verification before treating a release candidate as shippable.",
    )
    add_check(
        checks,
        "external-adoption-packet-present",
        "External adoption packet is present",
        contains_all(rc_doc_text, ["external adoption packet", "first command", "support boundary", "proof bundle"]),
        ["docs/v4-release-candidate.md"],
        "Give external users one packet with first command, proof bundle, support boundary, and non-claims.",
    )
    add_check(
        checks,
        "final-schema-docs-present",
        "Final schema docs are present",
        contains_all(schema_doc_text, ["compatibility policy", "migration checks", "deprecation policy"]),
        ["docs/v4-schema-freeze.md"],
        "Keep the schema freeze docs linked from release-candidate readiness so v4 does not drift after the freeze.",
    )
    add_check(
        checks,
        "plugin-refresh-proof-present",
        "Plugin refresh proof is present",
        "codex status --strict" in rc_doc_text.lower() and "codex status --strict" in plugin_text.lower(),
        ["docs/v4-release-candidate.md", "plugins/ios-shipguard/skills/ios-shipguard/SKILL.md"],
        "Make plugin refresh proof visible in the release-candidate path, including the installed Codex plugin check.",
    )
    add_check(
        checks,
        "release-candidate-gauntlet-receipts-present",
        "Value gauntlet has release-candidate receipts",
        "v4ReleaseCandidateReadinessReceipts" in gauntlet_text and "runtimeV4ReleaseCandidateReadiness" in gauntlet_text,
        ["scripts/tool_value_gauntlet.py"],
        "Add a runtime receipt family so release-candidate readiness is measured by command proof.",
    )
    add_check(
        checks,
        "release-candidate-report-quality-present",
        "Report-quality accepts release-candidate reports",
        TOOL in report_quality_text,
        ["scripts/ios_report_quality.py"],
        "Allow report-quality to score the v4 release-candidate readiness report as a root ShipGuard report.",
    )
    add_check(
        checks,
        "release-candidate-self-audit-package-present",
        "Self-audit and package proof include the surface",
        "v4 release-candidate --help" in self_audit_text
        and "tests/v4_release_candidate_test.sh" in package_test_text
        and "scripts/v4_release_candidate.py" in package_test_text,
        ["scripts/self_audit.sh", "tests/package_release_test.sh"],
        "Include the command, script, docs, test, and receipt fixture in self-audit and package proof.",
    )
    add_check(
        checks,
        "release-candidate-command-matrix-present",
        "Command matrix exposes the release-candidate surface",
        "v4 release-candidate" in matrix_text,
        ["docs/command-matrix.md"],
        "Add release-candidate readiness to the command matrix so the v4 path is discoverable.",
    )
    add_check(
        checks,
        "release-candidate-changelog-present",
        "Changelog records the readiness gate",
        contains_all(changelog_text, ["v3.131", "release-candidate", "install"]),
        ["CHANGELOG.md"],
        "Record the release-candidate readiness gate in the changelog.",
    )
    if published_release_asset_proof["provided"]:
        add_check(
            checks,
            "published-release-assets-consumed",
            "Supplied release assets pass consumer proof",
            published_release_asset_proof["status"] == "pass",
            ["release-consume verify", "consumer-report.json", "asset-digests.json"],
            "Run consumer-side release proof against downloaded assets before using release-candidate readiness as stable-v4 evidence.",
        )
    if github_release_asset_download_proof["requested"]:
        add_check(
            checks,
            "github-release-assets-downloaded",
            "GitHub release assets download natively",
            github_release_asset_download_proof["status"] == "pass",
            ["GitHub release API", "downloaded release assets directory"],
            "Let LaunchKey download release assets from GitHub before consumer proof so maintainers do not need a separate manual `gh release download` step.",
        )
    if external_adoption_evidence_proof["provided"]:
        add_check(
            checks,
            "external-adoption-evidence-validated",
            "External adoption evidence passes the evidence contract",
            external_adoption_evidence_proof["status"] == "pass",
            ["external adoption evidence records", "redaction contract", "non-claims"],
            "Attach independent public or private-redacted adoption evidence before using LaunchKey as stable-v4 release evidence.",
        )
    if security_review_evidence_proof["provided"]:
        add_check(
            checks,
            "security-review-evidence-validated",
            "Security review evidence passes the evidence contract",
            security_review_evidence_proof["status"] == "pass",
            ["security review evidence records", "required security scope", "critical/high finding summary"],
            "Attach public or private-redacted security review evidence before using LaunchKey as stable-v4 release evidence.",
        )

    required_checks = [check for check in checks if check["required"]]
    failed_required = [check for check in required_checks if check["status"] != "pass"]
    status = "pass" if not failed_required else "review"

    def route_status(check_id: str) -> str:
        return "pass" if any(check["id"] == check_id and check["status"] == "pass" for check in checks) else "review"

    def supplied_or_route_status(proof: dict[str, Any], check_id: str) -> str:
        if proof.get("provided"):
            return str(proof.get("status") or "review")
        return route_status(check_id)

    readiness_proof = {
        "freshInstall": {
            "status": supplied_or_route_status(fresh_install_package_proof, "fresh-install-proof-present"),
            "commands": [
                "./scripts/package_release.sh",
                "tar -tzf <release-tarball>",
                "<package>/scripts/install.sh --prefix <tmp-prefix>",
                "<tmp-prefix>/bin/shipguard validate <package>",
            ],
            "packageProofStatus": fresh_install_package_proof["status"],
        },
        "upgrade": {
            "status": supplied_or_route_status(upgrade_package_proof, "upgrade-proof-present"),
            "commands": [
                "shipguard version",
                "./scripts/install.sh --prefix <existing-prefix>",
                "<existing-prefix>/bin/shipguard version",
            ],
            "packageProofStatus": upgrade_package_proof["status"],
        },
        "uninstall": {
            "status": supplied_or_route_status(rollback_package_proof, "uninstall-proof-present"),
            "commands": [
                "rm -rf <tmp-prefix>",
                "test ! -e <tmp-prefix>/bin/shipguard",
            ],
            "rollbackPackageProofStatus": rollback_package_proof["status"],
        },
        "releaseProofConsumption": {
            "status": supplied_or_route_status(published_release_asset_proof, "release-proof-consumption-present"),
            "commands": [
                "./bin/shipguard release-proof build --out <proof-dir> --release-url <url> --version <version> --tag <tag> --commit <sha> --ci-run-url <url>",
                "./bin/shipguard release-consume verify --dir <downloaded-assets-dir> --out <consume-dir> --version <version>",
            ],
            "publishedReleaseAssetProofStatus": published_release_asset_proof["status"],
        },
        "externalAdoptionPacket": {
            "status": route_status("external-adoption-packet-present"),
            "artifacts": ["README.md", "docs/v4-release-candidate.md", "docs/cli.md", "release proof bundle"],
        },
        "finalSchemaDocs": {
            "status": route_status("final-schema-docs-present"),
            "artifacts": ["docs/v4-schema-freeze.md", "docs/compatibility.md"],
        },
        "pluginRefreshProof": {
            "status": route_status("plugin-refresh-proof-present"),
            "commands": [
                "codex plugin marketplace add .",
                "codex plugin add ios-shipguard@shipguard",
                "./bin/shipguard codex status --strict",
            ],
        },
    }
    release_readiness = {
        "currentVersion": version,
        "targetVersion": "4.0.0",
        "productStage": "v4-release-candidate-readiness",
        "releaseClaim": "candidate-ready" if status == "pass" else "not-ready",
        "stableV4Release": False,
        "freshInstallPackageProof": fresh_install_package_proof["status"],
        "freshInstallPackageProofRequiredForStableV4": True,
        "upgradePackageProof": upgrade_package_proof["status"],
        "upgradePackageProofRequiredForStableV4": True,
        "rollbackPackageProof": rollback_package_proof["status"],
        "rollbackPackageProofRequiredForStableV4": True,
        "publishedReleaseAssetProof": published_release_asset_proof["status"],
        "githubReleaseAssetDownloadProof": github_release_asset_download_proof["status"],
        "externalAdoptionEvidenceProof": external_adoption_evidence_proof["status"],
        "externalAdoptionEvidenceStableGate": external_adoption_evidence_proof["stableV4GateStatus"],
        "externalAdoptionEvidenceRequiredForStableV4": True,
        "securityReviewEvidenceProof": security_review_evidence_proof["status"],
        "securityReviewEvidenceStableGate": security_review_evidence_proof["stableV4GateStatus"],
        "securityReviewEvidenceRequiredForStableV4": True,
        "publishedReleaseAssetsRequiredForStableV4": True,
        "requiredProofCommands": [
            "git diff --check",
            "./tests/v4_release_candidate_test.sh",
            "./tests/tool_value_gauntlet_test.sh",
            "./bin/shipguard validate",
            "./bin/shipguard docs-check . --out /tmp/shipguard-docs-check",
            "./tests/self_audit_test.sh",
            "./tests/cli_smoke_test.sh",
            "./tests/package_release_test.sh",
            "codex plugin marketplace add .",
            "codex plugin add ios-shipguard@shipguard",
            "./bin/shipguard codex status --strict",
            "./bin/shipguard v4 release-candidate --path . --out <candidate-dir> --package-tarball <release-tarball> --shipguard-eval --shareable",
            "./bin/shipguard v4 release-candidate --path . --out <candidate-dir> --package-tarball <release-tarball> --upgrade-from-tarball <previous-release-tarball> --shipguard-eval --shareable",
            "./bin/shipguard v4 release-candidate --path . --out <candidate-dir> --download-release-assets --github-release-repo <owner/repo> --release-version <version> --shipguard-eval --shareable",
            "./bin/shipguard release-consume verify --dir <downloaded-assets-dir> --out <consume-dir> --version <version>",
            "./bin/shipguard v4 release-candidate --path . --out <candidate-dir> --external-adoption-evidence <evidence-json-or-dir> --shipguard-eval --shareable",
            "./bin/shipguard v4 release-candidate --path . --out <candidate-dir> --security-review-evidence <evidence-json-or-dir> --shipguard-eval --shareable",
        ],
    }
    external_adoption_packet = {
        "firstCommand": "./bin/shipguard full-audit --path . --out /tmp/shipguard-full-audit --profile quick --shipguard-eval --shareable",
        "supportBoundary": "ShipGuard gives an external developer local proof and report-quality checks; it does not run private app remediation unless explicitly asked.",
        "proofBundle": ["release manifest", "release index", "release replay", "release consume report", "self-audit report"],
        "nonClaims": [
            "No OpenAI marketplace acceptance is claimed.",
            "No third-party adoption is claimed by this local readiness report.",
            "No private app validation is part of this ShipGuard product QA run.",
        ],
    }
    blocked_claims = [
        "This proves release-candidate readiness, not a stable v4 product release.",
        "Marketplace acceptance, broad external adoption, and third-party security certification remain outside this local report.",
        "Private Ringly or Ilmify app validation is not part of this report.",
        "Physical-device iOS proof is not implied by package, docs, or local fixture proof.",
    ]
    scope_boundary = {
        "shipguardOnly": True,
        "targetAppsReadOnly": True,
        "privateAppsUsed": False,
        "doesNotEditTargetApps": True,
        "doesNotPush": True,
        "doesNotPublishRelease": True,
        "shareable": bool(args.shareable),
    }
    package_receipts_pass = (
        fresh_install_package_proof["status"] == "pass"
        and upgrade_package_proof["status"] == "pass"
        and rollback_package_proof["status"] == "pass"
    )
    report_quality_questions = []
    if not package_receipts_pass:
        report_quality_questions.append(
            "Can a fresh user install, upgrade, uninstall, and validate ShipGuard from the release package without maintainer context?"
        )
    if published_release_asset_proof["status"] != "pass":
        report_quality_questions.append(
            "Can a consumer download release assets and independently verify the manifest, tarball SHA-256, replay, and attestation?"
        )
    if external_adoption_evidence_proof.get("stableV4GateStatus") != "pass":
        report_quality_questions.append(
            "Which independent external adoption evidence can be attached without faking adoption, leaking private data, or claiming stable v4 too early?"
        )
    if security_review_evidence_proof.get("stableV4GateStatus") != "pass":
        report_quality_questions.append(
            "Which final security review evidence can be attached without leaking private data, hiding critical/high findings, or claiming stable v4 too early?"
        )
    report_quality_questions.extend(
        [
            "Does the adoption packet tell an external developer the first command, proof bundle, support boundary, and non-claims?",
            "What stable v4 product release proof remains after release-candidate readiness passes?",
        ]
    )
    blocking_proof = build_blocking_proof_detail(
        fresh_install_package_proof,
        upgrade_package_proof,
        rollback_package_proof,
        github_release_asset_download_proof,
        published_release_asset_proof,
        external_adoption_evidence_proof,
        security_review_evidence_proof,
    )
    if status != "pass" and blocking_proof:
        evidence_sentence = (
            f" Failure evidence: {blocking_proof['failureEvidence']}"
            if blocking_proof.get("failureEvidence")
            else ""
        )
        priority_action = f"{blocking_proof['nextAction']}{evidence_sentence}"
        next_command = str(blocking_proof["nextCommand"])
        summary = f"{blocking_proof['summary']} {blocking_proof['failure']}"
        proof_source = str(blocking_proof["proofSource"])
    elif status == "pass" and fresh_install_package_proof["status"] == "not-provided":
        priority_action = (
            "Attach a real fresh-install receipt from the release package before any stable v4 claim; "
            "downloaded release-asset proof, external adoption evidence, final security review, rollback proof, and release proof consumption still remain stabilization gates."
        )
        next_command = fresh_install_package_proof["nextCommand"]
        summary = (
            "ShipGuard has release-candidate readiness proof, but no release package tarball was supplied for a fresh-install receipt."
        )
        proof_source = "v4 release-candidate checks plus documented package install boundary; fresh install package proof not supplied"
    elif status == "pass" and upgrade_package_proof["status"] == "not-provided":
        priority_action = (
            "Attach an upgrade receipt from a previous release package to the candidate package before any stable v4 claim; "
            "downloaded release-asset proof, external adoption evidence, final security review, and release proof consumption still remain stabilization gates."
        )
        next_command = upgrade_package_proof["nextCommand"]
        summary = (
            "ShipGuard has release-candidate readiness proof and supplied package fresh-install proof, but no previous release tarball was supplied for upgrade proof."
        )
        proof_source = "v4 release-candidate checks plus fresh-install package receipt; upgrade package proof not supplied"
    elif status == "pass" and rollback_package_proof["status"] == "not-provided":
        priority_action = (
            "Attach rollback cleanup proof from the release package before any stable v4 claim; "
            "downloaded release-asset proof, external adoption evidence, final security review, and release proof consumption still remain stabilization gates."
        )
        next_command = rollback_package_proof["nextCommand"]
        summary = (
            "ShipGuard has release-candidate readiness proof, but no release package tarball was supplied for rollback cleanup proof."
        )
        proof_source = "v4 release-candidate checks plus documented rollback boundary; rollback package proof not supplied"
    elif status == "pass" and published_release_asset_proof["status"] == "not-provided":
        priority_action = (
            "Attach downloaded release assets to the v4 product release candidate before any stable v4 claim; "
            "external adoption evidence, final security review, package proof, rollback proof, and release proof consumption still remain stabilization gates."
        )
        next_command = published_release_asset_proof["nextCommand"]
        summary = (
            "ShipGuard has release-candidate readiness proof, but no downloaded release assets were supplied for consumer-side stable-v4 proof."
        )
        proof_source = "v4 release-candidate checks plus documented release-consume boundary; published asset proof not supplied"
    elif status == "pass" and external_adoption_evidence_proof["stableV4GateStatus"] != "pass":
        if external_adoption_evidence_proof["status"] == "not-provided":
            priority_action = (
                "Attach independent external adoption evidence before any stable v4 claim; final security review remains a separate stabilization gate."
            )
            summary = (
                "ShipGuard has release-candidate readiness proof and supplied package/release-asset proof, but no external adoption evidence was supplied."
            )
        else:
            priority_action = (
                "Replace the supplied adoption evidence with real public-external or private-redacted-external independent evidence before any stable v4 claim; final security review remains a separate stabilization gate."
            )
            summary = (
                "ShipGuard has structurally valid adoption evidence, but it is not stable-v4 eligible independent evidence."
            )
        next_command = external_adoption_evidence_proof["nextCommand"]
        proof_source = "v4 release-candidate checks plus package/release-asset receipts; external adoption evidence stable gate not satisfied"
    elif status == "pass" and security_review_evidence_proof["stableV4GateStatus"] != "pass":
        if security_review_evidence_proof["status"] == "not-provided":
            priority_action = (
                "Attach final security review evidence before any stable v4 claim; the evidence must cover CLI, plugin, GitHub Actions, release proof, package install, and redaction/privacy surfaces."
            )
            summary = (
                "ShipGuard has release-candidate readiness proof and supplied package/release-asset/adoption proof, but no final security review evidence was supplied."
            )
        else:
            priority_action = (
                "Replace the supplied security review evidence with real public-security-review or private-redacted-security-review evidence before any stable v4 claim."
            )
            summary = (
                "ShipGuard has structurally valid security review evidence, but it is not stable-v4 eligible final security review evidence."
            )
        next_command = security_review_evidence_proof["nextCommand"]
        proof_source = "v4 release-candidate checks plus package/release-asset/adoption receipts; security review evidence stable gate not satisfied"
    elif status == "pass":
        priority_action = (
            "Use the passing fresh-install, upgrade, rollback, release-asset, external-adoption, and security-review receipts as v4 stabilization inputs, then prepare the final stable-v4 release proof packet."
        )
        next_command = (
            "./bin/shipguard full-audit --path . --out /tmp/shipguard-full-audit --profile release "
            "--include-install --release-url <release-url> --version <version> --tag <tag> "
            "--commit <commit-sha> --ci-run-url <ci-run-url> --shipguard-eval --shareable"
        )
        summary = "ShipGuard has release-candidate readiness proof, supplied package tarball passed fresh-install and rollback proof, supplied previous package upgraded to the candidate, supplied release assets passed consumer-side verification, external adoption evidence passed the stable gate, and security review evidence passed the stable gate."
        proof_source = "v4 release-candidate checks plus fresh-install package receipt, upgrade receipt, rollback receipt, release-consume consumer-report, asset digest matrix, external adoption evidence receipt, and security review evidence receipt"
    else:
        priority_action = "Complete the missing release-candidate readiness checks before calling v4 candidate-ready."
        next_command = "./tests/v4_release_candidate_test.sh"
        summary = "ShipGuard v4 release-candidate readiness still has missing proof."
        proof_source = "v4 release-candidate checks, value-gauntlet receipts, docs, package proof hooks, and release-consume boundaries"
    result_ux = build_result_ux(
        status=status,
        summary=summary,
        proof_source=proof_source,
        why_it_matters="This removes manual interpretation from the v4 gate: a release candidate must be installable, consumable, and externally understandable.",
        next_command=next_command,
        next_action_summary=priority_action,
    )
    result_ux["priorityAction"] = priority_action
    if blocking_proof:
        result_ux["blockingProof"] = blocking_proof

    report: dict[str, Any] = {
        "schemaVersion": SCHEMA_VERSION,
        "generatedAt": utc_now(),
        "tool": TOOL,
        "surface": SURFACE,
        "version": version,
        "repo": root.as_posix(),
        "status": status,
        "productStage": "v4-release-candidate-readiness",
        "checks": checks,
        "readinessProof": readiness_proof,
        "installProof": readiness_proof["freshInstall"],
        "freshInstallPackageProof": fresh_install_package_proof,
        "upgradeProof": readiness_proof["upgrade"],
        "upgradePackageProof": upgrade_package_proof,
        "uninstallProof": readiness_proof["uninstall"],
        "rollbackPackageProof": rollback_package_proof,
        "releaseProofConsumption": readiness_proof["releaseProofConsumption"],
        "githubReleaseAssetDownloadProof": github_release_asset_download_proof,
        "publishedReleaseAssetProof": published_release_asset_proof,
        "externalAdoptionPacket": external_adoption_packet,
        "externalAdoptionEvidenceProof": external_adoption_evidence_proof,
        "securityReviewEvidenceProof": security_review_evidence_proof,
        "finalSchemaDocs": readiness_proof["finalSchemaDocs"],
        "pluginRefreshProof": readiness_proof["pluginRefreshProof"],
        "releaseReadiness": release_readiness,
        "blockedClaims": blocked_claims,
        "blockingProof": blocking_proof,
        "scopeBoundary": scope_boundary,
        "reportQualityQuestions": report_quality_questions,
        "resultUX": result_ux,
    }
    if args.shipguard_eval:
        report["shipguardEval"] = {
            "mode": "ShipGuard product QA",
            "allowedInput": "ShipGuard source tree and public fixtures",
            "forbiddenOutput": "Private target-app edits, unproven stable-v4 release claims, or marketplace acceptance claims",
            "nextImprovement": priority_action,
        }
    if args.shareable:
        replacements = {
            root.as_posix(): "<repo>",
            home.as_posix(): "<home>",
        }
        if github_release_asset_download_proof.get("downloadDir"):
            replacements[str(github_release_asset_download_proof["downloadDir"])] = "<downloaded-release-assets>"
        if published_release_asset_proof.get("assetsDir"):
            assets_replacement = (
                "<downloaded-release-assets>"
                if published_release_asset_proof.get("downloadSource") == "github-release-assets"
                else "<release-assets>"
            )
            replacements[str(published_release_asset_proof["assetsDir"])] = assets_replacement
        if published_release_asset_proof.get("consumeOut"):
            replacements[str(published_release_asset_proof["consumeOut"])] = "<release-consume-out>"
        if github_release_asset_download_proof.get("apiUrl") and str(github_release_asset_download_proof["apiUrl"]).startswith("file:"):
            replacements[str(github_release_asset_download_proof["apiUrl"])] = "<github-api-url>"
        if github_release_asset_download_proof.get("releaseEndpoint") and str(github_release_asset_download_proof["releaseEndpoint"]).startswith("file:"):
            replacements[str(github_release_asset_download_proof["releaseEndpoint"])] = "<github-release-endpoint>"
        for asset in github_release_asset_download_proof.get("downloadedAssets", []):
            if isinstance(asset, dict):
                if asset.get("path"):
                    replacements[str(asset["path"])] = "<downloaded-release-assets>/" + Path(str(asset.get("path"))).name
                if asset.get("source") and str(asset["source"]).startswith("file:"):
                    replacements[str(asset["source"])] = "<github-asset-url>/" + str(asset.get("name") or "asset")
        if fresh_install_package_proof.get("packageTarball"):
            replacements[str(fresh_install_package_proof["packageTarball"])] = "<package-tarball>"
        if fresh_install_package_proof.get("installPrefix"):
            replacements[str(fresh_install_package_proof["installPrefix"])] = "<fresh-install-prefix>"
        if fresh_install_package_proof.get("workDir"):
            replacements[str(fresh_install_package_proof["workDir"])] = "<fresh-install-work-dir>"
        if fresh_install_package_proof.get("packageRoot"):
            replacements[str(fresh_install_package_proof["packageRoot"])] = "<fresh-install-package-root>"
        if fresh_install_package_proof.get("installedRoot"):
            replacements[str(fresh_install_package_proof["installedRoot"])] = "<fresh-install-root>"
        if upgrade_package_proof.get("previousTarball"):
            replacements[str(upgrade_package_proof["previousTarball"])] = "<previous-package-tarball>"
        if upgrade_package_proof.get("candidateTarball"):
            replacements[str(upgrade_package_proof["candidateTarball"])] = "<package-tarball>"
        if upgrade_package_proof.get("upgradePrefix"):
            replacements[str(upgrade_package_proof["upgradePrefix"])] = "<upgrade-prefix>"
        if upgrade_package_proof.get("workDir"):
            replacements[str(upgrade_package_proof["workDir"])] = "<upgrade-work-dir>"
        if upgrade_package_proof.get("previousPackageRoot"):
            replacements[str(upgrade_package_proof["previousPackageRoot"])] = "<previous-package-root>"
        if upgrade_package_proof.get("candidatePackageRoot"):
            replacements[str(upgrade_package_proof["candidatePackageRoot"])] = "<candidate-package-root>"
        if upgrade_package_proof.get("installedRoot"):
            replacements[str(upgrade_package_proof["installedRoot"])] = "<upgrade-installed-root>"
        if rollback_package_proof.get("packageTarball"):
            replacements[str(rollback_package_proof["packageTarball"])] = "<package-tarball>"
        if rollback_package_proof.get("rollbackPrefix"):
            replacements[str(rollback_package_proof["rollbackPrefix"])] = "<rollback-prefix>"
        if rollback_package_proof.get("workDir"):
            replacements[str(rollback_package_proof["workDir"])] = "<rollback-work-dir>"
        if rollback_package_proof.get("packageRoot"):
            replacements[str(rollback_package_proof["packageRoot"])] = "<rollback-package-root>"
        if rollback_package_proof.get("installedRoot"):
            replacements[str(rollback_package_proof["installedRoot"])] = "<rollback-installed-root>"
        for evidence_input in external_adoption_evidence_proof.get("evidenceInputs", []):
            replacements[str(evidence_input)] = "<external-adoption-evidence>"
        for record in external_adoption_evidence_proof.get("records", []):
            if isinstance(record, dict) and record.get("path"):
                replacements[str(record["path"])] = "<external-adoption-evidence>/" + Path(str(record["path"])).name
        for evidence_input in security_review_evidence_proof.get("evidenceInputs", []):
            replacements[str(evidence_input)] = "<security-review-evidence>"
        for record in security_review_evidence_proof.get("records", []):
            if isinstance(record, dict) and record.get("path"):
                replacements[str(record["path"])] = "<security-review-evidence>/" + Path(str(record["path"])).name
        report = scrub_value(report, replacements)
    return report


def append_package_hygiene_markdown(lines: list[str], proof: dict[str, Any]) -> None:
    hygiene = proof.get("packageHygieneEvidence")
    if not isinstance(hygiene, dict):
        return
    lines.append(f"- Package hygiene status: `{hygiene.get('status')}`")
    lines.append(
        f"- Package hygiene findings: `{hygiene.get('blockedFindingCount', 0)}` blocked, `{hygiene.get('reviewFindingCount', 0)}` review"
    )
    affected = ", ".join(hygiene.get("affectedVersions") or [])
    if affected:
        lines.append(f"- Package hygiene affected versions: {affected}")
    first = hygiene.get("firstFinding")
    if isinstance(first, dict):
        lines.append(
            f"- First package hygiene finding: `{first.get('ruleId')}` in `{first.get('tarball')}` at `{first.get('member') or 'n/a'}`: {first.get('evidence')}"
        )
    if hygiene.get("nextCommand"):
        lines.append(f"- Package hygiene command: `{hygiene.get('nextCommand')}`")


def render_markdown(report: dict[str, Any]) -> str:
    lines: list[str] = [
        "# ShipGuard V4 Release Candidate Readiness",
        "",
        f"- Status: `{report['status']}`",
        f"- Product stage: `{report['productStage']}`",
        f"- Release claim: `{report['releaseReadiness']['releaseClaim']}`",
        f"- Stable v4 release: `{report['releaseReadiness']['stableV4Release']}`",
        f"- Version inspected: `{report['version']}`",
        "",
        *render_result_markdown(report["resultUX"]),
        "## Readiness Proof",
        "",
    ]
    blocking_proof = report.get("blockingProof")
    if blocking_proof:
        lines.extend(
            [
                "## Blocking Proof",
                "",
                f"- Receipt: `{blocking_proof.get('receipt')}`",
                f"- Status: `{blocking_proof.get('status')}`",
                f"- Failure: {blocking_proof.get('failure')}",
            ]
        )
        if blocking_proof.get("failureEvidence"):
            lines.append(f"- Failure evidence: `{blocking_proof.get('failureEvidence')}`")
        lines.append(f"- Next command: `{blocking_proof.get('nextCommand')}`")
        lines.append(f"- Next action: {blocking_proof.get('nextAction')}")
        lines.append("")
    for key, proof in report["readinessProof"].items():
        title = key[0].upper() + key[1:]
        lines.append(f"- {title}: `{proof.get('status')}`")
    lines.extend(["", "## Fresh Install", ""])
    for command in report["installProof"].get("commands", []):
        lines.append(f"- `{command}`")
    proof = report["freshInstallPackageProof"]
    lines.extend(["", "## Fresh Install Package Proof", ""])
    lines.append(f"- Status: `{proof.get('status')}`")
    lines.append(f"- Required for stable v4: `{proof.get('requiredForStableV4')}`")
    lines.append(f"- Summary: {proof.get('summary')}")
    if proof.get("provided"):
        lines.append(f"- Installed version: `{proof.get('installedVersion')}`")
        lines.append(f"- Legacy alias version: `{proof.get('installedLegacyVersion')}`")
        lines.append(f"- Forbidden installed paths: `{proof.get('forbiddenInstalledPathCount')}`")
        if proof.get("packageTarball"):
            lines.append(f"- Package tarball: `{proof.get('packageTarball')}`")
        if proof.get("installPrefix"):
            lines.append(f"- Install prefix: `{proof.get('installPrefix')}`")
        append_package_hygiene_markdown(lines, proof)
        attachment = proof.get("freshInstallProofAttachment") if isinstance(proof.get("freshInstallProofAttachment"), dict) else {}
        if attachment:
            lines.extend(["", "### Fresh Install Proof Attachment", ""])
            lines.append(f"- Status: `{attachment.get('status')}`")
            lines.append(f"- Package tarball: `{attachment.get('packageTarball') or 'missing'}`")
            lines.append(f"- Install prefix: `{attachment.get('installPrefix') or 'missing'}`")
            lines.append(f"- Installed version: `{attachment.get('installedVersion') or 'missing'}`")
            lines.append(f"- Validation exit code: `{attachment.get('validateExitCode')}`")
            lines.append(f"- Forbidden installed paths: `{attachment.get('forbiddenInstalledPathCount')}`")
            lines.append(f"- Missing proof artifacts: `{', '.join(attachment.get('missingProofArtifacts') or []) or 'none'}`")
    else:
        lines.append(f"- Next command: `{proof.get('nextCommand')}`")
    lines.extend(["", "## Upgrade", ""])
    for command in report["upgradeProof"].get("commands", []):
        lines.append(f"- `{command}`")
    proof = report["upgradePackageProof"]
    lines.extend(["", "## Upgrade Package Proof", ""])
    lines.append(f"- Status: `{proof.get('status')}`")
    lines.append(f"- Required for stable v4: `{proof.get('requiredForStableV4')}`")
    lines.append(f"- Summary: {proof.get('summary')}")
    if proof.get("provided"):
        lines.append(f"- Previous installed version: `{proof.get('previousInstalledVersion')}`")
        lines.append(f"- Upgraded version: `{proof.get('upgradedVersion')}`")
        lines.append(f"- Forbidden installed paths: `{proof.get('forbiddenInstalledPathCount')}`")
        if proof.get("previousTarball"):
            lines.append(f"- Previous package tarball: `{proof.get('previousTarball')}`")
        if proof.get("candidateTarball"):
            lines.append(f"- Candidate package tarball: `{proof.get('candidateTarball')}`")
        if proof.get("upgradePrefix"):
            lines.append(f"- Upgrade prefix: `{proof.get('upgradePrefix')}`")
        append_package_hygiene_markdown(lines, proof)
        attachment = proof.get("upgradeProofAttachment") if isinstance(proof.get("upgradeProofAttachment"), dict) else {}
        if attachment:
            lines.extend(["", "### Upgrade Proof Attachment", ""])
            lines.append(f"- Status: `{attachment.get('status')}`")
            lines.append(f"- Previous package version: `{attachment.get('previousPackageVersion') or 'missing'}`")
            lines.append(f"- Upgraded version: `{attachment.get('upgradedVersion') or 'missing'}`")
            lines.append(f"- Validation exit code: `{attachment.get('validateExitCode')}`")
            lines.append(f"- Forbidden installed paths: `{attachment.get('forbiddenInstalledPathCount')}`")
            lines.append(f"- Missing proof artifacts: `{', '.join(attachment.get('missingProofArtifacts') or []) or 'none'}`")
    else:
        lines.append(f"- Next command: `{proof.get('nextCommand')}`")
    lines.extend(["", "## Uninstall", ""])
    for command in report["uninstallProof"].get("commands", []):
        lines.append(f"- `{command}`")
    proof = report["rollbackPackageProof"]
    lines.extend(["", "## Rollback Package Proof", ""])
    lines.append(f"- Status: `{proof.get('status')}`")
    lines.append(f"- Required for stable v4: `{proof.get('requiredForStableV4')}`")
    lines.append(f"- Summary: {proof.get('summary')}")
    if proof.get("provided"):
        lines.append(f"- Installed version: `{proof.get('installedVersion')}`")
        lines.append(f"- Removed paths: `{proof.get('removedPathCount')}`")
        lines.append(f"- Remaining paths: `{proof.get('remainingPathCount')}`")
        if proof.get("rollbackPrefix"):
            lines.append(f"- Rollback prefix: `{proof.get('rollbackPrefix')}`")
        append_package_hygiene_markdown(lines, proof)
        attachment = proof.get("rollbackProofAttachment") if isinstance(proof.get("rollbackProofAttachment"), dict) else {}
        if attachment:
            lines.extend(["", "### Rollback Proof Attachment", ""])
            lines.append(f"- Status: `{attachment.get('status')}`")
            lines.append(f"- Installed version: `{attachment.get('installedVersion') or 'missing'}`")
            lines.append(f"- Version exit code: `{attachment.get('versionExitCode')}`")
            lines.append(f"- Removed paths: `{attachment.get('removedPathCount')}`")
            lines.append(f"- Remaining paths: `{attachment.get('remainingPathCount')}`")
            lines.append(f"- Missing proof artifacts: `{', '.join(attachment.get('missingProofArtifacts') or []) or 'none'}`")
    else:
        lines.append(f"- Next command: `{proof.get('nextCommand')}`")
    lines.extend(["", "## Release Proof Consumption", ""])
    for command in report["releaseProofConsumption"].get("commands", []):
        lines.append(f"- `{command}`")
    proof = report["githubReleaseAssetDownloadProof"]
    lines.extend(["", "## GitHub Release Asset Download", ""])
    lines.append(f"- Status: `{proof.get('status')}`")
    lines.append(f"- Requested: `{proof.get('requested')}`")
    lines.append(f"- Summary: {proof.get('summary')}")
    if proof.get("requested"):
        lines.append(f"- Repository: `{proof.get('repo')}`")
        lines.append(f"- Tag: `{proof.get('tag')}`")
        lines.append(f"- Asset count: `{proof.get('assetCount')}`")
        if proof.get("downloadDir"):
            lines.append(f"- Download directory: `{proof.get('downloadDir')}`")
        attachment = proof.get("downloadProofAttachment") if isinstance(proof.get("downloadProofAttachment"), dict) else {}
        if attachment:
            asset_names = attachment.get("downloadedAssetNames") if isinstance(attachment.get("downloadedAssetNames"), list) else []
            lines.extend(["", "### Download Proof Attachment", ""])
            lines.append(f"- Status: `{attachment.get('status')}`")
            lines.append(f"- Repository: `{attachment.get('repo') or 'missing'}`")
            lines.append(f"- Tag: `{attachment.get('tag') or 'missing'}`")
            lines.append(f"- Release endpoint: `{attachment.get('releaseEndpoint') or 'missing'}`")
            lines.append(f"- Download dir: `{attachment.get('downloadDir') or 'missing'}`")
            lines.append(f"- Downloaded assets: `{', '.join(str(name) for name in asset_names) or 'none'}`")
            lines.append(f"- Asset digest rows: `{len(attachment.get('downloadedAssetDigests') or [])}`")
            lines.append(f"- Next command: `{attachment.get('nextCommand')}`")
        blocking = proof.get("downloadBlockingProof") if isinstance(proof.get("downloadBlockingProof"), dict) else {}
        if blocking:
            lines.extend(["", "### Download Blocking Proof", ""])
            lines.append(f"- Status: `{blocking.get('status')}`")
            lines.append(f"- Repository: `{blocking.get('repo') or 'missing'}`")
            lines.append(f"- Tag: `{blocking.get('tag') or 'missing'}`")
            lines.append(f"- Release endpoint: `{blocking.get('releaseEndpoint') or 'missing'}`")
            lines.append(f"- Download dir: `{blocking.get('downloadDir') or 'missing'}`")
            lines.append(f"- Error: `{blocking.get('error') or 'missing'}`")
            lines.append(f"- Next command: `{blocking.get('nextCommand')}`")
    else:
        lines.append(f"- Next command: `{proof.get('nextCommand')}`")
    proof = report["publishedReleaseAssetProof"]
    lines.extend(["", "## Published Release Asset Proof", ""])
    lines.append(f"- Status: `{proof.get('status')}`")
    lines.append(f"- Required for stable v4: `{proof.get('requiredForStableV4')}`")
    lines.append(f"- Summary: {proof.get('summary')}")
    if proof.get("provided"):
        lines.append(f"- Version: `{proof.get('version')}`")
        lines.append(f"- Consumer report status: `{proof.get('consumerReportStatus')}`")
        lines.append(f"- Replay status: `{proof.get('replayStatus')}`")
        lines.append(f"- Attestation status: `{proof.get('attestationStatus')}`")
        if proof.get("artifactSha256"):
            lines.append(f"- Artifact SHA-256: `{proof.get('artifactSha256')}`")
        attachment = proof.get("releaseAssetProofAttachment") if isinstance(proof.get("releaseAssetProofAttachment"), dict) else {}
        if attachment:
            lines.extend(["", "### Release Asset Proof Attachment", ""])
            lines.append(f"- Status: `{attachment.get('status')}`")
            lines.append(f"- Download source: `{attachment.get('downloadSource')}`")
            lines.append(f"- Consumer report: `{attachment.get('consumerReportPath') or 'missing'}`")
            lines.append(f"- Asset digest matrix: `{attachment.get('assetDigestMatrixPath') or 'missing'}`")
            lines.append(f"- Missing proof artifacts: `{', '.join(attachment.get('missingProofArtifacts') or []) or 'none'}`")
    else:
        lines.append(f"- Next command: `{proof.get('nextCommand')}`")
    lines.extend(["", "## External Adoption Packet", ""])
    packet = report["externalAdoptionPacket"]
    lines.append(f"- First command: `{packet['firstCommand']}`")
    lines.append(f"- Support boundary: {packet['supportBoundary']}")
    lines.append(f"- Proof bundle: {', '.join(packet['proofBundle'])}")
    for claim in packet["nonClaims"]:
        lines.append(f"- {claim}")
    proof = report["externalAdoptionEvidenceProof"]
    lines.extend(["", "## External Adoption Evidence", ""])
    lines.append(f"- Status: `{proof.get('status')}`")
    lines.append(f"- Stable v4 gate: `{proof.get('stableV4GateStatus')}`")
    lines.append(f"- Required for stable v4: `{proof.get('requiredForStableV4')}`")
    lines.append(f"- Summary: {proof.get('summary')}")
    if proof.get("provided"):
        lines.append(f"- Evidence records: `{proof.get('evidenceRecordCount')}`")
        lines.append(f"- Valid records: `{proof.get('validRecordCount')}`")
        lines.append(f"- Stable-v4 eligible records: `{proof.get('stableV4EligibleEvidenceCount')}`")
    else:
        lines.append(f"- Next command: `{proof.get('nextCommand')}`")
    proof = report["securityReviewEvidenceProof"]
    lines.extend(["", "## Security Review Evidence", ""])
    lines.append(f"- Status: `{proof.get('status')}`")
    lines.append(f"- Stable v4 gate: `{proof.get('stableV4GateStatus')}`")
    lines.append(f"- Required for stable v4: `{proof.get('requiredForStableV4')}`")
    lines.append(f"- Summary: {proof.get('summary')}")
    lines.append(f"- Required scope: `{', '.join(proof.get('requiredScope', []))}`")
    if proof.get("provided"):
        lines.append(f"- Evidence records: `{proof.get('evidenceRecordCount')}`")
        lines.append(f"- Valid records: `{proof.get('validRecordCount')}`")
        lines.append(f"- Stable-v4 eligible records: `{proof.get('stableV4EligibleEvidenceCount')}`")
    else:
        lines.append(f"- Next command: `{proof.get('nextCommand')}`")
    lines.extend(["", "## Plugin Refresh Proof", ""])
    for command in report["pluginRefreshProof"].get("commands", []):
        lines.append(f"- `{command}`")
    lines.extend(["", "## Release Readiness", ""])
    for command in report["releaseReadiness"]["requiredProofCommands"]:
        lines.append(f"- `{command}`")
    lines.extend(["", "## Blocked Claims", ""])
    for claim in report["blockedClaims"]:
        lines.append(f"- {claim}")
    lines.extend(["", "## Checks", ""])
    for check in report["checks"]:
        marker = "pass" if check["status"] == "pass" else "review"
        lines.append(f"- `{marker}` {check['title']}: {check['recommendation']}")
    lines.extend(["", "## Report Quality Questions", ""])
    for question in report["reportQualityQuestions"]:
        lines.append(f"- {question}")
    if "shipguardEval" in report:
        lines.extend(
            [
                "",
                "## Scope Boundary",
                "",
                "- This is ShipGuard product QA, not a target-app remediation task.",
                "- Release-candidate readiness can pass while stable v4 product release remains blocked.",
                "- Shareable reports must not include private app source, local paths, screenshots, or tokens.",
            ]
        )
    lines.append("")
    return "\n".join(lines)


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate ShipGuard v4 release-candidate readiness reports.")
    parser.add_argument("--path", default=".", help="ShipGuard repository path. Defaults to current directory.")
    parser.add_argument("--out", required=True, help="Output directory for v4-release-candidate reports.")
    parser.add_argument("--package-tarball", help="Optional release package tarball to verify with a fresh install.")
    parser.add_argument("--fresh-install-prefix", help="Optional empty install prefix for --package-tarball proof. Defaults under --out.")
    parser.add_argument("--fresh-install-work-dir", help="Optional extraction/work directory for --package-tarball proof. Defaults under --out.")
    parser.add_argument("--upgrade-from-tarball", help="Optional previous release package tarball to install before upgrading to --package-tarball.")
    parser.add_argument("--upgrade-prefix", help="Optional empty install prefix for --upgrade-from-tarball proof. Defaults under --out.")
    parser.add_argument("--upgrade-work-dir", help="Optional extraction/work directory for upgrade proof. Defaults under --out.")
    parser.add_argument("--rollback-prefix", help="Optional empty install prefix for rollback cleanup proof. Defaults under --out.")
    parser.add_argument("--rollback-work-dir", help="Optional extraction/work directory for rollback cleanup proof. Defaults under --out.")
    parser.add_argument("--release-assets", help="Optional downloaded release assets directory to verify with release-consume.")
    parser.add_argument("--release-version", help="Version to use when verifying --release-assets. Defaults to VERSION.")
    parser.add_argument("--release-consume-out", help="Output directory for embedded release-consume proof. Defaults under --out.")
    parser.add_argument("--download-release-assets", action="store_true", help="Download GitHub release assets into a local proof directory before running release-consume.")
    parser.add_argument("--github-release-repo", help="GitHub repository in owner/repo form for --download-release-assets.")
    parser.add_argument("--download-release-assets-dir", help="Optional destination for downloaded GitHub release assets. Defaults under --out.")
    parser.add_argument("--github-api-url", default="https://api.github.com", help="GitHub API base URL. Defaults to https://api.github.com.")
    parser.add_argument("--github-token-env", default="GITHUB_TOKEN", help="Environment variable containing an optional GitHub API token.")
    parser.add_argument("--external-adoption-evidence", action="append", help="Optional external adoption evidence JSON file or directory. May be passed multiple times.")
    parser.add_argument("--security-review-evidence", action="append", help="Optional final security review evidence JSON file or directory. May be passed multiple times.")
    parser.add_argument("--shipguard-eval", action="store_true", help="Include ShipGuard-only product QA boundaries.")
    parser.add_argument("--shareable", action="store_true", help="Redact local absolute paths for shareable output.")
    parser.add_argument("--json", action="store_true", help="Write only JSON output.")
    parser.add_argument("--markdown", action="store_true", help="Write only Markdown output.")
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    out_dir = Path(args.out).expanduser().resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    report = build_report(args)

    write_json = args.json or not args.markdown
    write_markdown = args.markdown or not args.json
    if write_json:
        (out_dir / "v4-release-candidate.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if write_markdown:
        (out_dir / "v4-release-candidate.md").write_text(render_markdown(report), encoding="utf-8")
    print(f"wrote {out_dir}")
    return 0 if report["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
