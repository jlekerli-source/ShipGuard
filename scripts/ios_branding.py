#!/usr/bin/env python3
"""ShipGuard naming contract and branded iOS surface audit."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import sys
from pathlib import Path
from typing import Any


SCHEMA_VERSION = 1
ROOT = Path(__file__).resolve().parents[1]

SURFACES: list[dict[str, Any]] = [
    {
        "id": "brand",
        "command": "shipguard ios brand",
        "surfaceName": "ShipGuard Brand Deck",
        "codename": "brand-deck",
        "plainPurpose": "Keep ShipGuard naming, tone, and future feature labels consistent.",
        "tone": "Vibey but accountable.",
        "proofBoundary": "This command audits naming and docs; it does not rename private app code.",
        "aliases": ["naming scheme", "brand audit", "vibe rules"],
    },
    {
        "id": "doctor",
        "command": "shipguard ios doctor",
        "surfaceName": "ShipGuard DockCheck",
        "codename": "dockcheck",
        "plainPurpose": "Inspect Xcode, SwiftPM, schemes, targets, and proof readiness.",
        "tone": "Operational and quick.",
        "proofBoundary": "Source topology only; no simulator build is claimed.",
        "aliases": ["ios doctor", "topology check"],
    },
    {
        "id": "inventory",
        "command": "shipguard ios inventory",
        "surfaceName": "ShipGuard CargoScan",
        "codename": "cargoscan",
        "plainPurpose": "Map permissions, entitlements, StoreKit, widgets, intents, and runtime risk.",
        "tone": "Risk-aware and concrete.",
        "proofBoundary": "Inventory findings are routing inputs, not edits or validation proof.",
        "aliases": ["risk inventory", "surface map"],
    },
    {
        "id": "plan",
        "command": "shipguard ios plan",
        "surfaceName": "ShipGuard BriefForge",
        "codename": "briefforge",
        "plainPurpose": "Turn inventory into a scoped Codex brief with blockers and proof route.",
        "tone": "Decisive and scoped.",
        "proofBoundary": "Plans do not prove implementation; they name the next evidence lane.",
        "aliases": ["guided plan", "Codex brief"],
    },
    {
        "id": "prove",
        "command": "shipguard ios prove",
        "surfaceName": "ShipGuard ProofVault",
        "codename": "proofvault",
        "plainPurpose": "Separate local proof, simulator proof, manual proof, and blocked claims.",
        "tone": "Strict and evidence-first.",
        "proofBoundary": "ProofVault routes evidence; it does not invent missing proof.",
        "aliases": ["proof router", "claim boundary"],
    },
    {
        "id": "launchdeck",
        "command": "shipguard ios launchdeck",
        "surfaceName": "ShipGuard LaunchDeck",
        "codename": "launchdeck",
        "plainPurpose": "Route build/run, debugger, live preview, hot reload, and profiler work.",
        "tone": "Techy launch-control energy.",
        "proofBoundary": "LaunchDeck routes and grades receipts; Codex/Xcode tools execute simulator work.",
        "aliases": ["build/run front door", "Build iOS Apps bridge"],
    },
    {
        "id": "performance",
        "command": "shipguard ios performance",
        "surfaceName": "ShipGuard PulseRadar",
        "codename": "pulseradar",
        "plainPurpose": "Find SwiftUI, rendering, main-thread, and profiler-proof performance risks.",
        "tone": "Fast, skeptical, measurement-heavy.",
        "proofBoundary": "Source findings need route proof and device traces before smoothness claims.",
        "aliases": ["performance audit", "fps radar"],
    },
    {
        "id": "design",
        "command": "shipguard ios design",
        "surfaceName": "ShipGuard VibeCheck",
        "codename": "vibecheck",
        "plainPurpose": "Audit UI/UX coherence, motion, haptics, preview routing, and icon direction.",
        "tone": "Product taste with receipts.",
        "proofBoundary": "Visual, icon, and haptic quality claims need preview, ImageGen, or device proof.",
        "aliases": ["design audit", "UI/UX review", "motion and haptics"],
    },
    {
        "id": "modernize",
        "command": "shipguard ios modernize",
        "surfaceName": "ShipGuard UpgradeForge",
        "codename": "upgradeforge",
        "plainPurpose": "Plan Swift, SwiftUI, Observation, availability, and platform modernization.",
        "tone": "Forward-looking but migration-safe.",
        "proofBoundary": "Modernization roadmaps do not upgrade code until a scoped task is authorized.",
        "aliases": ["Swift upgrade", "modernization"],
    },
    {
        "id": "app-intelligence",
        "command": "shipguard ios app-intelligence",
        "surfaceName": "ShipGuard SignalLens",
        "codename": "signallens",
        "plainPurpose": "Audit App Intents, shortcuts, widgets, Spotlight, Siri, and system exposure.",
        "tone": "System-aware and privacy-aware.",
        "proofBoundary": "System exposure needs entitlement, privacy, and runtime proof before claims.",
        "aliases": ["App Intents", "system surfaces"],
    },
    {
        "id": "ai-readiness",
        "command": "shipguard ios ai-readiness",
        "surfaceName": "ShipGuard ModelDock",
        "codename": "modeldock",
        "plainPurpose": "Compare on-device, cloud, Core ML, no-AI, privacy, latency, and cost choices.",
        "tone": "Pragmatic, not hype-driven.",
        "proofBoundary": "ModelDock recommends architecture; model quality needs separate eval proof.",
        "aliases": ["AI readiness", "Core AI route"],
    },
    {
        "id": "external-audit",
        "command": "shipguard ios external-audit",
        "surfaceName": "ShipGuard SourceScout",
        "codename": "sourcescout",
        "plainPurpose": "Audit external repos, posts, and skills before native ShipGuard adoption.",
        "tone": "Curious but license-honest.",
        "proofBoundary": "External ideas count as integrated only after native action and validation.",
        "aliases": ["external source audit", "adoption ledger"],
    },
    {
        "id": "spec-workflow",
        "command": "shipguard ios spec-workflow",
        "surfaceName": "ShipGuard SpecForge",
        "codename": "specforge",
        "plainPurpose": "Generate ShipGuard-owned constitution, spec, plan, tasks, and analysis gates.",
        "tone": "Structured and execution-ready.",
        "proofBoundary": "SpecForge creates work instructions; implementation still needs validation.",
        "aliases": ["spec workflow", "requirements workflow"],
    },
    {
        "id": "report-quality",
        "command": "shipguard ios report-quality",
        "surfaceName": "ShipGuard QualityRadar",
        "codename": "qualityradar",
        "plainPurpose": "Grade ShipGuard reports for usefulness, boundaries, shareability, and fixtures.",
        "tone": "Direct and product-QA focused.",
        "proofBoundary": "QualityRadar grades ShipGuard output, not the scanned target app.",
        "aliases": ["report quality", "product QA"],
    },
    {
        "id": "preview",
        "command": "shipguard ios preview",
        "surfaceName": "ShipGuard MirrorPort",
        "codename": "mirrorport",
        "plainPurpose": "Serve the phone-shaped preview and typed visual-event receipts.",
        "tone": "Visual and handoff-friendly.",
        "proofBoundary": "MirrorPort captures intent; simulator taps need semantic element proof.",
        "aliases": ["preview bridge", "iPhone side preview"],
    },
    {
        "id": "devspace",
        "command": "shipguard ios devspace",
        "surfaceName": "ShipGuard Devspace Bridge",
        "codename": "devspace-bridge",
        "plainPurpose": "Expose preview evidence to ChatGPT/MCP planning and guarded Codex handoff.",
        "tone": "Connector-aware and boundary-heavy.",
        "proofBoundary": "Model selection happens in ChatGPT; Devspace does not execute arbitrary shell work.",
        "aliases": ["MCP bridge", "ChatGPT visual planning"],
    },
    {
        "id": "redact",
        "command": "shipguard ios redact",
        "surfaceName": "ShipGuard RedactionBay",
        "codename": "redactionbay",
        "plainPurpose": "Redact paths, tokens, IDs, accounts, and private terms before sharing.",
        "tone": "Privacy-first and boring on purpose.",
        "proofBoundary": "Redaction lowers risk; screenshots and private context still need review.",
        "aliases": ["redaction", "privacy scrub"],
    },
    {
        "id": "eval",
        "command": "shipguard ios eval",
        "surfaceName": "ShipGuard EvalArena",
        "codename": "evalarena",
        "plainPurpose": "Run deterministic behavior evals for routing, proof honesty, and plugin guidance.",
        "tone": "Competitive, repeatable, CI-safe.",
        "proofBoundary": "EvalArena covers workflow behavior, not app runtime correctness.",
        "aliases": ["workflow evals", "demo lane"],
    },
    {
        "id": "goals",
        "command": "shipguard ios goals",
        "surfaceName": "ShipGuard GoalEngine",
        "codename": "goalengine",
        "plainPurpose": "Keep slash-goal loops evidence-gated and restartable.",
        "tone": "Persistent and receipt-driven.",
        "proofBoundary": "GoalEngine tracks handoffs; completion still needs attached evidence.",
        "aliases": ["next goal", "slash goal"],
    },
    {
        "id": "release",
        "command": "shipguard release-proof",
        "surfaceName": "ShipGuard ReleaseDock",
        "codename": "releasedock",
        "plainPurpose": "Package, replay, consume, diff, attest, and publish release evidence.",
        "tone": "Shipping-focused and reproducible.",
        "proofBoundary": "ReleaseDock proves artifacts; GitHub/App Store publication remains external proof.",
        "aliases": ["release proof", "release evidence"],
    },
    {
        "id": "autopsy",
        "command": "shipguard autopsy",
        "surfaceName": "ShipGuard AutopsyLab",
        "codename": "autopsylab",
        "plainPurpose": "Score AI coding runs, diffs, tasks, validation logs, and PR-ready gates.",
        "tone": "Forensic and blunt.",
        "proofBoundary": "AutopsyLab evaluates a run transcript; it does not inspect live app behavior.",
        "aliases": ["run review", "ci gate"],
    },
    {
        "id": "arena",
        "command": "shipguard arena",
        "surfaceName": "ShipGuard ArenaBench",
        "codename": "arenabench",
        "plainPurpose": "Run, compare, import, sign, and verify public benchmark fixture packs.",
        "tone": "Benchmark-driven and reproducible.",
        "proofBoundary": "ArenaBench proves fixture behavior, not private production outcomes.",
        "aliases": ["benchmark", "fixture arena"],
    },
]

NAMING_RULES = [
    "Keep CLI verbs literal and searchable; add personality through surface names, section labels, and report copy.",
    "Every branded name must sit beside a plain-purpose sentence so new users are never forced to decode the joke.",
    "Use short techy nouns from the ShipGuard universe: Deck, Dock, Radar, Forge, Lens, Port, Vault, Bay, Arena, Engine, Lab.",
    "Avoid app-specific branding in reusable surfaces. Ringly and Ilmify belong only in read-only product-QA evidence docs.",
    "Never let a vibe label weaken proof language. Release, payment, privacy, haptic, performance, and simulator claims stay literal.",
    "New iOS commands must add a surface row here, docs coverage, a routing/eval case when user-facing, and package/self-audit coverage.",
]

ACTIVE_DOCS = [
    "README.md",
    "docs/cli.md",
    "docs/command-matrix.md",
    "docs/ios-shipguard.md",
    "docs/shipguard-naming.md",
    "plugins/ios-shipguard/skills/ios-shipguard/SKILL.md",
    "plugins/ios-shipguard/skills/ios-shipguard/references/modes.md",
]

BANNED_ACTIVE_PHRASES = [
    "Shipyard",
    "Shipcard",
    "Illumify",
    "InweFi",
    "Build iOS Apps bridge",
    "Build iOS Apps front door",
]


def utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def fail(message: str) -> None:
    print(f"ios-brand: {message}", file=sys.stderr)
    raise SystemExit(1)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Audit ShipGuard's branded naming scheme and future naming contract.")
    parser.add_argument("--path", default=".", help="ShipGuard checkout to inspect")
    parser.add_argument("--out", help="Output directory for ios-branding.md and ios-branding.json")
    parser.add_argument("--strict", action="store_true", help="Exit non-zero when active docs or command wiring drift")
    parser.add_argument("--json", action="store_true", help="Print JSON report to stdout")
    parser.add_argument("--markdown", action="store_true", help="Print Markdown report to stdout")
    return parser.parse_args()


def read_if_exists(path: Path) -> str:
    if not path.is_file():
        return ""
    return path.read_text(encoding="utf-8", errors="ignore")


def build_findings(root: Path) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    bin_text = read_if_exists(root / "bin" / "shipguard")
    doc_texts = {doc: read_if_exists(root / doc) for doc in ACTIVE_DOCS}
    combined_docs = "\n".join(doc_texts.values())

    for doc, text in doc_texts.items():
        if not text:
            findings.append(
                {
                    "severity": "high",
                    "category": "coverage",
                    "ruleId": "branding-active-doc-missing",
                    "evidence": doc,
                    "recommendation": f"Restore {doc} or remove it from the active naming coverage list.",
                    "proofGuidance": "Run shipguard ios brand --strict after restoring the file.",
                }
            )

    required_fields = ["surfaceName", "codename", "plainPurpose", "tone", "proofBoundary"]
    for surface in SURFACES:
        for field in required_fields:
            if not surface.get(field):
                findings.append(
                    {
                        "severity": "high",
                        "category": "surface-registry",
                        "ruleId": "branding-surface-field-missing",
                        "evidence": f"{surface.get('id', '<unknown>')} missing {field}",
                        "recommendation": "Every surface needs a branded name plus plain purpose, tone, and proof boundary.",
                        "proofGuidance": "Update scripts/ios_branding.py and rerun tests/ios_branding_test.sh.",
                    }
                )
        command = surface["command"]
        root_command = command.replace("shipguard ", "", 1)
        if command.startswith("shipguard ios ") and root_command.split()[1] not in bin_text:
            findings.append(
                {
                    "severity": "high",
                    "category": "command-wiring",
                    "ruleId": "branding-command-not-wired",
                    "evidence": command,
                    "recommendation": "Wire the command through bin/shipguard before publishing the surface name.",
                    "proofGuidance": f"Run `{command} --help` plus CLI smoke tests.",
                }
            )
        if surface["surfaceName"] not in combined_docs:
            findings.append(
                {
                    "severity": "review",
                    "category": "docs",
                    "ruleId": "branding-surface-doc-mention-missing",
                    "evidence": surface["surfaceName"],
                    "recommendation": "Mention the branded surface in the active docs so users see the naming scheme.",
                    "proofGuidance": "Run shipguard ios brand --strict and docs-check after updating docs.",
                }
            )

    for phrase in BANNED_ACTIVE_PHRASES:
        hits = [doc for doc, text in doc_texts.items() if phrase in text]
        if hits:
            findings.append(
                {
                    "severity": "high",
                    "category": "active-copy",
                    "ruleId": "branding-stale-active-phrase",
                    "evidence": f"{phrase} in {', '.join(hits)}",
                    "recommendation": "Replace stale active wording with the ShipGuard-native branded surface name.",
                    "proofGuidance": "Historical changelog/evidence entries may keep old terms; active docs and skill guidance should not.",
                }
            )

    if not findings:
        findings.append(
            {
                "severity": "info",
                "category": "naming-contract",
                "ruleId": "branding-contract-covered",
                "evidence": f"{len(SURFACES)} surfaces registered with active docs coverage.",
                "recommendation": "Keep adding new public surfaces here before release.",
                "proofGuidance": "Run tests/ios_branding_test.sh and shipguard ios brand --strict.",
            }
        )
    return findings


def build_report(root: Path, strict: bool) -> dict[str, Any]:
    findings = build_findings(root)
    blocking = [item for item in findings if item["severity"] == "high"]
    return {
        "schemaVersion": SCHEMA_VERSION,
        "tool": "shipguard ios brand",
        "generatedAt": utc_now(),
        "status": "pass" if not blocking else "review",
        "strict": strict,
        "surfaceCount": len(SURFACES),
        "brandPrinciple": "Friendly ship-control energy, but every joke has a proof receipt attached.",
        "namingRules": NAMING_RULES,
        "surfaces": SURFACES,
        "futureNamingContract": {
            "newCommandChecklist": [
                "Add the literal CLI command to bin/shipguard.",
                "Add a branded surface row to scripts/ios_branding.py.",
                "Mention the surface in docs/shipguard-naming.md and the command matrix.",
                "Add skill or eval routing when a user would ask for the surface by name.",
                "Add self-audit, package, and focused tests before pushing.",
            ],
            "toneGuardrail": "A surface can be funny only after its plain purpose and proof boundary are clear.",
            "publicInterfacePolicy": "Do not rename stable CLI commands just for flavor; make aliases and docs feel native while commands remain automation-safe.",
        },
        "findings": findings,
    }


def render_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# ShipGuard Brand Deck",
        "",
        f"- Status: {report['status']}",
        f"- Surfaces: {report['surfaceCount']}",
        f"- Principle: {report['brandPrinciple']}",
        "",
        "## Naming Rules",
        "",
    ]
    for rule in report["namingRules"]:
        lines.append(f"- {rule}")
    lines.extend(
        [
            "",
            "## Surface Scheme",
            "",
            "| Command | Branded Surface | Plain Purpose | Proof Boundary |",
            "| --- | --- | --- | --- |",
        ]
    )
    for surface in report["surfaces"]:
        lines.append(
            f"| `{surface['command']}` | {surface['surfaceName']} | {surface['plainPurpose']} | {surface['proofBoundary']} |"
        )
    lines.extend(
        [
            "",
            "## Future Naming Contract",
            "",
            f"- Tone guardrail: {report['futureNamingContract']['toneGuardrail']}",
            f"- Public interface policy: {report['futureNamingContract']['publicInterfacePolicy']}",
            "",
            "### New Command Checklist",
            "",
        ]
    )
    for item in report["futureNamingContract"]["newCommandChecklist"]:
        lines.append(f"- {item}")
    lines.extend(
        [
            "",
            "## Findings",
            "",
            "| Severity | Rule | Evidence | Recommendation |",
            "| --- | --- | --- | --- |",
        ]
    )
    for finding in report["findings"]:
        lines.append(
            f"| {finding['severity']} | {finding['ruleId']} | {finding['evidence']} | {finding['recommendation']} |"
        )
    lines.append("")
    return "\n".join(lines)


def main() -> None:
    args = parse_args()
    root = Path(args.path).resolve()
    if not root.is_dir():
        fail(f"path is not a directory: {root}")

    report = build_report(root, strict=args.strict)
    markdown = render_markdown(report)

    if args.out:
        out_dir = Path(args.out)
        out_dir.mkdir(parents=True, exist_ok=True)
        (out_dir / "ios-branding.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        (out_dir / "ios-branding.md").write_text(markdown, encoding="utf-8")
        print(f"wrote: {out_dir / 'ios-branding.json'}")
        print(f"wrote: {out_dir / 'ios-branding.md'}")
        print(f"status: {report['status']}")

    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    elif args.markdown or not args.out:
        print(markdown)

    if args.strict and report["status"] != "pass":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
