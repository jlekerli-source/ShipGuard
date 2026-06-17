# iOS ShipGuard Preview Handoff

## Prompt

Use $ios-shipguard preview-bridge mode. The latest preview event is copy-change/change-copy from preview-context-menu. Note: Rename greeting label to Welcome back. For copy or visual events, edit source and refresh preview proof instead of tapping the simulator.

## Target Resolution

- Status: `source-edit-target`
- Intent: `copy-change`
- Action: `change-copy`
- Raw coordinate tap allowed: `false`
- XcodeBuildMCP next tool: `snapshot_ui`
- Element ref required before touch: `false`

## Checklist

- Locate the source text or localization key that owns the selected copy.
- Make the smallest copy edit.
- Refresh the preview screenshot after the source edit.

## Required Proof

- source diff for the copy change
- refreshed preview screenshot
- accessibility label check when relevant

## Suggested Actions

- Locate the owning SwiftUI text, accessibility label, or localization key before editing copy.
- Update the smallest copy surface that matches the selected coordinates and note.
- Refresh the preview screenshot and check accessibility labels after the copy change.

## Latest Event

```json
{
  "action": "change-copy",
  "contextLabel": "Greeting label",
  "normalizedX": 0.44,
  "normalizedY": 0.31,
  "note": "Rename greeting label to Welcome back.",
  "pixelX": 172,
  "pixelY": 262,
  "source": "preview-context-menu",
  "timestamp": "2026-06-17T00:00:00Z",
  "type": "copy-change",
  "viewport": {
    "height": 844,
    "width": 390
  }
}
```

## Receipts

- sessionJson: `fixtures/ios-devspace/complete-preview/session.json`
- eventLog: `fixtures/ios-devspace/complete-preview/preview-events.jsonl`
- handoffJson: `fixtures/ios-devspace/complete-preview/handoff.json`
- handoffMarkdown: `fixtures/ios-devspace/complete-preview/handoff.md`
- lastScreenshot: `fixtures/ios-devspace/complete-preview/last-screenshot.png`
- previewUrl: `http://127.0.0.1:8765`

## Safety Rules

- Do not use browser coordinates as simulator taps.
- For tap or navigation events, match a semantic XcodeBuildMCP `elementRef` before touch.
- For copy or visual events, edit source and refresh preview proof instead of tapping the simulator.
