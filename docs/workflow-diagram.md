# Workflow Diagram

```mermaid
flowchart TD
  A["User request or issue"] --> B["Read AGENTS.md"]
  B --> C["Classify risk lane"]
  C --> D{"Risky or broad?"}
  D -->|"yes"| E["Write or update PLANS.md"]
  D -->|"no"| F["Make narrow change"]
  E --> F
  F --> G["Run smallest proof command"]
  G --> H{"Proof passed?"}
  H -->|"yes"| I["Review diff and regression risk"]
  H -->|"blocked"| J["Write exact blocker and next action"]
  I --> K["Score run if useful"]
  K --> L["Commit, release, or hand off"]
  J --> L
```

## Plain-Text Fallback

```text
request
  -> read AGENTS.md
  -> classify risk
  -> write PLANS.md when risk is broad
  -> make the narrow change
  -> run the smallest proof command
  -> review the diff and regression risk
  -> score the run when useful
  -> commit, release, or hand off
```

## Maintainer Rule

The workflow is not complete when code changes. It is complete when the maintainer has evidence, a clear handoff, and an honest statement of what is still unproven.
