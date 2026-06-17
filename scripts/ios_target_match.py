#!/usr/bin/env python3
"""Match ShipGuard preview events to XcodeBuildMCP UI snapshot candidates."""

from __future__ import annotations

import argparse
import json
import math
import re
import sys
from pathlib import Path
from typing import Any


STOPWORDS = {
    "a",
    "an",
    "and",
    "change",
    "clearer",
    "fix",
    "for",
    "here",
    "make",
    "please",
    "rename",
    "should",
    "tap",
    "the",
    "this",
    "to",
}
TEXT_KEYS = (
    "label",
    "title",
    "text",
    "value",
    "name",
    "accessibilityLabel",
    "accessibilityIdentifier",
    "identifier",
    "placeholder",
    "id",
)
REF_KEYS = ("elementRef", "element_ref", "elementId", "elementID", "id", "identifier", "accessibilityIdentifier")
ROLE_KEYS = ("role", "type", "elementType", "className", "class", "trait", "traits")
CHILD_KEYS = ("children", "elements", "nodes", "subviews", "views", "items", "windows", "tree", "ui")
GEOMETRY_KEYS = {"frame", "bounds", "rect", "Frame", "Bounds", "Rect", "screen", "viewport", "window", "size"}


def fail(message: str) -> None:
    print(f"ios-target-match: {message}", file=sys.stderr)
    raise SystemExit(1)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Rank XcodeBuildMCP describe_ui/snapshot_ui elements against a ShipGuard preview handoff."
    )
    parser.add_argument("--handoff", required=True, help="JSON file from preview /api/handoff or Devspace preview_handoff.")
    parser.add_argument("--snapshot", required=True, help="JSON file from XcodeBuildMCP describe_ui or snapshot_ui.")
    parser.add_argument("--out", help="Optional output directory for ios-target-match.json and ios-target-match.md.")
    parser.add_argument("--max-candidates", type=int, default=5, help="Number of candidates to return. Default: 5.")
    return parser.parse_args()


def safe_text(value: Any, limit: int = 1000) -> str:
    if not isinstance(value, str):
        return ""
    return value.strip()[:limit]


def read_json(path: str) -> Any:
    try:
        return json.loads(Path(path).expanduser().read_text(encoding="utf-8"))
    except FileNotFoundError:
        fail(f"file not found: {path}")
    except json.JSONDecodeError as exc:
        fail(f"invalid JSON in {path}: {exc}")


def as_number(value: Any) -> float | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        try:
            return float(value)
        except ValueError:
            return None
    return None


def tokens(value: str) -> set[str]:
    return {token for token in re.findall(r"[a-z0-9]+", value.lower()) if token not in STOPWORDS and len(token) > 1}


def nested_dict(value: dict[str, Any], keys: tuple[str, ...]) -> dict[str, Any] | None:
    for key in keys:
        nested = value.get(key)
        if isinstance(nested, dict):
            return nested
    return None


def extract_frame(value: dict[str, Any]) -> dict[str, float] | None:
    frame_source = nested_dict(value, ("frame", "bounds", "rect", "Frame", "Bounds", "Rect")) or value
    x = as_number(frame_source.get("x", frame_source.get("X")))
    y = as_number(frame_source.get("y", frame_source.get("Y")))
    width = as_number(frame_source.get("width", frame_source.get("Width", frame_source.get("w"))))
    height = as_number(frame_source.get("height", frame_source.get("Height", frame_source.get("h"))))
    if x is None or y is None or width is None or height is None:
        return None
    if width < 0 or height < 0:
        return None
    return {"x": x, "y": y, "width": width, "height": height}


def extract_size(value: Any) -> tuple[float, float] | None:
    if not isinstance(value, dict):
        return None
    for key in ("screen", "viewport", "window", "bounds", "frame", "size"):
        nested = value.get(key)
        if isinstance(nested, dict):
            width = as_number(nested.get("width", nested.get("Width", nested.get("w"))))
            height = as_number(nested.get("height", nested.get("Height", nested.get("h"))))
            if width and height:
                return width, height
    width = as_number(value.get("width", value.get("Width", value.get("w"))))
    height = as_number(value.get("height", value.get("Height", value.get("h"))))
    if width and height:
        return width, height
    return None


def text_values(value: dict[str, Any]) -> list[str]:
    rows = []
    for key in TEXT_KEYS:
        text = safe_text(value.get(key), 220)
        if text:
            rows.append(text)
    return rows


def first_text(value: dict[str, Any], keys: tuple[str, ...]) -> str | None:
    for key in keys:
        text = safe_text(value.get(key), 220)
        if text:
            return text
    return None


def looks_like_element(value: dict[str, Any]) -> bool:
    if extract_frame(value):
        return True
    if first_text(value, REF_KEYS) or first_text(value, TEXT_KEYS) or first_text(value, ROLE_KEYS):
        return True
    return False


def bool_value(value: Any) -> bool | None:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        lowered = value.lower()
        if lowered in {"true", "yes", "1"}:
            return True
        if lowered in {"false", "no", "0"}:
            return False
    return None


def normalize_element(value: dict[str, Any], path: str) -> dict[str, Any]:
    ref = first_text(value, REF_KEYS)
    role = first_text(value, ROLE_KEYS)
    texts = text_values(value)
    frame = extract_frame(value)
    hidden = bool_value(value.get("hidden", value.get("isHidden")))
    enabled = bool_value(value.get("enabled", value.get("isEnabled")))
    hittable = bool_value(value.get("hittable", value.get("isHittable")))
    return {
        "path": path,
        "elementRef": ref,
        "label": texts[0] if texts else None,
        "texts": texts,
        "role": role,
        "frame": frame,
        "hidden": hidden,
        "enabled": enabled,
        "hittable": hittable,
        "raw": {key: value.get(key) for key in sorted(value.keys()) if key not in CHILD_KEYS},
    }


def flatten_elements(value: Any, path: str = "$") -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    if isinstance(value, dict):
        if looks_like_element(value):
            rows.append(normalize_element(value, path))
        for key, child in value.items():
            if key in {"raw"} or key in GEOMETRY_KEYS:
                continue
            if isinstance(child, (dict, list)):
                rows.extend(flatten_elements(child, f"{path}.{key}"))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            rows.extend(flatten_elements(child, f"{path}[{index}]"))
    return rows


def unwrap_handoff(payload: Any) -> dict[str, Any]:
    if not isinstance(payload, dict):
        return {}
    nested = payload.get("handoff")
    if isinstance(nested, dict) and ("latestEvent" in nested or "targetResolution" in nested):
        return nested
    return payload


def event_from_handoff(handoff: dict[str, Any]) -> dict[str, Any] | None:
    event = handoff.get("latestEvent")
    return event if isinstance(event, dict) else None


def target_resolution_from_handoff(handoff: dict[str, Any]) -> dict[str, Any]:
    resolution = handoff.get("targetResolution")
    return resolution if isinstance(resolution, dict) else {"rawCoordinateTapAllowed": False}


def event_point(event: dict[str, Any] | None) -> tuple[float, float] | None:
    if not event:
        return None
    nx = as_number(event.get("normalizedX"))
    ny = as_number(event.get("normalizedY"))
    if nx is not None and ny is not None:
        return max(0.0, min(1.0, nx)), max(0.0, min(1.0, ny))
    px = as_number(event.get("pixelX"))
    py = as_number(event.get("pixelY"))
    viewport = event.get("viewport")
    if px is not None and py is not None and isinstance(viewport, dict):
        width = as_number(viewport.get("width"))
        height = as_number(viewport.get("height"))
        if width and height:
            return max(0.0, min(1.0, px / width)), max(0.0, min(1.0, py / height))
    return None


def query_tokens(event: dict[str, Any] | None, target_resolution: dict[str, Any]) -> set[str]:
    parts = []
    if event:
        for key in ("note", "contextLabel", "action", "type"):
            parts.append(safe_text(event.get(key), 1000))
    for key in ("note", "contextLabel", "intent", "action"):
        parts.append(safe_text(target_resolution.get(key), 1000))
    return tokens(" ".join(parts))


def candidate_tokens(candidate: dict[str, Any]) -> set[str]:
    parts = [safe_text(candidate.get("role"), 220)]
    parts.extend(text for text in candidate.get("texts", []) if isinstance(text, str))
    return tokens(" ".join(parts))


def candidate_center(candidate: dict[str, Any], screen_size: tuple[float, float] | None) -> tuple[float, float] | None:
    frame = candidate.get("frame")
    if not isinstance(frame, dict):
        return None
    width, height = screen_size or (None, None)
    if not width or not height:
        return None
    cx = (frame["x"] + frame["width"] / 2.0) / width
    cy = (frame["y"] + frame["height"] / 2.0) / height
    return cx, cy


def score_candidate(
    candidate: dict[str, Any],
    *,
    point: tuple[float, float] | None,
    screen_size: tuple[float, float] | None,
    q_tokens: set[str],
    event: dict[str, Any] | None,
) -> dict[str, Any]:
    score = 0.0
    reasons: list[str] = []
    center = candidate_center(candidate, screen_size)
    if point and center:
        distance = math.sqrt((center[0] - point[0]) ** 2 + (center[1] - point[1]) ** 2)
        distance_score = max(0.0, 1.0 - distance / 0.35) * 52.0
        score += distance_score
        reasons.append(f"coordinate distance {distance:.3f}")

    c_tokens = candidate_tokens(candidate)
    overlap = sorted(q_tokens & c_tokens)
    if q_tokens and overlap:
        text_score = min(32.0, 32.0 * len(overlap) / max(1, len(q_tokens)))
        score += text_score
        reasons.append("matched text tokens: " + ", ".join(overlap[:6]))

    role = safe_text(candidate.get("role"), 120).lower()
    event_type = safe_text(event.get("type"), 80).lower() if event else ""
    action = safe_text(event.get("action"), 80).lower() if event else ""
    if any(word in role for word in ("button", "control", "link", "cell")) and (
        event_type in {"tap-request", "navigate-request"} or action in {"tap", "navigate"}
    ):
        score += 8.0
        reasons.append(f"interactive role {role}")
    if event_type == "copy-change" and c_tokens:
        score += 5.0
        reasons.append("text-bearing source candidate")
    if candidate.get("hittable") is True:
        score += 4.0
        reasons.append("hittable")
    if candidate.get("enabled") is True:
        score += 2.0
        reasons.append("enabled")
    if candidate.get("hidden") is True:
        score -= 25.0
        reasons.append("hidden penalty")

    confidence = "low"
    if score >= 75:
        confidence = "high"
    elif score >= 50:
        confidence = "medium"
    return {
        "score": round(max(0.0, min(100.0, score)), 2),
        "confidence": confidence,
        "elementRef": candidate.get("elementRef"),
        "label": candidate.get("label"),
        "role": candidate.get("role"),
        "frame": candidate.get("frame"),
        "path": candidate.get("path"),
        "reasons": reasons or ["no strong coordinate or text match"],
    }


def screen_size_for_match(snapshot: Any, event: dict[str, Any] | None) -> tuple[float, float] | None:
    size = extract_size(snapshot)
    if size:
        return size
    if event and isinstance(event.get("viewport"), dict):
        viewport = event["viewport"]
        width = as_number(viewport.get("width"))
        height = as_number(viewport.get("height"))
        if width and height:
            return width, height
    return None


def match_target(handoff_payload: Any, snapshot_payload: Any, max_candidates: int = 5) -> dict[str, Any]:
    handoff = unwrap_handoff(handoff_payload)
    event = event_from_handoff(handoff)
    target_resolution = target_resolution_from_handoff(handoff)
    raw_allowed = target_resolution.get("rawCoordinateTapAllowed")
    elements = flatten_elements(snapshot_payload)
    point = event_point(event)
    screen_size = screen_size_for_match(snapshot_payload, event)
    q_tokens = query_tokens(event, target_resolution)
    scored = [
        score_candidate(candidate, point=point, screen_size=screen_size, q_tokens=q_tokens, event=event)
        for candidate in elements
    ]
    scored = [candidate for candidate in scored if candidate["score"] > 0]
    scored.sort(key=lambda item: (-item["score"], item.get("label") or "", item.get("path") or ""))
    candidates = scored[: max(1, max_candidates)]
    for index, candidate in enumerate(candidates, start=1):
        candidate["rank"] = index

    top = candidates[0] if candidates else None
    status = "no-candidates"
    if top:
        status = "matched" if top["confidence"] in {"high", "medium"} else "needs-review"
    event_type = safe_text(event.get("type"), 80) if event else "none"
    next_steps = [
        "Review the top candidate against the current screenshot and UI hierarchy.",
        "Do not use raw browser coordinates as simulator input.",
    ]
    if event_type in {"tap-request", "navigate-request"}:
        next_steps.append("If the candidate is correct, use XcodeBuildMCP tap with the candidate id/label/elementRef.")
    elif event_type == "copy-change":
        next_steps.append("Use the candidate label as source search context; edit the owning SwiftUI/localization source, not the simulator.")
    else:
        next_steps.append("Use the candidate only as context for the next Codex implementation step.")

    result = {
        "ok": True,
        "tool": "shipguard ios target-match",
        "status": status,
        "rawCoordinateTapAllowed": raw_allowed if isinstance(raw_allowed, bool) else False,
        "screenSize": {"width": screen_size[0], "height": screen_size[1]} if screen_size else None,
        "latestEvent": event,
        "targetResolution": target_resolution,
        "candidateCount": len(elements),
        "queryTokens": sorted(q_tokens),
        "candidates": candidates,
        "nextSteps": next_steps,
    }
    result["markdown"] = render_markdown(result)
    return result


def render_markdown(result: dict[str, Any]) -> str:
    lines = [
        "# iOS Target Match",
        "",
        f"- Status: `{result['status']}`",
        f"- Raw coordinate tap allowed: `{str(result['rawCoordinateTapAllowed']).lower()}`",
        f"- Candidates scanned: `{result['candidateCount']}`",
        "",
        "## Candidates",
        "",
    ]
    candidates = result.get("candidates", [])
    if not candidates:
        lines.append("No matching UI candidates were found.")
    else:
        lines.append("| Rank | Score | Confidence | Element Ref | Label | Role | Reasons |")
        lines.append("| --- | ---: | --- | --- | --- | --- | --- |")
        for candidate in candidates:
            reasons = "; ".join(candidate.get("reasons", []))
            lines.append(
                "| {rank} | {score} | {confidence} | `{ref}` | {label} | {role} | {reasons} |".format(
                    rank=candidate.get("rank"),
                    score=candidate.get("score"),
                    confidence=candidate.get("confidence"),
                    ref=candidate.get("elementRef") or "",
                    label=(candidate.get("label") or "").replace("|", "\\|"),
                    role=(candidate.get("role") or "").replace("|", "\\|"),
                    reasons=reasons.replace("|", "\\|"),
                )
            )
    lines.extend(["", "## Next Steps", ""])
    for step in result.get("nextSteps", []):
        lines.append(f"- {step}")
    return "\n".join(lines) + "\n"


def main() -> int:
    args = parse_args()
    if args.max_candidates < 1:
        fail("--max-candidates must be at least 1")
    handoff = read_json(args.handoff)
    snapshot = read_json(args.snapshot)
    result = match_target(handoff, snapshot, args.max_candidates)
    if args.out:
        out_dir = Path(args.out).expanduser().resolve()
        out_dir.mkdir(parents=True, exist_ok=True)
        json_path = out_dir / "ios-target-match.json"
        markdown_path = out_dir / "ios-target-match.md"
        json_path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        markdown_path.write_text(result["markdown"], encoding="utf-8")
        print(f"wrote: {json_path}")
        print(f"wrote: {markdown_path}")
    else:
        print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
