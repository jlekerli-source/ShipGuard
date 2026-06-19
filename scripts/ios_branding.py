#!/usr/bin/env python3
"""ShipGuard naming contract and branded public surface audit."""

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
        "command": "shipguard brand",
        "relatedCommands": ["shipguard ios brand"],
        "surfaceName": "ShipGuard Brand Deck",
        "codename": "brand-deck",
        "plainPurpose": "Keep ShipGuard naming, tone, and future feature labels consistent across the whole toolkit.",
        "tone": "Vibey but accountable.",
        "proofBoundary": "This command audits naming and docs; it does not rename private app code.",
        "aliases": ["naming scheme", "brand audit", "vibe rules"],
    },
    {
        "id": "init",
        "command": "shipguard init",
        "surfaceName": "ShipGuard StarterBay",
        "codename": "starterbay",
        "plainPurpose": "Install starter workflow profiles into iOS, web, backend, or CLI repos.",
        "tone": "Welcoming, quick, and copy-safe.",
        "proofBoundary": "StarterBay copies templates; the target repo still needs validation after install.",
        "aliases": ["starter profile", "repo bootstrap"],
    },
    {
        "id": "validate",
        "command": "shipguard validate",
        "surfaceName": "ShipGuard RigCheck",
        "codename": "rigcheck",
        "plainPurpose": "Validate that a ShipGuard checkout or package contains the required workflow bundle.",
        "tone": "Mechanical and strict.",
        "proofBoundary": "RigCheck proves bundle shape, not app behavior or release readiness.",
        "aliases": ["bundle validation", "workflow check"],
    },
    {
        "id": "root-doctor",
        "command": "shipguard doctor",
        "surfaceName": "ShipGuard RepoVitals",
        "codename": "repovitals",
        "plainPurpose": "Check whether a target repo has the starter workflow files it should have.",
        "tone": "Diagnostic and practical.",
        "proofBoundary": "RepoVitals checks installation health; it does not audit the app implementation.",
        "aliases": ["repo doctor", "starter health"],
    },
    {
        "id": "web-audit",
        "command": "shipguard web audit",
        "surfaceName": "ShipGuard WebScan",
        "codename": "webscan",
        "plainPurpose": "Run a first web-app audit for framework signals, auth/payment risks, validation lanes, starter workflow health, and next commands.",
        "tone": "Frontend-aware, scoped, and validation-first.",
        "proofBoundary": "WebScan is read-only source analysis; it recommends proof commands but does not run browser or production checks.",
        "aliases": ["web audit", "frontend first audit"],
    },
    {
        "id": "web-plan",
        "command": "shipguard web plan",
        "surfaceName": "ShipGuard WebForge",
        "codename": "webforge",
        "plainPurpose": "Turn WebScan output into scoped web tasks, validation commands, stop conditions, and report-quality questions.",
        "tone": "Practical, frontend-native, and proof-first.",
        "proofBoundary": "WebForge plans next work from a read-only audit; it does not edit, run, or deploy the target web app.",
        "aliases": ["web fix plan", "frontend work plan"],
    },
    {
        "id": "backend-audit",
        "command": "shipguard backend audit",
        "surfaceName": "ShipGuard ServiceRadar",
        "codename": "serviceradar",
        "plainPurpose": "Run a first backend-service audit for API, auth, migration, queue, webhook, observability, validation, and next-command signals.",
        "tone": "Operational, risk-aware, and backend-native.",
        "proofBoundary": "ServiceRadar is read-only source analysis; it does not contact services, databases, queues, or production endpoints.",
        "aliases": ["backend audit", "service audit"],
    },
    {
        "id": "backend-plan",
        "command": "shipguard backend plan",
        "surfaceName": "ShipGuard ServiceForge",
        "codename": "serviceforge",
        "plainPurpose": "Turn ServiceRadar output into scoped backend tasks, validation commands, stop conditions, and report-quality questions.",
        "tone": "Operational, conservative, and proof-heavy.",
        "proofBoundary": "ServiceForge plans next work from a read-only audit; it does not contact services, mutate databases, or deploy code.",
        "aliases": ["backend fix plan", "service work plan"],
    },
    {
        "id": "cli-audit",
        "command": "shipguard cli audit",
        "surfaceName": "ShipGuard CommandLens",
        "codename": "commandlens",
        "plainPurpose": "Run a first CLI-tool audit for command dispatch, argument parsing, stdout/stderr contracts, exit codes, redaction, packaging, and next commands.",
        "tone": "Precise, contract-focused, and shell-friendly.",
        "proofBoundary": "CommandLens is read-only source analysis; it does not execute target CLI commands or mutate user files.",
        "aliases": ["cli audit", "command audit"],
    },
    {
        "id": "cli-plan",
        "command": "shipguard cli plan",
        "surfaceName": "ShipGuard CommandForge",
        "codename": "commandforge",
        "plainPurpose": "Turn CommandLens output into scoped CLI tasks, smoke commands, contract checks, stop conditions, and report-quality questions.",
        "tone": "Contract-first, shell-aware, and explicit.",
        "proofBoundary": "CommandForge plans next work from a read-only audit; it does not execute or mutate the target CLI.",
        "aliases": ["cli fix plan", "command work plan"],
    },
    {
        "id": "policy",
        "command": "shipguard policy",
        "surfaceName": "ShipGuard RuleHarbor",
        "codename": "ruleharbor",
        "plainPurpose": "Initialize or inspect policy config for scoped agent behavior.",
        "tone": "Clear boundaries, no drama.",
        "proofBoundary": "RuleHarbor describes rules; enforcement needs the matching validation lane.",
        "aliases": ["policy config", "rules"],
    },
    {
        "id": "score",
        "command": "shipguard score",
        "surfaceName": "ShipGuard RunScore",
        "codename": "runscore",
        "plainPurpose": "Score a Codex run against scope, ownership, risk, validation, and handoff quality.",
        "tone": "Blunt and review-minded.",
        "proofBoundary": "RunScore grades supplied text; it does not verify unprovided logs or diffs.",
        "aliases": ["scorecard", "run rating"],
    },
    {
        "id": "value-gauntlet",
        "command": "shipguard value-gauntlet",
        "surfaceName": "ShipGuard Tool Value Gauntlet",
        "codename": "tool-value-gauntlet",
        "plainPurpose": "Grade ShipGuard commands, skills, plugins, actions, docs, and proof surfaces for real developer usefulness.",
        "tone": "Demanding, practical, and product-QA focused.",
        "proofBoundary": "Tool Value Gauntlet is read-only product QA; it prioritizes ShipGuard upgrades and does not edit target apps.",
        "aliases": ["tool usefulness audit", "100/10 dev value audit"],
    },
    {
        "id": "full-audit",
        "command": "shipguard full-audit",
        "surfaceName": "ShipGuard Full Audit",
        "codename": "full-audit",
        "plainPurpose": "Run or plan the full ShipYard validation, value, package, plugin, CI, and release-proof lane from one resumable report.",
        "tone": "Operational, concise, and evidence-aware.",
        "proofBoundary": "Full Audit orchestrates ShipGuard proof stages and records receipts; it does not push commits, publish releases, or edit target apps.",
        "aliases": ["unleash the beast", "shipyard proof lane", "release audit lane"],
    },
    {
        "id": "pilot-bench",
        "command": "shipguard pilot-bench",
        "surfaceName": "ShipGuard PilotBench",
        "codename": "pilot-bench",
        "plainPurpose": "Score public-safe read-only task traces for external pilot verdict usefulness.",
        "tone": "Evidence-first, sharp, and product-QA focused.",
        "proofBoundary": "PilotBench scores ShipGuard verdict quality from traces; it does not grade or modify the target app.",
        "aliases": ["external pilot verdict bench", "pilot verdict scoring"],
    },
    {
        "id": "transcript",
        "command": "shipguard transcript",
        "surfaceName": "ShipGuard TraceVault",
        "codename": "tracevault",
        "plainPurpose": "Redact, verify, and index maintainer transcripts for public-safe evidence.",
        "tone": "Careful, archival, and privacy-aware.",
        "proofBoundary": "TraceVault audits transcript artifacts; human review is still required for sensitive context.",
        "aliases": ["transcript redaction", "run transcript corpus"],
    },
    {
        "id": "review-comment",
        "command": "shipguard review-comment",
        "surfaceName": "ShipGuard ReviewBeacon",
        "codename": "reviewbeacon",
        "plainPurpose": "Turn autopsy output into a PR-ready review comment and badge.",
        "tone": "Reviewer-friendly and concise.",
        "proofBoundary": "ReviewBeacon summarizes an existing report; it does not create new validation evidence.",
        "aliases": ["PR comment", "review badge"],
    },
    {
        "id": "ci-gate",
        "command": "shipguard ci-gate",
        "surfaceName": "ShipGuard GateTower",
        "codename": "gatetower",
        "plainPurpose": "Create CI gate output from run, diff, task, policy, and validation logs.",
        "tone": "Firm, automatable, and evidence-first.",
        "proofBoundary": "GateTower enforces configured evidence; bad inputs still need source review.",
        "aliases": ["CI gate", "quality gate"],
    },
    {
        "id": "ci-summary",
        "command": "shipguard ci-summary",
        "surfaceName": "ShipGuard BriefBeacon",
        "codename": "briefbeacon",
        "plainPurpose": "Render CI gate JSON into a GitHub Actions step summary.",
        "tone": "Readable and status-focused.",
        "proofBoundary": "BriefBeacon reports gate state; it does not rerun validation.",
        "aliases": ["CI summary", "step summary"],
    },
    {
        "id": "check-run",
        "command": "shipguard check-run",
        "surfaceName": "ShipGuard CheckPilot",
        "codename": "checkpilot",
        "plainPurpose": "Generate or post GitHub Checks API payloads from gate output.",
        "tone": "API-aware and dry-run friendly.",
        "proofBoundary": "CheckPilot can prepare payloads locally; posting needs GitHub token and API proof.",
        "aliases": ["GitHub Check Run", "checks payload"],
    },
    {
        "id": "sarif",
        "command": "shipguard sarif",
        "surfaceName": "ShipGuard AlertBeacon",
        "codename": "alertbeacon",
        "plainPurpose": "Convert autopsy findings into SARIF for code scanning surfaces.",
        "tone": "Standards-friendly and precise.",
        "proofBoundary": "AlertBeacon exports findings; it does not prove GitHub ingestion.",
        "aliases": ["SARIF export", "code scanning"],
    },
    {
        "id": "docs-check",
        "command": "shipguard docs-check",
        "surfaceName": "ShipGuard LinkSweep",
        "codename": "linksweep",
        "plainPurpose": "Check Markdown docs for broken local links.",
        "tone": "Quiet and hygiene-focused.",
        "proofBoundary": "LinkSweep checks local Markdown references, not external website uptime.",
        "aliases": ["docs links", "Markdown link check"],
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
        "id": "devspace-check",
        "command": "shipguard ios devspace-check",
        "surfaceName": "ShipGuard BridgeWatch",
        "codename": "bridgewatch",
        "plainPurpose": "Grade Devspace connector readiness, public URL safety, and widget handoff quality.",
        "tone": "Careful, skeptical, and connector-aware.",
        "proofBoundary": "BridgeWatch is static readiness proof; it does not start tunnels or execute handoffs.",
        "aliases": ["Devspace readiness", "connector check"],
    },
    {
        "id": "target-match",
        "command": "shipguard ios target-match",
        "surfaceName": "ShipGuard TapCompass",
        "codename": "tapcompass",
        "plainPurpose": "Match preview events to UI snapshot elements before a visual handoff becomes action.",
        "tone": "Precise and anti-coordinate.",
        "proofBoundary": "TapCompass improves target confidence; real taps still need simulator proof.",
        "aliases": ["target matching", "tap routing"],
    },
    {
        "id": "codex-handoff",
        "command": "shipguard ios codex-handoff",
        "surfaceName": "ShipGuard HandoffRail",
        "codename": "handoffrail",
        "plainPurpose": "Package a guarded Codex app-server handoff from a prompt or preview planning bundle.",
        "tone": "Direct and bounded.",
        "proofBoundary": "HandoffRail prepares instructions; execution requires an explicit local Codex action.",
        "aliases": ["Codex handoff", "handoff bundle"],
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
        "id": "demo",
        "command": "shipguard ios demo",
        "surfaceName": "ShipGuard DemoDock",
        "codename": "demodock",
        "plainPurpose": "Run a clean first-run iOS ShipGuard demo without Xcode, credentials, or private code.",
        "tone": "Friendly, reproducible, and low-friction.",
        "proofBoundary": "DemoDock proves package onboarding, not a target app workflow.",
        "aliases": ["first-run demo", "package demo"],
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
        "id": "release-manifest",
        "command": "shipguard release-manifest",
        "surfaceName": "ShipGuard ManifestForge",
        "codename": "manifestforge",
        "plainPurpose": "Build or verify release manifests and proof ledgers for packaged artifacts.",
        "tone": "Ledger-like and reproducible.",
        "proofBoundary": "ManifestForge records artifact identity; release publication remains separate proof.",
        "aliases": ["release manifest", "proof ledger"],
    },
    {
        "id": "release-index",
        "command": "shipguard release-index",
        "surfaceName": "ShipGuard ReleaseAtlas",
        "codename": "releaseatlas",
        "plainPurpose": "Build a catalog from release manifests.",
        "tone": "Organized and history-aware.",
        "proofBoundary": "ReleaseAtlas indexes supplied manifests; it does not verify missing artifacts.",
        "aliases": ["release catalog", "manifest index"],
    },
    {
        "id": "release-replay",
        "command": "shipguard release-replay",
        "surfaceName": "ShipGuard ReplayRig",
        "codename": "replayrig",
        "plainPurpose": "Replay release verification against downloaded assets, manifests, and ledgers.",
        "tone": "Repeatable and skeptical.",
        "proofBoundary": "ReplayRig verifies available release assets, not external download-page correctness.",
        "aliases": ["release replay", "asset replay"],
    },
    {
        "id": "release-attest",
        "command": "shipguard release-attest",
        "surfaceName": "ShipGuard TrustStamp",
        "codename": "truststamp",
        "plainPurpose": "Build release attestation JSON, Markdown, and badge evidence.",
        "tone": "Trust-focused and concise.",
        "proofBoundary": "TrustStamp attests to local replay inputs; it is not a legal signing service.",
        "aliases": ["release attestation", "proof badge"],
    },
    {
        "id": "release-consume",
        "command": "shipguard release-consume",
        "surfaceName": "ShipGuard ConsumerDock",
        "codename": "consumerdock",
        "plainPurpose": "Verify downloaded release assets from a consumer's perspective.",
        "tone": "User-facing and distrust-by-default.",
        "proofBoundary": "ConsumerDock verifies downloaded files; it cannot prove what another user downloaded.",
        "aliases": ["consumer proof", "download verification"],
    },
    {
        "id": "release-diff",
        "command": "shipguard release-diff",
        "surfaceName": "ShipGuard DiffLens",
        "codename": "difflens",
        "plainPurpose": "Compare two release proof asset directories and report what changed.",
        "tone": "Comparative and change-aware.",
        "proofBoundary": "DiffLens compares supplied artifacts only; missing baselines are explicit blockers.",
        "aliases": ["release diff", "asset comparison"],
    },
    {
        "id": "release-evidence",
        "command": "shipguard release-evidence",
        "surfaceName": "ShipGuard EvidenceHarbor",
        "codename": "evidenceharbor",
        "plainPurpose": "Export or verify release evidence sites, indexes, and local evidence bundles.",
        "tone": "Public-proof oriented and orderly.",
        "proofBoundary": "EvidenceHarbor packages evidence; hosting and external publication remain separate proof.",
        "aliases": ["evidence site", "release evidence bundle"],
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
    {
        "id": "codex-status",
        "command": "shipguard codex status",
        "surfaceName": "ShipGuard PluginRadar",
        "codename": "pluginradar",
        "plainPurpose": "Check local Codex plugin install state, stale metadata, and CLI resolution.",
        "tone": "Environment-aware and direct.",
        "proofBoundary": "PluginRadar inspects local cache state; a new thread may still be required to load updates.",
        "aliases": ["plugin status", "Codex install check"],
    },
    {
        "id": "leaderboard",
        "command": "shipguard leaderboard",
        "surfaceName": "ShipGuard ScoreTower",
        "codename": "scoretower",
        "plainPurpose": "Build stable leaderboard JSON from arena benchmark results.",
        "tone": "Competitive but reproducible.",
        "proofBoundary": "ScoreTower ranks supplied results; benchmark trust depends on fixture integrity.",
        "aliases": ["leaderboard", "benchmark ranking"],
    },
    {
        "id": "self-audit",
        "command": "shipguard self-audit",
        "surfaceName": "ShipGuard SelfScan",
        "codename": "selfscan",
        "plainPurpose": "Generate toolkit readiness proof for the ShipGuard checkout.",
        "tone": "Internal-quality focused.",
        "proofBoundary": "SelfScan audits ShipGuard readiness, not target-app readiness.",
        "aliases": ["self audit", "toolkit readiness"],
    },
    {
        "id": "next-goal",
        "command": "shipguard next-goal",
        "surfaceName": "ShipGuard NextRail",
        "codename": "nextrail",
        "plainPurpose": "Generate the next slash-plan and slash-goal handoff for the improvement loop.",
        "tone": "Forward-moving and bounded.",
        "proofBoundary": "NextRail creates the next plan; completion still requires validation evidence.",
        "aliases": ["next goal", "slash handoff"],
    },
    {
        "id": "version",
        "command": "shipguard version",
        "surfaceName": "ShipGuard VersionBeacon",
        "codename": "versionbeacon",
        "plainPurpose": "Print the toolkit version from VERSION.",
        "tone": "Tiny and exact.",
        "proofBoundary": "VersionBeacon reports the local package version, not GitHub release freshness.",
        "aliases": ["version", "local version"],
    },
]

NAMING_RULES = [
    "Keep CLI verbs literal and searchable; add personality through surface names, section labels, and report copy.",
    "Every branded name must sit beside a plain-purpose sentence so new users are never forced to decode the joke.",
    "Use short techy nouns from the ShipGuard universe: Deck, Dock, Radar, Forge, Lens, Port, Vault, Bay, Arena, Engine, Lab.",
    "Avoid app-specific branding in reusable surfaces. Ringly and Ilmify belong only in read-only product-QA evidence docs.",
    "Never let a vibe label weaken proof language. Release, payment, privacy, haptic, performance, and simulator claims stay literal.",
    "New public commands must add a surface row here, docs coverage, a routing/eval case when user-facing, and package/self-audit coverage.",
]

COMMAND_COVERAGE_TARGETS = [
    "shipguard brand",
    "shipguard ios brand",
    "shipguard init",
    "shipguard validate",
    "shipguard doctor",
    "shipguard web audit",
    "shipguard web plan",
    "shipguard backend audit",
    "shipguard backend plan",
    "shipguard cli audit",
    "shipguard cli plan",
    "shipguard policy",
    "shipguard score",
    "shipguard value-gauntlet",
    "shipguard pilot-bench",
    "shipguard autopsy",
    "shipguard arena",
    "shipguard transcript",
    "shipguard review-comment",
    "shipguard ci-gate",
    "shipguard ci-summary",
    "shipguard check-run",
    "shipguard sarif",
    "shipguard docs-check",
    "shipguard ios doctor",
    "shipguard ios inventory",
    "shipguard ios preview",
    "shipguard ios devspace",
    "shipguard ios devspace-check",
    "shipguard ios target-match",
    "shipguard ios codex-handoff",
    "shipguard ios plan",
    "shipguard ios prove",
    "shipguard ios launchdeck",
    "shipguard ios performance",
    "shipguard ios design",
    "shipguard ios modernize",
    "shipguard ios app-intelligence",
    "shipguard ios ai-readiness",
    "shipguard ios external-audit",
    "shipguard ios spec-workflow",
    "shipguard ios report-quality",
    "shipguard ios redact",
    "shipguard ios eval",
    "shipguard ios demo",
    "shipguard ios goals",
    "shipguard codex status",
    "shipguard leaderboard",
    "shipguard release-manifest",
    "shipguard release-index",
    "shipguard release-replay",
    "shipguard release-attest",
    "shipguard release-proof",
    "shipguard release-consume",
    "shipguard release-diff",
    "shipguard release-evidence",
    "shipguard self-audit",
    "shipguard next-goal",
    "shipguard version",
]

ARTIFACT_CALLSIGNS: list[dict[str, str]] = [
    {
        "pattern": "scripts/*.sh",
        "callSign": "Deckhand Scripts",
        "plainPurpose": "Small shell operators that move validation, packaging, and proof work forward.",
        "exampleLabel": "[deckhand]",
        "proofBoundary": "Keep physical script names literal; use the call sign in reports, logs, and docs headings.",
    },
    {
        "pattern": "scripts/ios_*.py",
        "callSign": "Sonar Modules",
        "plainPurpose": "Python scanners that read source, classify risk, and emit structured iOS reports.",
        "exampleLabel": "[sonar]",
        "proofBoundary": "Sonar modules inspect and route; they do not claim simulator or device proof.",
    },
    {
        "pattern": "tests/*_test.sh",
        "callSign": "Gauntlet Runs",
        "plainPurpose": "Repeatable tests that prove a ShipGuard behavior did not drift.",
        "exampleLabel": "[gauntlet]",
        "proofBoundary": "A gauntlet pass proves the named behavior only; broader release proof still needs package and CI lanes.",
    },
    {
        "pattern": "actions/*/action.yml",
        "callSign": "Signal Flares",
        "plainPurpose": "GitHub Action entrypoints that publish ShipGuard proof into CI.",
        "exampleLabel": "[flare]",
        "proofBoundary": "Signal flares package CI intent; a real workflow run is the publication proof.",
    },
    {
        "pattern": "fixtures/**",
        "callSign": "Proof Playground",
        "plainPurpose": "Synthetic public cases that make report quality and routing behavior testable.",
        "exampleLabel": "[playground]",
        "proofBoundary": "Fixture proof cannot be sold as private production-app proof.",
    },
    {
        "pattern": "*.json",
        "callSign": "Blackbox Receipts",
        "plainPurpose": "Machine-readable evidence, status, findings, and release metadata.",
        "exampleLabel": "[blackbox]",
        "proofBoundary": "A receipt is only as strong as the command and input that generated it.",
    },
    {
        "pattern": "*.md",
        "callSign": "Bridge Notes",
        "plainPurpose": "Human-readable handoffs, reports, docs, and release summaries.",
        "exampleLabel": "[bridge]",
        "proofBoundary": "Bridge notes explain proof; they do not replace raw JSON, logs, or command receipts.",
    },
    {
        "pattern": "*.log",
        "callSign": "Engine Tapes",
        "plainPurpose": "Raw command output, build traces, profiler notes, and failure trails.",
        "exampleLabel": "[engine]",
        "proofBoundary": "Engine tapes must stay unedited when used as evidence; redacted copies need a redaction report.",
    },
    {
        "pattern": "dist/*.tar.gz",
        "callSign": "Cargo Crates",
        "plainPurpose": "Release packages that users can unpack and verify outside the source checkout.",
        "exampleLabel": "[cargo]",
        "proofBoundary": "Cargo crates need manifest, replay, consume, and package tests before release claims.",
    },
    {
        "pattern": "plugins/**",
        "callSign": "Docking Gear",
        "plainPurpose": "Codex plugin metadata, skills, and MCP launch configuration.",
        "exampleLabel": "[dock]",
        "proofBoundary": "Docking gear updates require plugin refresh and a new Codex thread before claiming installed behavior.",
    },
]

PRODUCT_PLACES: list[dict[str, str]] = [
    {
        "name": "ShipGuard ShipYard",
        "codename": "shipyard",
        "plainPurpose": "The workshop layer for the whole toolkit: commands, docs, tests, fixtures, plugins, packages, and proof loops.",
        "whereItAppears": "README, Brand Deck reports, naming docs, release handoffs, and human-facing summaries.",
        "proofBoundary": "ShipYard names the workspace experience; it is not a repo rename and does not change automation paths.",
    }
]

REPORT_QUALITY_QUESTIONS = [
    "Does every public ShipGuard surface have a branded name, plain purpose, proof boundary, active-doc coverage, and package proof before release?",
    "Do active docs and plugin skill guidance avoid stale app-specific, generic plugin, or misspelled ShipGuard names while keeping stable CLI commands script-safe?",
    "Do scripts, tests, logs, fixtures, release packages, and plugin files have human-facing ShipGuard call signs without physically renaming automation-sensitive paths?",
    "Does ShipGuard ShipYard appear as the workshop-level product place without rebranding or renaming the repository paths?",
    "Does the next slash-plan and slash-goal include Brand Deck strict proof whenever a public surface is added or renamed?",
    "Should any repeated naming weakness become a deterministic Brand Deck eval case or public fixture instead of a one-off docs note?",
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
    parser = argparse.ArgumentParser(description="Audit ShipGuard's branded public surface scheme and future naming contract.")
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


def surface_commands(surface: dict[str, Any]) -> list[str]:
    commands = [surface["command"]]
    commands.extend(surface.get("relatedCommands", []))
    return commands


def all_surface_commands() -> set[str]:
    commands: set[str] = set()
    for surface in SURFACES:
        commands.update(surface_commands(surface))
    return commands


def command_is_wired(bin_text: str, command: str) -> bool:
    tokens = command.split()
    if len(tokens) < 2 or tokens[0] != "shipguard":
        return True
    if len(tokens) == 2:
        return f"{tokens[1]})" in bin_text or f'"{tokens[1]}"' in bin_text
    if tokens[1] == "ios" and len(tokens) >= 3:
        return f'"{tokens[2]}"' in bin_text or f"{tokens[2]})" in bin_text
    if tokens[1] == "codex" and len(tokens) >= 3:
        return f"cmd_{tokens[1]}" in bin_text and f'"{tokens[2]}"' in bin_text
    if tokens[1] == "leaderboard" and len(tokens) >= 2:
        return "cmd_leaderboard" in bin_text
    return f"{tokens[1]})" in bin_text or f"cmd_{tokens[1].replace('-', '_')}" in bin_text


def build_findings(root: Path) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    bin_text = read_if_exists(root / "bin" / "shipguard")
    doc_texts = {doc: read_if_exists(root / doc) for doc in ACTIVE_DOCS}
    combined_docs = "\n".join(doc_texts.values())
    covered_commands = all_surface_commands()

    for doc, text in doc_texts.items():
        if not text:
            findings.append(
                {
                    "severity": "high",
                    "category": "coverage",
                    "ruleId": "branding-active-doc-missing",
                    "evidence": doc,
                    "recommendation": f"Restore {doc} or remove it from the active naming coverage list.",
                    "proofGuidance": "Run shipguard brand --strict after restoring the file.",
                }
            )

    for command in COMMAND_COVERAGE_TARGETS:
        if command not in covered_commands:
            findings.append(
                {
                    "severity": "high",
                    "category": "surface-registry",
                    "ruleId": "branding-public-command-uncovered",
                    "evidence": command,
                    "recommendation": "Add a branded surface row with plain purpose, tone, proof boundary, and docs coverage.",
                    "proofGuidance": "Update scripts/ios_branding.py, docs/shipguard-naming.md, and tests/ios_branding_test.sh.",
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
        for command in surface_commands(surface):
            if not command_is_wired(bin_text, command):
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
                    "severity": "high",
                    "category": "docs",
                    "ruleId": "branding-surface-doc-mention-missing",
                    "evidence": surface["surfaceName"],
                    "recommendation": "Mention the branded surface in the active docs so users see the naming scheme.",
                    "proofGuidance": "Run shipguard brand --strict and docs-check after updating docs.",
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
                "proofGuidance": "Run tests/ios_branding_test.sh and shipguard brand --strict.",
            }
        )
    return findings


def build_report(root: Path, strict: bool) -> dict[str, Any]:
    findings = build_findings(root)
    blocking = [item for item in findings if item["severity"] == "high"]
    return {
        "schemaVersion": SCHEMA_VERSION,
        "tool": "shipguard brand",
        "surface": "ShipGuard Brand Deck",
        "compatibilityCommands": ["shipguard ios brand"],
        "intent": "shipguard-product-qa",
        "generatedAt": utc_now(),
        "status": "pass" if not blocking else "review",
        "strict": strict,
        "scopeBoundary": {
            "shipguardOnly": True,
            "targetAppsReadOnly": True,
            "purpose": "Grade ShipGuard's public naming system; do not rename target-app code.",
        },
        "surfaceCount": len(SURFACES),
        "brandPrinciple": "Friendly ship-control energy, but every joke has a proof receipt attached.",
        "namingRules": NAMING_RULES,
        "productPlaces": PRODUCT_PLACES,
        "surfaces": SURFACES,
        "artifactCallsigns": ARTIFACT_CALLSIGNS,
        "futureNamingContract": {
            "newCommandChecklist": [
                "Add the literal CLI command to bin/shipguard.",
                "Add a branded surface row to scripts/ios_branding.py.",
                "Mention the surface in docs/shipguard-naming.md and the command matrix.",
                "Add skill or eval routing when a user would ask for the surface by name.",
                "Add or reuse artifact call signs for any new script, log, fixture, package, or plugin family.",
                "Add self-audit, package, and focused tests before pushing.",
                "Run shipguard brand --strict; keep shipguard ios brand working as a compatibility route.",
            ],
            "toneGuardrail": "A surface can be funny only after its plain purpose and proof boundary are clear.",
            "publicInterfacePolicy": "Do not rename stable CLI commands, script files, report files, logs, fixtures, or package paths just for flavor; use ShipGuard surface names, call signs, and aliases while automation paths remain safe.",
        },
        "reportQualityQuestions": REPORT_QUALITY_QUESTIONS,
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
            "## Product Places",
            "",
            "| Name | Plain Purpose | Where It Appears | Proof Boundary |",
            "| --- | --- | --- | --- |",
        ]
    )
    for place in report["productPlaces"]:
        lines.append(
            f"| {place['name']} | {place['plainPurpose']} | {place['whereItAppears']} | {place['proofBoundary']} |"
        )
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
        command_cell = "<br>".join(f"`{command}`" for command in surface_commands(surface))
        lines.append(
            f"| {command_cell} | {surface['surfaceName']} | {surface['plainPurpose']} | {surface['proofBoundary']} |"
        )
    lines.extend(
        [
            "",
            "## Nitty-Gritty Call Signs",
            "",
            "| Path Pattern | Call Sign | Example Label | Plain Purpose | Proof Boundary |",
            "| --- | --- | --- | --- | --- |",
        ]
    )
    for item in report["artifactCallsigns"]:
        lines.append(
            f"| `{item['pattern']}` | {item['callSign']} | `{item['exampleLabel']}` | {item['plainPurpose']} | {item['proofBoundary']} |"
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
    lines.extend(["", "## Report Quality Questions", ""])
    for question in report["reportQualityQuestions"]:
        lines.append(f"- {question}")
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
