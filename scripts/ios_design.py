#!/usr/bin/env python3
"""Audit iOS UI/UX coherence, motion, haptics, preview routing, and icon direction."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import re
import sys
from pathlib import Path
from typing import Any

import ios_doctor
import ios_scan_scope


SCHEMA_VERSION = 1
APP_TYPES = [
    "auto",
    "utility",
    "game",
    "fitness",
    "health",
    "education",
    "kids",
    "creative",
    "commerce",
    "social",
    "finance",
    "saas",
]
SOURCE_SUFFIXES = {
    ".swift",
    ".plist",
    ".json",
    ".md",
    ".storekit",
    ".xcconfig",
    ".pbxproj",
}


APP_TYPE_KEYWORDS = {
    "utility": ["alarm", "timer", "reminder", "task", "notification", "widget", "shortcut", "productivity"],
    "game": ["spritekit", "scenekit", "gamekit", "skscene", "level", "score", "gameplay", "leaderboard"],
    "fitness": ["workout", "fitness", "exercise", "activity", "steps", "training", "run", "pace"],
    "health": ["healthkit", "health", "sleep", "heart", "medication", "symptom", "wellness", "mindfulness"],
    "education": ["lesson", "quiz", "course", "learn", "flashcard", "school", "student", "teacher"],
    "kids": ["kids", "child", "children", "parent", "guardian", "playful", "classroom"],
    "creative": ["camera", "photo", "drawing", "canvas", "editor", "design", "portfolio", "media"],
    "commerce": ["storekit", "purchase", "product", "checkout", "cart", "subscription", "entitlement", "price"],
    "social": ["profile", "share", "message", "chat", "follower", "friend", "community", "comment"],
    "finance": ["finance", "budget", "bank", "payment", "invoice", "transaction", "portfolio", "account"],
    "saas": ["dashboard", "workspace", "team", "admin", "organization", "project", "analytics", "crm"],
}


COLOR_PATTERN = re.compile(
    r"\b(?:Color|UIColor)\s*\(|\.(?:red|blue|green|purple|orange|yellow|pink|teal|mint|indigo|brown|cyan|gray|black|white)\b|#[0-9a-fA-F]{6}\b"
)
VISIBLE_STRING_PATTERN = re.compile(r"\b(?:Text|Button|Label|Toggle|Picker|NavigationTitle)\s*\(\s*\"([^\"]{1,90})\"")
NUMBER_PATTERN = re.compile(r"\d+")


def utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def fail(message: str) -> None:
    print(f"ios-design: {message}", file=sys.stderr)
    raise SystemExit(1)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Audit iOS UI/UX coherence, motion, haptics, preview routing, and app icon direction."
    )
    parser.add_argument("--path", default=".", help="iOS project or package root to scan")
    parser.add_argument("--out", help="Output directory for ios-design.md and ios-design.json")
    parser.add_argument("--app-type", choices=APP_TYPES, default="auto", help="Override inferred app type. Default: auto")
    parser.add_argument("--preview-out", help="Existing shipguard ios preview output directory to include as visual evidence")
    parser.add_argument("--icon-brief", action="store_true", help="Write app-icon-imagegen-brief.md with an ImageGen-ready prompt")
    parser.add_argument(
        "--shipguard-eval",
        action="store_true",
        help="Mark this scan as ShipGuard product QA only; findings must not become target-app work.",
    )
    parser.add_argument(
        "--shareable",
        action="store_true",
        help="Omit local absolute paths from JSON and Markdown so the report can be scored or shared without redaction.",
    )
    parser.add_argument("--json", action="store_true", help="Print JSON to stdout instead of Markdown")
    parser.add_argument("--markdown", action="store_true", help="Print Markdown to stdout")
    return parser.parse_args()


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="ignore")


def rel(path: Path, root: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return path.as_posix()


def report_path(path: Path, *, root: Path, shareable: bool, placeholder: str) -> str:
    if not shareable:
        return path.as_posix()
    try:
        relative = path.relative_to(root)
        return relative.as_posix() or "."
    except ValueError:
        return f"<{placeholder}>"


def source_records(root: Path) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    scan = ios_scan_scope.iter_files(root, SOURCE_SUFFIXES)
    records: list[dict[str, Any]] = []
    for path in scan.files:
        text = read_text(path)
        records.append({"path": path, "file": rel(path, root), "text": text, "lower": text.lower()})
    return records, ios_scan_scope.summary(scan)


def first_signal(records: list[dict[str, Any]], token: str) -> dict[str, str] | None:
    lowered = token.lower()
    for record in records:
        if lowered in record["lower"]:
            return {"token": token, "file": record["file"]}
    return None


def app_type_signal_weight(record: dict[str, Any]) -> int:
    file = str(record["file"])
    name = Path(file).name
    if file.endswith(".swift"):
        return 4
    if file.endswith((".pbxproj", ".plist", ".storekit", ".xcconfig")):
        return 3
    if file.endswith(".json"):
        return 2
    if name in {"AGENTS.md", "README.md", "BEST_PRACTICES.md"}:
        return 1
    if file.endswith(".md"):
        return 1
    return 1


def app_type_signal_cap(record: dict[str, Any]) -> int:
    name = Path(str(record["file"])).name
    if name in {"AGENTS.md", "README.md", "BEST_PRACTICES.md"}:
        return 1
    if str(record["file"]).endswith(".md"):
        return 2
    return 5


def collect_doctor_facts(root: Path) -> dict[str, Any]:
    report = ios_doctor.build_report(root)
    bundle_ids: list[str] = []
    target_names: list[str] = []
    deployment_targets: list[str] = []
    swift_versions: list[str] = []
    for project in report.get("xcode_projects", []):
        deployment_targets.extend(str(item) for item in project.get("deployment_targets", []))
        swift_versions.extend(str(item) for item in project.get("swift_versions", []))
        for target in project.get("target_details", []):
            if target.get("name"):
                target_names.append(str(target["name"]))
        for bundle_id in project.get("bundle_ids", []):
            bundle_ids.append(str(bundle_id))
    for package in report.get("swift_packages", []):
        if package.get("name"):
            target_names.append(str(package["name"]))
        if package.get("swift_tools_version"):
            swift_versions.append(str(package["swift_tools_version"]))
        deployment_targets.extend(str(item).replace("_", ".") for item in package.get("ios_platforms", []))
    return {
        "bundleIds": sorted(set(bundle_ids)),
        "targetNames": sorted(set(target_names)),
        "deploymentTargets": sorted(set(deployment_targets)),
        "swiftVersions": sorted(set(swift_versions)),
    }


def infer_app_type(records: list[dict[str, Any]], facts: dict[str, Any], override: str) -> dict[str, Any]:
    scores = {kind: 0 for kind in APP_TYPE_KEYWORDS}
    signals: list[dict[str, Any]] = []
    metadata = " ".join(facts["bundleIds"] + facts["targetNames"]).lower()

    for kind, keywords in APP_TYPE_KEYWORDS.items():
        for keyword in keywords:
            lowered_keyword = keyword.lower()
            count = 0
            best_signal: dict[str, Any] | None = None
            for record in records:
                raw_count = record["lower"].count(lowered_keyword)
                if not raw_count:
                    continue
                contribution = min(raw_count, app_type_signal_cap(record)) * app_type_signal_weight(record)
                count += contribution
                if best_signal is None or contribution > best_signal["count"]:
                    best_signal = {
                        "token": keyword,
                        "count": contribution,
                        "file": record["file"],
                    }
            if keyword.lower() in metadata:
                count += 6
                if best_signal is None:
                    best_signal = {"token": keyword, "count": 6, "file": "metadata"}
            if count:
                scores[kind] += count
                signals.append(
                    {
                        "appType": kind,
                        "token": keyword,
                        "count": count,
                        "file": best_signal["file"] if best_signal else "metadata",
                    }
                )

    # StoreKit/product files often describe monetization, not the app genre.
    # Prefer a close utility signal when alarms, widgets, notifications, or shortcuts are also present.
    if scores["utility"] and scores["commerce"] and scores["utility"] >= scores["commerce"] - 4:
        scores["utility"] += 4

    if override != "auto":
        return {
            "value": override,
            "inferred": max(scores, key=scores.get) if any(scores.values()) else "utility",
            "override": override,
            "confidence": 1.0,
            "scores": scores,
            "signals": sorted(signals, key=lambda item: (-int(item["count"]), item["appType"], item["token"]))[:12],
        }

    if not any(scores.values()):
        scores["utility"] = 1
        signals.append({"appType": "utility", "token": "default", "count": 1, "file": "fallback"})
    inferred = max(scores, key=scores.get)
    total = sum(scores.values())
    confidence = min(0.92, max(0.35, scores[inferred] / max(total, 1)))
    return {
        "value": inferred,
        "inferred": inferred,
        "override": None,
        "confidence": round(confidence, 2),
        "scores": scores,
        "signals": sorted(signals, key=lambda item: (-int(item["count"]), item["appType"], item["token"]))[:12],
    }


def extract_string_samples(records: list[dict[str, Any]], limit: int = 10) -> list[str]:
    samples: list[str] = []
    for record in records:
        for match in VISIBLE_STRING_PATTERN.finditer(record["text"]):
            value = match.group(1).strip()
            if value and value not in samples:
                samples.append(value)
                if len(samples) >= limit:
                    return samples
    return samples


def count_pattern(records: list[dict[str, Any]], pattern: re.Pattern[str]) -> int:
    return sum(len(pattern.findall(record["text"])) for record in records)


def collect_design_dna(records: list[dict[str, Any]]) -> dict[str, Any]:
    swift_text = "\n".join(record["text"] for record in records if record["file"].endswith(".swift"))
    lower_text = swift_text.lower()
    component_tokens = {
        "NavigationStack": swift_text.count("NavigationStack"),
        "TabView": swift_text.count("TabView"),
        "List": swift_text.count("List("),
        "Form": swift_text.count("Form("),
        "Button": swift_text.count("Button("),
        "Toggle": swift_text.count("Toggle("),
        "Picker": swift_text.count("Picker("),
        "ProgressView": swift_text.count("ProgressView"),
    }
    return {
        "colors": {
            "colorSignals": count_pattern(records, COLOR_PATTERN),
            "gradients": swift_text.count("LinearGradient") + swift_text.count("RadialGradient") + swift_text.count("AngularGradient"),
            "materials": swift_text.count("Material") + swift_text.count(".thinMaterial") + swift_text.count(".regularMaterial"),
        },
        "typography": {
            "fontModifiers": swift_text.count(".font(") + swift_text.count("Font."),
            "dynamicTypeSignals": swift_text.count("dynamicTypeSize") + swift_text.count("@ScaledMetric") + swift_text.count("UIFontMetrics"),
            "lineLimitSignals": swift_text.count(".lineLimit("),
        },
        "components": component_tokens,
        "copyTone": {
            "visibleStringCount": len(VISIBLE_STRING_PATTERN.findall(swift_text)),
            "samples": extract_string_samples(records),
            "localizationSignals": swift_text.count("LocalizedStringResource") + swift_text.count("String(localized:") + swift_text.count("NSLocalizedString"),
        },
        "iconography": {
            "sfSymbolSignals": swift_text.count("systemName:") + swift_text.count("Label("),
            "customImageSignals": swift_text.count("Image(\""),
            "symbolEffectSignals": swift_text.count(".symbolEffect"),
        },
        "layout": {
            "roundedSignals": swift_text.count("RoundedRectangle") + swift_text.count(".cornerRadius(") + swift_text.count(".clipShape("),
            "shadowSignals": swift_text.count(".shadow("),
            "blurSignals": swift_text.count(".blur(") + swift_text.count("VisualEffectBlur"),
            "cardNameSignals": lower_text.count("card"),
        },
        "motion": {
            "withAnimationSignals": swift_text.count("withAnimation"),
            "animationModifiers": swift_text.count(".animation("),
            "repeatForeverSignals": swift_text.count("repeatForever"),
            "timelineViewSignals": swift_text.count("TimelineView"),
            "reduceMotionSignals": swift_text.count("accessibilityReduceMotion") + swift_text.count("isReduceMotionEnabled"),
        },
        "haptics": {
            "uikitFeedbackSignals": swift_text.count("UIImpactFeedbackGenerator")
            + swift_text.count("UISelectionFeedbackGenerator")
            + swift_text.count("UINotificationFeedbackGenerator"),
            "coreHapticsSignals": swift_text.count("CoreHaptics") + swift_text.count("CHHapticEngine"),
            "sensoryFeedbackSignals": swift_text.count(".sensoryFeedback("),
        },
        "navigation": {
            "navigationStackSignals": swift_text.count("NavigationStack") + swift_text.count("NavigationView"),
            "sheetSignals": swift_text.count(".sheet(") + swift_text.count(".popover("),
            "deepLinkSignals": swift_text.count("onOpenURL") + swift_text.count("openURL") + swift_text.count("NavigationPath"),
        },
    }


def finding(
    *,
    rule_id: str,
    severity: str,
    category: str,
    title: str,
    evidence: str,
    recommendation: str,
    proof: str,
) -> dict[str, str]:
    return {
        "ruleId": rule_id,
        "severity": severity,
        "category": category,
        "title": title,
        "evidence": evidence,
        "recommendation": recommendation,
        "proof": proof,
        "proofGuidance": proof,
    }


def build_findings(app_type: str, dna: dict[str, Any], preview: dict[str, Any], icon_brief: bool) -> list[dict[str, str]]:
    findings: list[dict[str, str]] = []
    motion = dna["motion"]
    layout = dna["layout"]
    typography = dna["typography"]
    copy_tone = dna["copyTone"]
    iconography = dna["iconography"]
    components = dna["components"]
    haptics = dna["haptics"]

    motion_count = motion["withAnimationSignals"] + motion["animationModifiers"] + motion["repeatForeverSignals"] + motion["timelineViewSignals"]
    if motion_count and motion["reduceMotionSignals"] == 0:
        findings.append(
            finding(
                rule_id="motion-reduced-motion-gate",
                severity="high",
                category="Motion",
                title="Motion exists without a reduced-motion signal",
                evidence=f"{motion_count} motion signal(s) detected and no reduced-motion API signal found.",
                recommendation="Add a reduced-motion branch before approving animation polish or motion-heavy UI.",
                proof="Run the relevant surface with Reduce Motion enabled and record screenshot or UI-test evidence.",
            )
        )
    if motion["repeatForeverSignals"] or motion["timelineViewSignals"]:
        severity = "opportunity" if app_type in {"game", "kids", "creative"} else "review"
        findings.append(
            finding(
                rule_id="motion-continuous-animation-density",
                severity=severity,
                category="Motion",
                title="Continuous animation needs app-type justification",
                evidence=f"repeatForever={motion['repeatForeverSignals']}, TimelineView={motion['timelineViewSignals']}.",
                recommendation="Use the frequency gate: frequent or utility interactions should be instant or subtle; game/kids moments still need pause/reduced-motion behavior.",
                proof="Capture the screen after repeated use and test Reduce Motion; add profiler proof if animation is always active.",
            )
        )
    if layout["shadowSignals"] >= 3 or (layout["blurSignals"] and layout["shadowSignals"]):
        findings.append(
            finding(
                rule_id="visual-effects-stack-review",
                severity="review",
                category="Design DNA",
                title="Blur and shadow stack can weaken visual coherence",
                evidence=f"blur={layout['blurSignals']}, shadow={layout['shadowSignals']}.",
                recommendation="Reserve heavy blur/shadow for one semantic layer; use spacing, typography, and grouped surfaces first.",
                proof="Compare a before/after screenshot in the iPhone preview and check legibility in light/dark appearances.",
            )
        )
    if copy_tone["visibleStringCount"] and copy_tone["localizationSignals"] == 0:
        findings.append(
            finding(
                rule_id="visible-copy-localization-gate",
                severity="review",
                category="UX Writing",
                title="Visible copy lacks localization signals",
                evidence=f"{copy_tone['visibleStringCount']} visible string literal(s) detected.",
                recommendation="Route user-visible copy through the app's localization system before treating the design language as reusable.",
                proof="Run a localization or pseudo-localization check for the affected surface.",
            )
        )
    if typography["fontModifiers"] == 0 and typography["dynamicTypeSignals"] == 0:
        findings.append(
            finding(
                rule_id="typography-dynamic-type-gap",
                severity="opportunity",
                category="Accessibility",
                title="Typography system is not visible from source signals",
                evidence="No .font, Font, Dynamic Type, @ScaledMetric, or UIFontMetrics signal was detected.",
                recommendation="Define the intended type scale and verify compact width plus larger Dynamic Type before visual polish claims.",
                proof="Capture compact and larger Dynamic Type screenshots for the primary flow.",
            )
        )
    if sum(components.values()) >= 3 and iconography["sfSymbolSignals"] == 0 and iconography["customImageSignals"] == 0:
        findings.append(
            finding(
                rule_id="iconography-language-missing",
                severity="opportunity",
                category="Design DNA",
                title="No iconography language was detected",
                evidence="No SF Symbol or custom Image signal was detected in SwiftUI source.",
                recommendation="Choose whether the app's DNA is text-first or icon-assisted; use SF Symbols for tools and reserve custom art for brand moments.",
                proof="Review the preview for scan speed and VoiceOver labels before adding more icons.",
            )
        )
    if haptics["uikitFeedbackSignals"] == 0 and haptics["coreHapticsSignals"] == 0 and haptics["sensoryFeedbackSignals"] == 0:
        findings.append(
            finding(
                rule_id="haptics-blueprint-missing",
                severity="opportunity",
                category="Haptics",
                title="No haptic language was detected",
                evidence="No UIKit feedback generator, CoreHaptics, or sensoryFeedback signal was detected.",
                recommendation="Define haptics by interaction type before adding one-off tactile effects.",
                proof="Physical-device proof is required before claiming haptic quality.",
            )
        )
    if preview["status"] == "not-provided":
        findings.append(
            finding(
                rule_id="preview-proof-not-provided",
                severity="opportunity",
                category="Preview",
                title="Design audit has no live iPhone preview evidence",
                evidence="No --preview-out directory was provided.",
                recommendation="Run shipguard ios preview for a phone-shaped visual proof loop; use ios devspace when ChatGPT should plan from that widget.",
                proof="Attach preview-events.jsonl, handoff.md, and refreshed screenshot evidence for visual claims.",
            )
        )
    if not icon_brief:
        findings.append(
            finding(
                rule_id="icon-imagegen-brief-available",
                severity="opportunity",
                category="Icon",
                title="App icon ImageGen handoff was not requested",
                evidence="--icon-brief was not passed.",
                recommendation="Use --icon-brief when app identity or App Store polish is in scope; do not draft production icons as CSS or local SVG art.",
                proof="Review generated app-icon-imagegen-brief.md, then create bitmap candidates with ChatGPT ImageGen.",
            )
        )
    return findings


def motion_blueprint(app_type: str) -> dict[str, Any]:
    if app_type in {"game", "kids", "creative", "education"}:
        return {
            "perspective": {"primary": "Jakub", "secondary": "Jhey", "selective": "Emil for high-frequency controls"},
            "durationGuidance": "Expressive moments can run longer, but core controls should still feel instant after repeated use.",
            "frequencyGate": [
                "Rare reward or onboarding moments may be delightful.",
                "Daily task controls should stay subtle and fast.",
                "High-frequency or keyboard-driven actions should avoid noticeable animation.",
            ],
            "rules": [
                "Respect Reduce Motion for every animation.",
                "Avoid unpausable looping motion unless the app type truly depends on it.",
                "Use motion for orientation, feedback, and state continuity before decoration.",
            ],
        }
    if app_type in {"fitness", "health"}:
        return {
            "perspective": {"primary": "Jakub", "secondary": "Emil", "selective": "Jhey for celebration moments"},
            "durationGuidance": "Calm 180-350ms transitions; avoid nervous loops on health or progress states.",
            "frequencyGate": [
                "Workout or health logging should not be slowed by flourish.",
                "Milestone completion can be more expressive.",
                "Sensitive states need stable, legible transitions.",
            ],
            "rules": [
                "Avoid vestibular triggers, parallax, and unpausable movement.",
                "Keep progress feedback readable without motion.",
                "Use before/after preview proof for confidence-critical screens.",
            ],
        }
    return {
        "perspective": {"primary": "Emil", "secondary": "Jakub", "selective": "Jhey for onboarding or brand moments"},
        "durationGuidance": "Frequent utility interactions should be instant to 180ms; occasional transitions can sit around 180-250ms.",
        "frequencyGate": [
            "Frequent interactions should have no animation or an almost instant transition.",
            "Occasional state changes should be subtle and purposeful.",
            "Rare onboarding or empty-state moments may carry light delight.",
        ],
        "rules": [
            "Do not animate keyboard-initiated actions.",
            "Use transform and opacity instead of layout properties.",
            "Avoid pulse, glow, stagger spam, and bounce on utility controls.",
        ],
    }


def haptics_blueprint(app_type: str) -> dict[str, Any]:
    if app_type in {"game", "kids", "creative"}:
        tone = "expressive but still sparse"
    elif app_type in {"health", "fitness", "finance", "commerce"}:
        tone = "calm, confirmation-focused, and trust-preserving"
    else:
        tone = "quiet and utility-focused"
    return {
        "tone": tone,
        "deviceProofRequired": True,
        "patterns": [
            {"interaction": "low-stakes selection", "recommendedFeedback": "UISelectionFeedbackGenerator or sensoryFeedback(.selection)"},
            {"interaction": "direct manipulation or snap", "recommendedFeedback": "Light UIImpactFeedbackGenerator only at the final settled state"},
            {"interaction": "success, warning, error", "recommendedFeedback": "UINotificationFeedbackGenerator with matching semantic type"},
            {"interaction": "high-frequency controls", "recommendedFeedback": "No haptic feedback unless user value is proven on device"},
        ],
    }


def read_json_file(path: Path) -> dict[str, Any] | None:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None


def preview_evidence(preview_out: str | None, *, root: Path, shareable: bool) -> dict[str, Any]:
    if not preview_out:
        return {
            "status": "not-provided",
            "recommendedCommands": [
                "shipguard ios preview --out /tmp/ios-shipguard-preview",
                "shipguard ios devspace --port 8787 --preview-out /tmp/ios-shipguard-preview --bearer-token-env SHIPGUARD_DEVSPACE_TOKEN",
            ],
        }
    preview_root = Path(preview_out).expanduser().resolve()
    session = read_json_file(preview_root / "session.json")
    handoff = read_json_file(preview_root / "handoff.json")
    events_path = preview_root / "preview-events.jsonl"
    events: list[dict[str, Any]] = []
    if events_path.is_file():
        for raw in events_path.read_text(encoding="utf-8", errors="ignore").splitlines():
            raw = raw.strip()
            if not raw:
                continue
            try:
                events.append(json.loads(raw))
            except json.JSONDecodeError:
                continue
    latest = events[-1] if events else None
    return {
        "status": "provided" if preview_root.is_dir() else "missing",
        "path": report_path(preview_root, root=root, shareable=shareable, placeholder="preview-out"),
        "sessionFound": session is not None,
        "handoffFound": handoff is not None,
        "screenshotFound": (preview_root / "last-screenshot.png").is_file(),
        "eventCount": len(events),
        "latestEventType": latest.get("type") if isinstance(latest, dict) else None,
        "captureMode": session.get("captureMode") if isinstance(session, dict) else None,
        "targetResolutionStatus": (
            handoff.get("targetResolution", {}).get("status") if isinstance(handoff, dict) else None
        ),
    }


def build_icon_brief(app_type: str, app_type_report: dict[str, Any], dna: dict[str, Any]) -> dict[str, Any]:
    color_count = dna["colors"]["colorSignals"]
    visual_direction = {
        "utility": "clear, trustworthy, tool-like, and instantly recognizable at small sizes",
        "game": "bold, playful, high-contrast, and characterful without tiny UI details",
        "fitness": "energetic, clean, progress-oriented, and confidence-building",
        "health": "calm, humane, privacy-respecting, and clinically legible without feeling cold",
        "education": "friendly, clear, and learning-oriented with one memorable symbol",
        "kids": "warm, playful, simple, and safe-feeling",
        "creative": "expressive, crafted, and visually distinctive",
        "commerce": "trustworthy, premium, and product-focused",
        "social": "human, lively, and relationship-oriented",
        "finance": "stable, precise, and confidence-building",
        "saas": "sharp, professional, and system-like",
    }.get(app_type, "clear, trustworthy, and product-specific")
    prompt = (
        "Create three production-quality iOS app icon concepts for a "
        f"{app_type} app. The icon should feel {visual_direction}. "
        "Use one strong metaphor, simple geometry, strong silhouette, and no readable text. "
        "Design for App Store 1024x1024 usage and make sure it remains recognizable at 60x60. "
        f"The scanned source exposed {color_count} color signal(s); keep the palette coherent rather than decorative. "
        "Do not create a device mockup, CSS illustration, SVG-style wire art, or a screenshot of an app UI. "
        "Return polished bitmap-style icon artwork only."
    )
    return {
        "prompt": prompt,
        "appType": app_type,
        "confidence": app_type_report["confidence"],
        "assetChecklist": [
            "Generate square 1024x1024 PNG candidates.",
            "Check recognition at 60x60 and 29x29 sizes.",
            "Avoid text, tiny interface details, transparent backgrounds, and device frames.",
            "Keep final App Store asset local until the user approves sharing.",
            "Export through the app's normal asset catalog after a bitmap candidate is selected.",
        ],
        "handoff": "Use ChatGPT ImageGen for bitmap candidates; ShipGuard does not generate CSS or SVG icon art.",
    }


def shipguard_eval_boundary() -> dict[str, Any]:
    return {
        "targetAppsReadOnly": True,
        "shipguardOnly": True,
        "allowedUses": [
            "Evaluate ShipGuard design-report quality.",
            "Identify missing or noisy UI/UX, motion, haptic, preview, or icon guidance.",
            "Create redacted public fixtures or eval cases in ShipGuard.",
        ],
        "forbiddenUses": [
            "Do not edit the scanned app from this run.",
            "Do not create target-app redesign, icon, or haptic implementation tasks from this run.",
            "Do not present target-app findings as the active development goal.",
        ],
    }


def shipguard_eval_questions() -> list[str]:
    return [
        "Did the report tailor advice to the app type instead of applying one universal design rule?",
        "Did it separate design-system coherence findings from target-app implementation work?",
        "Did preview and Devspace guidance make the iPhone visual proof path obvious?",
        "Which private-app observation should become a public design fixture or eval case?",
    ]


def status_for(findings: list[dict[str, str]]) -> str:
    if any(item["severity"] == "high" for item in findings):
        return "blocked"
    if findings:
        return "review"
    return "pass"


def build_report(
    root: Path,
    *,
    app_type_override: str,
    preview_out: str | None,
    icon_brief: bool,
    shipguard_eval: bool = False,
    shareable: bool = False,
) -> dict[str, Any]:
    if not root.exists():
        fail(f"path not found: {root}")
    if not root.is_dir():
        fail(f"path must be a directory: {root}")
    records, scan_scope = source_records(root)
    facts = collect_doctor_facts(root)
    app_type = infer_app_type(records, facts, app_type_override)
    dna = collect_design_dna(records)
    preview = preview_evidence(preview_out, root=root, shareable=shareable)
    icon = build_icon_brief(app_type["value"], app_type, dna) if icon_brief else None
    findings = build_findings(app_type["value"], dna, preview, icon_brief)
    return {
        "schemaVersion": SCHEMA_VERSION,
        "tool": "shipguard ios design",
        "generatedAt": utc_now(),
        "intent": "shipguard-evaluation" if shipguard_eval else "app-development",
        "status": status_for(findings),
        "root": report_path(root, root=root, shareable=shareable, placeholder="scanned-app"),
        "shareability": {
            "mode": "shareable" if shareable else "local",
            "localAbsolutePathsIncluded": not shareable,
            "note": "Use --shareable before moving this design report into ChatGPT, GitHub, docs, benchmark fixtures, or release evidence."
            if not shareable
            else "Local absolute paths are omitted from report fields; still run report-quality before public sharing.",
        },
        "appType": app_type,
        "sourceSummary": {
            "filesScanned": len(records),
            "swiftFiles": sum(1 for item in records if item["file"].endswith(".swift")),
            "scanScope": scan_scope,
            "swiftVersions": facts["swiftVersions"],
            "deploymentTargets": facts["deploymentTargets"],
            "targets": facts["targetNames"],
            "bundleIds": facts["bundleIds"],
        },
        "designDNA": dna,
        "findings": findings,
        "motionBlueprint": motion_blueprint(app_type["value"]),
        "hapticsBlueprint": haptics_blueprint(app_type["value"]),
        "previewEvidence": preview,
        "iconBrief": icon,
        "scopeBoundary": shipguard_eval_boundary() if shipguard_eval else None,
        "reportQualityQuestions": shipguard_eval_questions() if shipguard_eval else [],
        "nextProof": [
            "Use shipguard ios preview for phone-shaped visual evidence before design claims.",
            "Use shipguard ios devspace when ChatGPT should plan from the preview widget; model choice happens in ChatGPT, not ShipGuard.",
            "Use physical-device proof before claiming haptic quality.",
            "Use ChatGPT ImageGen for icon bitmap candidates after reviewing app-icon-imagegen-brief.md.",
        ],
    }


def render_icon_brief(report: dict[str, Any]) -> str:
    icon = report["iconBrief"]
    if not icon:
        return ""
    lines = [
        "# App Icon ImageGen Brief",
        "",
        f"- App type: `{icon['appType']}`",
        f"- App-type confidence: {icon['confidence']}",
        "- Generation tool: ChatGPT ImageGen",
        "- Local generation policy: ShipGuard does not create CSS or SVG icon art.",
        "",
        "## Prompt",
        "",
        icon["prompt"],
        "",
        "## Asset Checklist",
        "",
    ]
    for item in icon["assetChecklist"]:
        lines.append(f"- {item}")
    lines.extend(["", "## Handoff", "", icon["handoff"], ""])
    return "\n".join(lines)


def render_markdown(report: dict[str, Any]) -> str:
    app_type = report["appType"]
    dna = report["designDNA"]
    motion = report["motionBlueprint"]
    haptics = report["hapticsBlueprint"]
    preview = report["previewEvidence"]
    lines = [
        "# iOS Design QA Audit",
        "",
        f"- Status: `{report['status']}`",
        f"- Intent: `{report['intent']}`",
        f"- Shareability mode: `{report['shareability']['mode']}`",
        f"- App type: `{app_type['value']}`",
        f"- App-type confidence: {app_type['confidence']}",
        f"- Swift files: {report['sourceSummary']['swiftFiles']}",
        f"- Skipped generated/proof/cache directories: {report['sourceSummary']['scanScope']['skippedDirectoryCount']}",
        "",
    ]
    if report["intent"] == "shipguard-evaluation":
        boundary = report["scopeBoundary"]
        lines.extend(
            [
                "## ShipGuard Evaluation Boundary",
                "",
                "- This scan is ShipGuard product QA only.",
                "- The scanned app is a read-only input; do not edit it from this run.",
                "- Use findings to improve ShipGuard design rules, report shape, docs, or fixtures.",
                "- Do not turn findings into target-app redesign, icon, or haptic tasks without a separate app-work request.",
                "",
                "Allowed uses: " + "; ".join(boundary["allowedUses"]),
                "",
                "Forbidden uses: " + "; ".join(boundary["forbiddenUses"]),
                "",
            ]
        )

    lines.extend(["## App Type Signals", "", "| App Type | Score |", "| --- | ---: |"])
    for kind, score in sorted(app_type["scores"].items(), key=lambda item: (-int(item[1]), item[0])):
        if score:
            lines.append(f"| {kind} | {score} |")
    if app_type["signals"]:
        lines.extend(["", "Top signals:"])
        for signal in app_type["signals"][:6]:
            lines.append(f"- `{signal['token']}` -> {signal['appType']} ({signal['count']}) in {signal['file']}")

    scan_scope = report["sourceSummary"]["scanScope"]
    if scan_scope["skippedDirectories"]:
        lines.extend(["", "Scan-scope exclusions:"])
        for directory in scan_scope["skippedDirectories"][:8]:
            lines.append(f"- `{directory}`")
        if scan_scope["skippedDirectoryListTruncated"]:
            lines.append("- Additional skipped directories are listed in JSON.")

    lines.extend(
        [
            "",
            "## Design DNA",
            "",
            f"- Color signals: {dna['colors']['colorSignals']}; gradients: {dna['colors']['gradients']}; materials: {dna['colors']['materials']}",
            f"- Typography signals: {dna['typography']['fontModifiers']}; Dynamic Type signals: {dna['typography']['dynamicTypeSignals']}",
            f"- SF Symbol signals: {dna['iconography']['sfSymbolSignals']}; custom images: {dna['iconography']['customImageSignals']}",
            f"- Motion signals: {dna['motion']['withAnimationSignals'] + dna['motion']['animationModifiers']}; repeatForever: {dna['motion']['repeatForeverSignals']}; TimelineView: {dna['motion']['timelineViewSignals']}",
            f"- Haptic signals: {dna['haptics']['uikitFeedbackSignals'] + dna['haptics']['coreHapticsSignals'] + dna['haptics']['sensoryFeedbackSignals']}",
        ]
    )
    if dna["copyTone"]["samples"]:
        lines.append("- Copy samples: " + "; ".join(f"`{item}`" for item in dna["copyTone"]["samples"][:5]))

    lines.extend(["", "## Findings", ""])
    if report["findings"]:
        lines.extend(["| Severity | Category | Rule | Finding | Recommendation | Proof |", "| --- | --- | --- | --- | --- | --- |"])
        for item in report["findings"]:
            lines.append(
                f"| {item['severity']} | {item['category']} | `{item['ruleId']}` | {item['title']} | {item['recommendation']} | {item['proof']} |"
            )
    else:
        lines.append("No design QA findings were detected.")

    lines.extend(
        [
            "",
            "## Motion Blueprint",
            "",
            f"- Primary lens: {motion['perspective']['primary']}",
            f"- Secondary lens: {motion['perspective']['secondary']}",
            f"- Selective lens: {motion['perspective']['selective']}",
            f"- Duration guidance: {motion['durationGuidance']}",
            "",
            "Frequency gate:",
        ]
    )
    for item in motion["frequencyGate"]:
        lines.append(f"- {item}")
    lines.append("")
    lines.append("Rules:")
    for item in motion["rules"]:
        lines.append(f"- {item}")

    lines.extend(["", "## Haptics Blueprint", "", f"- Tone: {haptics['tone']}", "- Device proof required: true", ""])
    for item in haptics["patterns"]:
        lines.append(f"- {item['interaction']}: {item['recommendedFeedback']}")

    lines.extend(["", "## Preview And Devspace", ""])
    if preview["status"] == "provided":
        lines.extend(
            [
                f"- Preview directory: `{preview['path']}`",
                f"- Session found: {preview['sessionFound']}",
                f"- Handoff found: {preview['handoffFound']}",
                f"- Screenshot found: {preview['screenshotFound']}",
                f"- Event count: {preview['eventCount']}",
                f"- Target resolution: {preview['targetResolutionStatus'] or 'unknown'}",
            ]
        )
    else:
        lines.extend(
            [
                "- No preview directory was supplied.",
                "- Run `shipguard ios preview --out /tmp/ios-shipguard-preview` for a phone-shaped visual proof loop.",
                "- Run `shipguard ios devspace --port 8787 --preview-out /tmp/ios-shipguard-preview --bearer-token-env SHIPGUARD_DEVSPACE_TOKEN` when ChatGPT should plan from the preview widget.",
                "- ChatGPT model selection happens in ChatGPT; ShipGuard exposes the MCP/App bridge but cannot force a model.",
            ]
        )

    if report["iconBrief"]:
        lines.extend(
            [
                "",
                "## App Icon ImageGen Brief",
                "",
                "- Wrote `app-icon-imagegen-brief.md` with a ChatGPT ImageGen prompt.",
                "- ShipGuard does not create CSS or SVG icon art.",
            ]
        )

    if report["reportQualityQuestions"]:
        lines.extend(["", "## Report Quality Questions", ""])
        for question in report["reportQualityQuestions"]:
            lines.append(f"- {question}")

    lines.extend(["", "## Next Proof", ""])
    for item in report["nextProof"]:
        lines.append(f"- {item}")
    lines.append("")
    return "\n".join(lines)


def write_outputs(report: dict[str, Any], out_dir: Path) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "ios-design.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (out_dir / "ios-design.md").write_text(render_markdown(report), encoding="utf-8")
    print(f"wrote: {out_dir / 'ios-design.md'}")
    print(f"wrote: {out_dir / 'ios-design.json'}")
    if report["iconBrief"]:
        (out_dir / "app-icon-imagegen-brief.md").write_text(render_icon_brief(report), encoding="utf-8")
        print(f"wrote: {out_dir / 'app-icon-imagegen-brief.md'}")
    print(f"status: {report['status']}")


def main() -> int:
    args = parse_args()
    root = Path(args.path).expanduser().resolve()
    report = build_report(
        root,
        app_type_override=args.app_type,
        preview_out=args.preview_out,
        icon_brief=args.icon_brief,
        shipguard_eval=args.shipguard_eval,
        shareable=args.shareable,
    )
    if args.out:
        write_outputs(report, Path(args.out).expanduser().resolve())
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    elif args.markdown or not args.out:
        print(render_markdown(report))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
