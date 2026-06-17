#!/usr/bin/env bash

set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
tmp_dir="$(mktemp -d)"
trap 'rm -rf "$tmp_dir"' EXIT

cd "$repo_root"

./bin/shipguard ios spec-workflow --help >/dev/null

./bin/shipguard ios design \
  --path fixtures/demo-ios-repo \
  --out "$tmp_dir/design" \
  --shipguard-eval \
  --shareable >/dev/null

./bin/shipguard ios report-quality \
  --reports "$tmp_dir/design" \
  --out "$tmp_dir/quality" \
  --shareable >/dev/null

./bin/shipguard ios spec-workflow \
  --path fixtures/demo-ios-repo \
  --feature "Spec-driven Devspace workflow integration" \
  --from-report "$tmp_dir/quality" \
  --app-type game \
  --shipguard-eval \
  --shareable \
  --out "$tmp_dir/spec" >/dev/null

test -f "$tmp_dir/spec/ios-spec-workflow.json"
test -f "$tmp_dir/spec/ios-spec-workflow.md"
test -f "$tmp_dir/spec/shipguard-constitution.md"
test -f "$tmp_dir/spec/feature-spec.md"
test -f "$tmp_dir/spec/implementation-plan.md"
test -f "$tmp_dir/spec/tasks.md"
test -f "$tmp_dir/spec/devspace-guardrails.md"
python3 -m json.tool "$tmp_dir/spec/ios-spec-workflow.json" >/dev/null
grep -q '"tool": "shipguard ios spec-workflow"' "$tmp_dir/spec/ios-spec-workflow.json"
grep -q '"value": "game"' "$tmp_dir/spec/ios-spec-workflow.json"
grep -q '"mode": "shareable"' "$tmp_dir/spec/ios-spec-workflow.json"
grep -q '"localAbsolutePathsIncluded": false' "$tmp_dir/spec/ios-spec-workflow.json"
grep -q '"intent": "shipguard-evaluation"' "$tmp_dir/spec/ios-spec-workflow.json"
grep -q '"shipguardOnly": true' "$tmp_dir/spec/ios-spec-workflow.json"
grep -q '"source": "GitHub Spec Kit"' "$tmp_dir/spec/ios-spec-workflow.json"
grep -q '"source": "CodexPro"' "$tmp_dir/spec/ios-spec-workflow.json"
grep -q 'Did the report tailor advice to the app type' "$tmp_dir/spec/ios-spec-workflow.json"
grep -q '# ShipGuard Constitution' "$tmp_dir/spec/shipguard-constitution.md"
grep -q 'Devspace is a planning bridge' "$tmp_dir/spec/shipguard-constitution.md"
grep -q '# Feature Spec' "$tmp_dir/spec/feature-spec.md"
grep -q 'The ShipGuard change answers report-quality actionability question:' "$tmp_dir/spec/feature-spec.md"
grep -q 'The ShipGuard change answers report-quality actionability question:' "$tmp_dir/spec/ios-spec-workflow.json"
grep -q '# Implementation Plan' "$tmp_dir/spec/implementation-plan.md"
grep -q './tests/ios_spec_workflow_test.sh' "$tmp_dir/spec/implementation-plan.md"
grep -q 'Devspace remains a connector and handoff path' "$tmp_dir/spec/implementation-plan.md"
grep -q './tests/ios_report_quality_test.sh' "$tmp_dir/spec/ios-spec-workflow.json"
grep -q 'Private-app observations remain ShipGuard product-QA evidence only' "$tmp_dir/spec/ios-spec-workflow.json"
grep -q '# Tasks' "$tmp_dir/spec/tasks.md"
grep -q '`S007` Resolve report-quality actionability question:' "$tmp_dir/spec/tasks.md"
grep -q '"id": "S007"' "$tmp_dir/spec/ios-spec-workflow.json"
grep -q 'Resolve report-quality actionability question:' "$tmp_dir/spec/ios-spec-workflow.json"
grep -q '# Devspace Guardrails' "$tmp_dir/spec/devspace-guardrails.md"
grep -q 'Model selection happens in ChatGPT, not ShipGuard' "$tmp_dir/spec/devspace-guardrails.md" || \
  grep -q 'model selection happens in ChatGPT, not ShipGuard' "$tmp_dir/spec/devspace-guardrails.md"
grep -q '/plan Spec-driven Devspace workflow integration' "$tmp_dir/spec/ios-spec-workflow.md"
grep -q '/goal Implement Spec-driven Devspace workflow integration' "$tmp_dir/spec/ios-spec-workflow.md"
grep -q 'Scan Scope' "$tmp_dir/spec/ios-spec-workflow.md"

if grep -R -F -q "$tmp_dir" "$tmp_dir/spec"; then
  echo "shareable spec-workflow output must not include temp absolute paths" >&2
  exit 1
fi

./bin/shipguard ios report-quality \
  --reports "$tmp_dir/spec" \
  --out "$tmp_dir/spec-quality" \
  --shareable >/dev/null
grep -q '"status": "pass"' "$tmp_dir/spec-quality/ios-report-quality.json"

mkdir -p "$tmp_dir/duplicate-question-quality"
python3 - <<'PY' "$tmp_dir/duplicate-question-quality/ios-report-quality.json"
import json
import sys

questions = [
    "Did the report expose source evidence for every recommendation?",
    "Did the report rank the next ShipGuard rule before examples?",
    "Did the report keep private app details as evaluation evidence only?",
    "Which observation should become a public fixture or eval case before changing the rule again?",
    "Did the report name the proof command for the next patch?",
    "Did the report distinguish scanner noise from product-critical gaps?",
    "Did the report preserve shareability metadata before planning?",
    "Which observation should become a public fixture or eval case before changing the rule again?",
    "Did the report keep the first unique questions in clarifying questions?",
    "Did the report leave a next slash goal after validation?",
]
data = {
    "schemaVersion": 1,
    "tool": "shipguard ios report-quality",
    "status": "pass",
    "shareability": {"mode": "shareable", "localAbsolutePathsIncluded": False},
    "reports": [{"path": "<fixture>/ios-design.json", "tool": "shipguard ios design", "status": "pass"}],
    "actionabilityQuestions": [
        {"tool": "shipguard ios design", "report": "<fixture>/ios-design.json", "question": question}
        for question in questions
    ],
}
open(sys.argv[1], "w", encoding="utf-8").write(json.dumps(data, indent=2, sort_keys=True) + "\n")
PY
./bin/shipguard ios spec-workflow \
  --path fixtures/demo-ios-repo \
  --feature "Deduplicate repeated report-quality questions" \
  --from-report "$tmp_dir/duplicate-question-quality" \
  --shipguard-eval \
  --shareable \
  --out "$tmp_dir/duplicate-question-spec" >/dev/null
python3 - <<'PY' "$tmp_dir/duplicate-question-spec/ios-spec-workflow.json" "$tmp_dir/duplicate-question-spec/ios-spec-workflow.md"
import json
from pathlib import Path
import sys

expected = [
    "Did the report expose source evidence for every recommendation?",
    "Did the report rank the next ShipGuard rule before examples?",
    "Did the report keep private app details as evaluation evidence only?",
    "Which observation should become a public fixture or eval case before changing the rule again?",
    "Did the report name the proof command for the next patch?",
    "Did the report distinguish scanner noise from product-critical gaps?",
    "Did the report preserve shareability metadata before planning?",
    "Did the report keep the first unique questions in clarifying questions?",
]
data = json.load(open(sys.argv[1], encoding="utf-8"))
clarifying = data["featureSpec"]["clarifyingQuestions"]
if clarifying != expected:
    raise SystemExit(f"clarifying questions were not first-eight unique questions: {clarifying!r}")
input_questions = [item["question"] for item in data["reportInputs"]["actionabilityQuestions"]]
if input_questions[:8] != expected:
    raise SystemExit(f"reportInputs questions were not deduplicated before cap: {input_questions!r}")
markdown = Path(sys.argv[2]).read_text(encoding="utf-8")
for question in expected:
    if question not in markdown:
        raise SystemExit(f"missing expected question in markdown: {question}")
PY
./bin/shipguard ios report-quality \
  --reports "$tmp_dir/duplicate-question-spec" \
  --out "$tmp_dir/duplicate-question-spec-quality" \
  --shareable >/dev/null
grep -q '"status": "pass"' "$tmp_dir/duplicate-question-spec-quality/ios-report-quality.json"

cp -R "$tmp_dir/spec" "$tmp_dir/missing-artifact-spec"
rm "$tmp_dir/missing-artifact-spec/tasks.md"
./bin/shipguard ios report-quality \
  --reports "$tmp_dir/missing-artifact-spec" \
  --out "$tmp_dir/missing-artifact-quality" \
  --shareable >/dev/null
grep -q '"status": "review"' "$tmp_dir/missing-artifact-quality/ios-report-quality.json"
grep -q '"ruleId": "spec-workflow-artifact-file-missing"' "$tmp_dir/missing-artifact-quality/ios-report-quality.json"
grep -q 'tasks.md' "$tmp_dir/missing-artifact-quality/ios-report-quality.json"
if grep -R -F -q "$tmp_dir" "$tmp_dir/missing-artifact-quality"; then
  echo "shareable artifact-missing quality output must not include temp absolute paths" >&2
  exit 1
fi

cp -R "$tmp_dir/spec" "$tmp_dir/weak-content-spec"
printf '# Tasks\n\n- TODO\n' > "$tmp_dir/weak-content-spec/tasks.md"
printf '# Devspace Guardrails\n\n- TODO\n' > "$tmp_dir/weak-content-spec/devspace-guardrails.md"
./bin/shipguard ios report-quality \
  --reports "$tmp_dir/weak-content-spec" \
  --out "$tmp_dir/weak-content-quality" \
  --shareable >/dev/null
grep -q '"status": "review"' "$tmp_dir/weak-content-quality/ios-report-quality.json"
grep -q '"ruleId": "spec-workflow-artifact-content-incomplete"' "$tmp_dir/weak-content-quality/ios-report-quality.json"
grep -q '"ruleId": "spec-workflow-artifact-placeholder-content"' "$tmp_dir/weak-content-quality/ios-report-quality.json"
grep -q 'tasks.md' "$tmp_dir/weak-content-quality/ios-report-quality.json"
grep -q 'devspace-guardrails.md' "$tmp_dir/weak-content-quality/ios-report-quality.json"
if grep -R -F -q "$tmp_dir" "$tmp_dir/weak-content-quality"; then
  echo "shareable weak-content quality output must not include temp absolute paths" >&2
  exit 1
fi

cp -R "$tmp_dir/spec" "$tmp_dir/missing-task-coverage-spec"
python3 - <<'PY' "$tmp_dir/missing-task-coverage-spec/ios-spec-workflow.json"
import json
import sys
path = sys.argv[1]
data = json.load(open(path, encoding="utf-8"))
data["taskPlan"] = [item for item in data["taskPlan"] if not str(item.get("task", "")).startswith("Resolve report-quality actionability question:")]
open(path, "w", encoding="utf-8").write(json.dumps(data, indent=2, sort_keys=True) + "\n")
PY
python3 - <<'PY' "$tmp_dir/missing-task-coverage-spec/tasks.md"
from pathlib import Path
import sys

Path(sys.argv[1]).write_text(
    "# Tasks\n\n"
    "- [ ] `S001` Record the ShipGuard constitution and non-goals for this feature. Proof: shipguard-constitution.md exists.\n"
    "- [ ] `S002` Write the feature spec with user outcomes, non-goals, acceptance criteria, and clarifying questions. Proof: feature-spec.md exists.\n"
    "- [ ] `S003` Map implementation phases to local proof commands and manual blockers. Proof: implementation-plan.md exists.\n"
    "- [ ] `S004` Prepare ordered tasks with validation commands before edits. Proof: tasks.md exists.\n"
    "- [ ] `S005` Check Devspace safety gates before ChatGPT visual planning or MCP exposure. Proof: devspace-guardrails.md exists and references devspace-check.\n"
    "- [ ] `S006` Run report-quality on generated ShipGuard artifacts before sharing. Proof: ios report-quality returns pass or documented review findings.\n",
    encoding="utf-8",
)
PY
./bin/shipguard ios report-quality \
  --reports "$tmp_dir/missing-task-coverage-spec" \
  --out "$tmp_dir/missing-task-coverage-quality" \
  --shareable >/dev/null
grep -q '"status": "review"' "$tmp_dir/missing-task-coverage-quality/ios-report-quality.json"
grep -q '"ruleId": "spec-workflow-task-coverage-missing"' "$tmp_dir/missing-task-coverage-quality/ios-report-quality.json"
grep -q '"ruleId": "spec-workflow-task-artifact-missing"' "$tmp_dir/missing-task-coverage-quality/ios-report-quality.json"
if grep -R -F -q "$tmp_dir" "$tmp_dir/missing-task-coverage-quality"; then
  echo "shareable missing-task-coverage quality output must not include temp absolute paths" >&2
  exit 1
fi

cp -R "$tmp_dir/spec" "$tmp_dir/missing-acceptance-coverage-spec"
python3 - <<'PY' "$tmp_dir/missing-acceptance-coverage-spec/ios-spec-workflow.json"
import json
import sys
path = sys.argv[1]
data = json.load(open(path, encoding="utf-8"))
data["featureSpec"]["acceptanceCriteria"] = [
    "The generated plan includes constitution, spec, checklist, tasks, analysis gates, and Devspace guardrails.",
    "Each task names a validation or proof lane.",
    "Shareable output avoids local absolute paths and passes ios report-quality.",
]
open(path, "w", encoding="utf-8").write(json.dumps(data, indent=2, sort_keys=True) + "\n")
PY
python3 - <<'PY' "$tmp_dir/missing-acceptance-coverage-spec/feature-spec.md"
from pathlib import Path
import sys

path = Path(sys.argv[1])
text = path.read_text(encoding="utf-8")
before, rest = text.split("## Acceptance Criteria", 1)
_, after = rest.split("## Clarifying Questions", 1)
path.write_text(
    before
    + "## Acceptance Criteria\n\n"
    + "- The generated plan includes constitution, spec, checklist, tasks, analysis gates, and Devspace guardrails.\n"
    + "- Each task names a validation or proof lane.\n"
    + "- Shareable output avoids local absolute paths and passes ios report-quality.\n\n"
    + "## Clarifying Questions"
    + after,
    encoding="utf-8",
)
PY
./bin/shipguard ios report-quality \
  --reports "$tmp_dir/missing-acceptance-coverage-spec" \
  --out "$tmp_dir/missing-acceptance-coverage-quality" \
  --shareable >/dev/null
grep -q '"status": "review"' "$tmp_dir/missing-acceptance-coverage-quality/ios-report-quality.json"
grep -q '"ruleId": "spec-workflow-acceptance-coverage-missing"' "$tmp_dir/missing-acceptance-coverage-quality/ios-report-quality.json"
grep -q '"ruleId": "spec-workflow-acceptance-artifact-missing"' "$tmp_dir/missing-acceptance-coverage-quality/ios-report-quality.json"
if grep -R -F -q "$tmp_dir" "$tmp_dir/missing-acceptance-coverage-quality"; then
  echo "shareable missing-acceptance-coverage quality output must not include temp absolute paths" >&2
  exit 1
fi

cp -R "$tmp_dir/spec" "$tmp_dir/missing-validation-coverage-spec"
python3 - <<'PY' "$tmp_dir/missing-validation-coverage-spec/ios-spec-workflow.json"
import json
import sys
path = sys.argv[1]
data = json.load(open(path, encoding="utf-8"))
data["technicalPlan"]["recommendedValidation"] = []
open(path, "w", encoding="utf-8").write(json.dumps(data, indent=2, sort_keys=True) + "\n")
PY
python3 - <<'PY' "$tmp_dir/missing-validation-coverage-spec/implementation-plan.md"
from pathlib import Path
import sys

path = Path(sys.argv[1])
text = path.read_text(encoding="utf-8")
before, rest = text.split("## Validation", 1)
_, after = rest.split("## Analysis Gates", 1)
path.write_text(
    before
    + "## Validation\n\n"
    + "- Validation commands need maintainer selection.\n\n"
    + "## Analysis Gates"
    + after,
    encoding="utf-8",
)
PY
./bin/shipguard ios report-quality \
  --reports "$tmp_dir/missing-validation-coverage-spec" \
  --out "$tmp_dir/missing-validation-coverage-quality" \
  --shareable >/dev/null
grep -q '"status": "review"' "$tmp_dir/missing-validation-coverage-quality/ios-report-quality.json"
grep -q '"ruleId": "spec-workflow-validation-coverage-missing"' "$tmp_dir/missing-validation-coverage-quality/ios-report-quality.json"
grep -q '"ruleId": "spec-workflow-validation-artifact-missing"' "$tmp_dir/missing-validation-coverage-quality/ios-report-quality.json"
if grep -R -F -q "$tmp_dir" "$tmp_dir/missing-validation-coverage-quality"; then
  echo "shareable missing-validation-coverage quality output must not include temp absolute paths" >&2
  exit 1
fi

cp -R "$tmp_dir/spec" "$tmp_dir/missing-analysis-coverage-spec"
python3 - <<'PY' "$tmp_dir/missing-analysis-coverage-spec/ios-spec-workflow.json"
import json
import sys
path = sys.argv[1]
data = json.load(open(path, encoding="utf-8"))
data["analysisGates"] = ["Analysis gates need maintainer selection."]
open(path, "w", encoding="utf-8").write(json.dumps(data, indent=2, sort_keys=True) + "\n")
PY
python3 - <<'PY' "$tmp_dir/missing-analysis-coverage-spec/implementation-plan.md"
from pathlib import Path
import sys

path = Path(sys.argv[1])
text = path.read_text(encoding="utf-8")
before, _ = text.split("## Analysis Gates", 1)
path.write_text(
    before
    + "## Analysis Gates\n\n"
    + "- Analysis gates need maintainer selection.\n",
    encoding="utf-8",
)
PY
./bin/shipguard ios report-quality \
  --reports "$tmp_dir/missing-analysis-coverage-spec" \
  --out "$tmp_dir/missing-analysis-coverage-quality" \
  --shareable >/dev/null
grep -q '"status": "review"' "$tmp_dir/missing-analysis-coverage-quality/ios-report-quality.json"
grep -q '"ruleId": "spec-workflow-analysis-coverage-missing"' "$tmp_dir/missing-analysis-coverage-quality/ios-report-quality.json"
grep -q '"ruleId": "spec-workflow-analysis-artifact-missing"' "$tmp_dir/missing-analysis-coverage-quality/ios-report-quality.json"
if grep -R -F -q "$tmp_dir" "$tmp_dir/missing-analysis-coverage-quality"; then
  echo "shareable missing-analysis-coverage quality output must not include temp absolute paths" >&2
  exit 1
fi

cp -R "$tmp_dir/spec" "$tmp_dir/weak-slash-handoff-spec"
python3 - <<'PY' "$tmp_dir/weak-slash-handoff-spec/ios-spec-workflow.json"
import json
import sys
path = sys.argv[1]
data = json.load(open(path, encoding="utf-8"))
data["slashPlan"] = "Plan later after maintainer selection."
data["slashGoal"] = "Goal later after maintainer selection."
open(path, "w", encoding="utf-8").write(json.dumps(data, indent=2, sort_keys=True) + "\n")
PY
python3 - <<'PY' "$tmp_dir/weak-slash-handoff-spec/ios-spec-workflow.md"
from pathlib import Path
import sys

path = Path(sys.argv[1])
head = path.read_text(encoding="utf-8").split("## Slash Plan", 1)[0]
path.write_text(
    head
    + "## Slash Plan\n\n"
    + "```text\nPlan later after maintainer selection.\n```\n\n"
    + "## Slash Goal\n\n"
    + "```text\nGoal later after maintainer selection.\n```\n",
    encoding="utf-8",
)
PY
./bin/shipguard ios report-quality \
  --reports "$tmp_dir/weak-slash-handoff-spec" \
  --out "$tmp_dir/weak-slash-handoff-quality" \
  --shareable >/dev/null
grep -q '"status": "review"' "$tmp_dir/weak-slash-handoff-quality/ios-report-quality.json"
grep -q '"ruleId": "spec-workflow-slash-handoff-incomplete"' "$tmp_dir/weak-slash-handoff-quality/ios-report-quality.json"
if grep -R -F -q "$tmp_dir" "$tmp_dir/weak-slash-handoff-quality"; then
  echo "shareable weak-slash-handoff quality output must not include temp absolute paths" >&2
  exit 1
fi

cp -R "$tmp_dir/spec" "$tmp_dir/missing-slash-artifact-spec"
python3 - <<'PY' "$tmp_dir/missing-slash-artifact-spec/ios-spec-workflow.md"
from pathlib import Path
import sys

path = Path(sys.argv[1])
head = path.read_text(encoding="utf-8").split("## Slash Plan", 1)[0]
path.write_text(
    head
    + "## Slash Plan\n\n"
    + "```text\nPlan later after maintainer selection.\n```\n\n"
    + "## Slash Goal\n\n"
    + "```text\nGoal later after maintainer selection.\n```\n",
    encoding="utf-8",
)
PY
./bin/shipguard ios report-quality \
  --reports "$tmp_dir/missing-slash-artifact-spec" \
  --out "$tmp_dir/missing-slash-artifact-quality" \
  --shareable >/dev/null
grep -q '"status": "review"' "$tmp_dir/missing-slash-artifact-quality/ios-report-quality.json"
grep -q '"ruleId": "spec-workflow-slash-handoff-artifact-missing"' "$tmp_dir/missing-slash-artifact-quality/ios-report-quality.json"
if grep -R -F -q "$tmp_dir" "$tmp_dir/missing-slash-artifact-quality"; then
  echo "shareable missing-slash-artifact quality output must not include temp absolute paths" >&2
  exit 1
fi

cp -R "$tmp_dir/spec" "$tmp_dir/missing-questions-spec"
python3 - <<'PY' "$tmp_dir/missing-questions-spec/ios-spec-workflow.json"
import json
import sys
path = sys.argv[1]
data = json.load(open(path, encoding="utf-8"))
data["featureSpec"]["clarifyingQuestions"] = ["Which maintainer outcome is most important?"]
open(path, "w", encoding="utf-8").write(json.dumps(data, indent=2, sort_keys=True) + "\n")
PY
python3 - <<'PY' "$tmp_dir/missing-questions-spec/feature-spec.md" "$tmp_dir/missing-questions-spec/ios-spec-workflow.md"
from pathlib import Path
import sys

feature = Path(sys.argv[1])
main = Path(sys.argv[2])
feature.write_text(
    "# Feature Spec\n\n"
    "## Summary\n\nSpec-driven Devspace workflow integration\n\n"
    "## User Outcomes\n\n- ShipGuard can plan work.\n\n"
    "## Non-Goals\n\n- Do not edit private apps.\n\n"
    "## Acceptance Criteria\n\n- Report-quality passes.\n\n"
    "## Clarifying Questions\n\n- Which maintainer outcome is most important?\n",
    encoding="utf-8",
)
main_text = main.read_text(encoding="utf-8")
head = main_text.split("## Clarifying Questions", 1)[0]
tail = "## Clarifying Questions\n\n- Which maintainer outcome is most important?\n\n## Scan Scope\n" + main_text.split("## Scan Scope", 1)[1]
main.write_text(head + tail, encoding="utf-8")
PY
./bin/shipguard ios report-quality \
  --reports "$tmp_dir/missing-questions-spec" \
  --out "$tmp_dir/missing-questions-quality" \
  --shareable >/dev/null
grep -q '"status": "review"' "$tmp_dir/missing-questions-quality/ios-report-quality.json"
grep -q '"ruleId": "spec-workflow-question-coverage-missing"' "$tmp_dir/missing-questions-quality/ios-report-quality.json"
grep -q '"ruleId": "spec-workflow-question-artifact-missing"' "$tmp_dir/missing-questions-quality/ios-report-quality.json"
if grep -R -F -q "$tmp_dir" "$tmp_dir/missing-questions-quality"; then
  echo "shareable missing-questions quality output must not include temp absolute paths" >&2
  exit 1
fi

./bin/shipguard ios spec-workflow \
  --path fixtures/demo-ios-repo \
  --feature "No report context spec" \
  --shareable \
  --out "$tmp_dir/no-context-spec" >/dev/null
./bin/shipguard ios report-quality \
  --reports "$tmp_dir/no-context-spec" \
  --out "$tmp_dir/no-context-quality" \
  --shareable >/dev/null
grep -q '"status": "review"' "$tmp_dir/no-context-quality/ios-report-quality.json"
grep -q '"ruleId": "spec-workflow-report-context-missing"' "$tmp_dir/no-context-quality/ios-report-quality.json"
grep -q '"ruleId": "spec-workflow-actionability-missing"' "$tmp_dir/no-context-quality/ios-report-quality.json"

json_stdout="$(
  ./bin/shipguard ios spec-workflow \
    --path fixtures/demo-ios-repo \
    --feature "Inline spec workflow" \
    --json
)"
printf '%s\n' "$json_stdout" | grep -q '"tool": "shipguard ios spec-workflow"'
printf '%s\n' "$json_stdout" | grep -q '"ruleId": "spec-report-context-not-provided"'

echo "ios spec-workflow tests passed"
