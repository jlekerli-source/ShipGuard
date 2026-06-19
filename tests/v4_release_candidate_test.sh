#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_root"

tmp_dir="$(mktemp -d)"
trap 'rm -rf "$tmp_dir"' EXIT

./bin/shipguard v4 release-candidate --help >/dev/null
./bin/shipguard v4 release-candidate \
  --path . \
  --out "$tmp_dir/v4-release-candidate" \
  --shipguard-eval \
  --shareable
./bin/shipguard v4 release-candidate \
  --path . \
  --out "$tmp_dir/json-only" \
  --json
./bin/shipguard v4 release-candidate \
  --path . \
  --out "$tmp_dir/markdown-only" \
  --markdown

test -f "$tmp_dir/v4-release-candidate/v4-release-candidate.json"
test -f "$tmp_dir/v4-release-candidate/v4-release-candidate.md"
test -f "$tmp_dir/json-only/v4-release-candidate.json"
test ! -f "$tmp_dir/json-only/v4-release-candidate.md"
test -f "$tmp_dir/markdown-only/v4-release-candidate.md"
test ! -f "$tmp_dir/markdown-only/v4-release-candidate.json"

python3 -m json.tool "$tmp_dir/v4-release-candidate/v4-release-candidate.json" >/dev/null

grep -q '# ShipGuard V4 Release Candidate Readiness' "$tmp_dir/v4-release-candidate/v4-release-candidate.md"
grep -q '## Result' "$tmp_dir/v4-release-candidate/v4-release-candidate.md"
grep -q 'Readiness Proof' "$tmp_dir/v4-release-candidate/v4-release-candidate.md"
grep -q 'Fresh Install' "$tmp_dir/v4-release-candidate/v4-release-candidate.md"
grep -q 'Fresh Install Package Proof' "$tmp_dir/v4-release-candidate/v4-release-candidate.md"
grep -q 'Release Proof Consumption' "$tmp_dir/v4-release-candidate/v4-release-candidate.md"
grep -q 'Published Release Asset Proof' "$tmp_dir/v4-release-candidate/v4-release-candidate.md"
grep -q 'External Adoption Packet' "$tmp_dir/v4-release-candidate/v4-release-candidate.md"
grep -q 'Plugin Refresh Proof' "$tmp_dir/v4-release-candidate/v4-release-candidate.md"
grep -q 'Blocked Claims' "$tmp_dir/v4-release-candidate/v4-release-candidate.md"
grep -q 'Scope Boundary' "$tmp_dir/v4-release-candidate/v4-release-candidate.md"

grep -q '"tool": "shipguard v4 release-candidate"' "$tmp_dir/v4-release-candidate/v4-release-candidate.json"
grep -q '"surface": "ShipGuard V4 Release Candidate Readiness"' "$tmp_dir/v4-release-candidate/v4-release-candidate.json"
grep -q '"status": "pass"' "$tmp_dir/v4-release-candidate/v4-release-candidate.json"
grep -q '"productStage": "v4-release-candidate-readiness"' "$tmp_dir/v4-release-candidate/v4-release-candidate.json"
grep -q '"readinessProof":' "$tmp_dir/v4-release-candidate/v4-release-candidate.json"
grep -q '"installProof":' "$tmp_dir/v4-release-candidate/v4-release-candidate.json"
grep -q '"freshInstallPackageProof":' "$tmp_dir/v4-release-candidate/v4-release-candidate.json"
grep -q '"upgradeProof":' "$tmp_dir/v4-release-candidate/v4-release-candidate.json"
grep -q '"uninstallProof":' "$tmp_dir/v4-release-candidate/v4-release-candidate.json"
grep -q '"releaseProofConsumption":' "$tmp_dir/v4-release-candidate/v4-release-candidate.json"
grep -q '"publishedReleaseAssetProof":' "$tmp_dir/v4-release-candidate/v4-release-candidate.json"
grep -q '"externalAdoptionPacket":' "$tmp_dir/v4-release-candidate/v4-release-candidate.json"
grep -q '"pluginRefreshProof":' "$tmp_dir/v4-release-candidate/v4-release-candidate.json"
grep -q '"releaseClaim": "candidate-ready"' "$tmp_dir/v4-release-candidate/v4-release-candidate.json"
grep -q '"stableV4Release": false' "$tmp_dir/v4-release-candidate/v4-release-candidate.json"
grep -q '"shipguardOnly": true' "$tmp_dir/v4-release-candidate/v4-release-candidate.json"
grep -q '"targetAppsReadOnly": true' "$tmp_dir/v4-release-candidate/v4-release-candidate.json"
grep -q '"privateAppsUsed": false' "$tmp_dir/v4-release-candidate/v4-release-candidate.json"
grep -q '"doesNotPublishRelease": true' "$tmp_dir/v4-release-candidate/v4-release-candidate.json"
grep -q '"mode": "ShipGuard product QA"' "$tmp_dir/v4-release-candidate/v4-release-candidate.json"

if grep -R -F -q "$repo_root" "$tmp_dir/v4-release-candidate"; then
  echo "shareable v4 release-candidate output must not include the local repo path" >&2
  exit 1
fi

python3 - "$tmp_dir/v4-release-candidate/v4-release-candidate.json" <<'PY'
import json
import sys

report = json.load(open(sys.argv[1], encoding="utf-8"))
assert report["tool"] == "shipguard v4 release-candidate"
assert report["surface"] == "ShipGuard V4 Release Candidate Readiness"
assert report["status"] == "pass"
assert report["productStage"] == "v4-release-candidate-readiness"
assert report["releaseReadiness"]["releaseClaim"] == "candidate-ready"
assert report["releaseReadiness"]["stableV4Release"] is False
assert report["releaseReadiness"]["freshInstallPackageProof"] == "not-provided"
assert report["releaseReadiness"]["publishedReleaseAssetProof"] == "not-provided"
for key in [
    "freshInstall",
    "upgrade",
    "uninstall",
    "releaseProofConsumption",
    "externalAdoptionPacket",
    "finalSchemaDocs",
    "pluginRefreshProof",
]:
    assert report["readinessProof"][key]["status"] == "pass"
assert "release-consume verify" in " ".join(report["releaseProofConsumption"]["commands"])
assert report["freshInstallPackageProof"]["status"] == "not-provided"
assert report["freshInstallPackageProof"]["provided"] is False
assert report["freshInstallPackageProof"]["requiredForStableV4"] is True
assert "--package-tarball <release-tarball>" in report["freshInstallPackageProof"]["nextCommand"]
assert "--package-tarball <release-tarball>" in report["resultUX"]["nextCommand"]
assert report["publishedReleaseAssetProof"]["status"] == "not-provided"
assert report["publishedReleaseAssetProof"]["provided"] is False
assert report["publishedReleaseAssetProof"]["requiredForStableV4"] is True
assert "--release-assets <downloaded-assets-dir>" in report["publishedReleaseAssetProof"]["nextCommand"]
assert "codex status --strict" in " ".join(report["pluginRefreshProof"]["commands"])
assert "external developer" in report["externalAdoptionPacket"]["supportBoundary"]
assert any("stable v4 product release" in claim.lower() for claim in report["blockedClaims"])
assert report["scopeBoundary"]["shipguardOnly"] is True
assert report["scopeBoundary"]["targetAppsReadOnly"] is True
assert report["scopeBoundary"]["privateAppsUsed"] is False
assert report["scopeBoundary"]["doesNotPublishRelease"] is True
assert "fresh-install receipt" in report["resultUX"]["priorityAction"].lower()
PY

version="$(sed -n '1p' VERSION)"
SHIPGUARD_GENERATED_AT="2026-06-19T00:00:00Z" \
  ./bin/shipguard release-proof build \
    --out "$tmp_dir/proof-bundle" \
    --version "$version" \
    --tag "v$version" \
    --commit 0123456789abcdef \
    --ci-run-url "https://github.com/jlekerli-source/ShipGuard/actions/runs/123" \
    --release-url "https://github.com/jlekerli-source/ShipGuard/releases/tag/v$version" \
    --issue-url "https://github.com/jlekerli-source/ShipGuard/issues/99" >/dev/null

mkdir -p "$tmp_dir/downloaded"
cp "$tmp_dir/proof-bundle/shipguard-v$version.tar.gz" "$tmp_dir/downloaded/"
cp "$tmp_dir/proof-bundle/proof/release-manifest.json" "$tmp_dir/downloaded/"
cp "$tmp_dir/proof-bundle/index/release-index.json" "$tmp_dir/downloaded/"
cp "$tmp_dir/proof-bundle/proof/proof-ledger.md" "$tmp_dir/downloaded/"
cp "$tmp_dir/proof-bundle/replay/replay-report.json" "$tmp_dir/downloaded/"
cp "$tmp_dir/proof-bundle/attestation/attestation.json" "$tmp_dir/downloaded/"
cp "$tmp_dir/proof-bundle/attestation/attestation-badge.json" "$tmp_dir/downloaded/"

SHIPGUARD_GENERATED_AT="2026-06-19T00:00:00Z" \
  ./bin/shipguard v4 release-candidate \
    --path . \
    --package-tarball "$tmp_dir/proof-bundle/shipguard-v$version.tar.gz" \
    --fresh-install-prefix "$tmp_dir/fresh-prefix" \
    --fresh-install-work-dir "$tmp_dir/fresh-work" \
    --out "$tmp_dir/with-assets" \
    --release-assets "$tmp_dir/downloaded" \
    --release-version "$version" \
    --release-consume-out "$tmp_dir/with-assets-consume" \
    --shipguard-eval \
    --shareable

test -f "$tmp_dir/with-assets/v4-release-candidate.json"
test -f "$tmp_dir/with-assets/v4-release-candidate.md"
test -f "$tmp_dir/with-assets-consume/consumer-report.json"
test -f "$tmp_dir/with-assets-consume/asset-digests.json"
test -x "$tmp_dir/fresh-prefix/bin/shipguard"

python3 - "$tmp_dir/with-assets/v4-release-candidate.json" <<'PY'
import json
import sys

report = json.load(open(sys.argv[1], encoding="utf-8"))
fresh = report["freshInstallPackageProof"]
proof = report["publishedReleaseAssetProof"]
assert report["status"] == "pass"
assert report["releaseReadiness"]["freshInstallPackageProof"] == "pass"
assert report["releaseReadiness"]["publishedReleaseAssetProof"] == "pass"
assert fresh["status"] == "pass"
assert fresh["provided"] is True
assert fresh["installedVersion"] == report["version"]
assert fresh["installedLegacyVersion"] == report["version"]
assert fresh["forbiddenInstalledPathCount"] == 0
assert fresh["packageTarball"] == "<package-tarball>"
assert fresh["installPrefix"] == "<fresh-install-prefix>"
assert fresh["workDir"] == "<fresh-install-work-dir>"
assert fresh["packageRoot"] == "<fresh-install-package-root>"
assert fresh["installedRoot"] == "<fresh-install-root>"
assert fresh["versionResult"]["exitCode"] == 0
assert fresh["legacyVersionResult"]["exitCode"] == 0
assert fresh["validateResult"]["exitCode"] == 0
assert proof["status"] == "pass"
assert proof["provided"] is True
assert proof["consumerReportStatus"] == "pass"
assert proof["replayStatus"] == "pass"
assert proof["attestationStatus"] == "pass"
assert proof["consumerReportPath"] == "<release-consume-out>/consumer-report.json"
assert proof["assetDigestMatrixPath"] == "<release-consume-out>/asset-digests.json"
assert proof["assetsDir"] == "<release-assets>"
assert proof["consumeOut"] == "<release-consume-out>"
assert report["resultUX"]["nextCommand"] == "./tests/v4_release_candidate_test.sh"
PY

if grep -R -F -q "$tmp_dir/downloaded" "$tmp_dir/with-assets"; then
  echo "shareable v4 release-candidate output must redact release asset paths" >&2
  exit 1
fi
if grep -R -F -q "$tmp_dir/with-assets-consume" "$tmp_dir/with-assets"; then
  echo "shareable v4 release-candidate output must redact release-consume paths" >&2
  exit 1
fi
if grep -R -F -q "$tmp_dir/fresh-prefix" "$tmp_dir/with-assets"; then
  echo "shareable v4 release-candidate output must redact fresh install prefix paths" >&2
  exit 1
fi
if grep -R -F -q "$tmp_dir/fresh-work" "$tmp_dir/with-assets"; then
  echo "shareable v4 release-candidate output must redact fresh install work paths" >&2
  exit 1
fi

if ./bin/shipguard v4 release-candidate \
  --path . \
  --out "$tmp_dir/missing-tarball" \
  --package-tarball "$tmp_dir/does-not-exist.tar.gz" \
  --json >/dev/null 2>&1; then
  echo "expected missing package tarball to fail release-candidate proof" >&2
  exit 1
fi
test -f "$tmp_dir/missing-tarball/v4-release-candidate.json"
grep -q '"status": "review"' "$tmp_dir/missing-tarball/v4-release-candidate.json"
grep -q '"freshInstallPackageProof": "blocked"' "$tmp_dir/missing-tarball/v4-release-candidate.json"

mkdir -p "$tmp_dir/unsafe-package/shipguard-v$version/scripts"
printf '#!/usr/bin/env bash\nexit 0\n' > "$tmp_dir/unsafe-package/shipguard-v$version/scripts/install.sh"
ln -s /tmp "$tmp_dir/unsafe-package/shipguard-v$version/unsafe-link"
(cd "$tmp_dir/unsafe-package" && tar -czf "$tmp_dir/unsafe-package.tar.gz" "shipguard-v$version")
if ./bin/shipguard v4 release-candidate \
  --path . \
  --out "$tmp_dir/unsafe-tarball" \
  --package-tarball "$tmp_dir/unsafe-package.tar.gz" \
  --json >/dev/null 2>&1; then
  echo "expected unsafe package tarball to fail release-candidate proof" >&2
  exit 1
fi
test -f "$tmp_dir/unsafe-tarball/v4-release-candidate.json"
grep -q '"freshInstallPackageProof": "blocked"' "$tmp_dir/unsafe-tarball/v4-release-candidate.json"
grep -q 'unsafe tarball member is a link or device' "$tmp_dir/unsafe-tarball/v4-release-candidate.json"

if ./bin/shipguard v4 release-candidate \
  --path . \
  --out "$tmp_dir/missing-assets" \
  --package-tarball "$tmp_dir/proof-bundle/shipguard-v$version.tar.gz" \
  --release-assets "$tmp_dir/does-not-exist" \
  --release-version "$version" \
  --json >/dev/null 2>&1; then
  echo "expected missing release assets to fail release-candidate proof" >&2
  exit 1
fi
test -f "$tmp_dir/missing-assets/v4-release-candidate.json"
grep -q '"status": "review"' "$tmp_dir/missing-assets/v4-release-candidate.json"
grep -q '"publishedReleaseAssetProof": "blocked"' "$tmp_dir/missing-assets/v4-release-candidate.json"

echo "v4 release-candidate test passed"
