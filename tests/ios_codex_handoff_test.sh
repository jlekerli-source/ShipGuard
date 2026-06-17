#!/usr/bin/env bash

set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
tmp_dir="$(mktemp -d)"
trap 'rm -rf "$tmp_dir"' EXIT

cd "$repo_root"

prompt_file="$tmp_dir/prompt.md"
prepared_out="$tmp_dir/prepared"
executed_out="$tmp_dir/executed"
fake_codex="$tmp_dir/fake-codex"

printf 'Use $ios-shipguard preview-devspace mode. Fix the latest copy-change event.\n' > "$prompt_file"

./bin/shipguard ios codex-handoff --help >/dev/null

./bin/shipguard ios codex-handoff \
  --prompt-file "$prompt_file" \
  --out "$prepared_out" \
  --cwd "$repo_root" >/dev/null

test -f "$prepared_out/codex-handoff-prompt.md"
test -f "$prepared_out/codex-app-server-plan.json"
test -f "$prepared_out/codex-app-server-messages.jsonl"
grep -q 'Fix the latest copy-change event' "$prepared_out/codex-handoff-prompt.md"
grep -q '"status": "prepared"' "$prepared_out/codex-app-server-plan.json"
grep -q '"explicitExecutionRequired": true' "$prepared_out/codex-app-server-plan.json"
grep -q '"method":"initialize"' "$prepared_out/codex-app-server-messages.jsonl"
grep -q '"threadId":"$THREAD_ID"' "$prepared_out/codex-app-server-messages.jsonl"

if ./bin/shipguard ios codex-handoff --prompt '' --out "$tmp_dir/empty" >/dev/null 2>&1; then
  echo "expected empty prompt to fail" >&2
  exit 1
fi

cat > "$fake_codex" <<'PY'
#!/usr/bin/env python3
import json
import sys

argv = sys.argv[1:]
if argv != ["app-server"]:
    print(f"unexpected args: {argv}", file=sys.stderr)
    raise SystemExit(2)

for line in sys.stdin:
    if not line.strip():
        continue
    message = json.loads(line)
    method = message.get("method")
    request_id = message.get("id")
    if method == "initialize":
        print(json.dumps({"id": request_id, "result": {"userAgent": "fake-codex"}}), flush=True)
    elif method == "initialized":
        continue
    elif method == "thread/start":
        print(json.dumps({"id": request_id, "result": {"thread": {"id": "thr_fake"}}}), flush=True)
    elif method == "turn/start":
        prompt = message["params"]["input"][0]["text"]
        if "copy-change" not in prompt:
            print(json.dumps({"id": request_id, "error": {"code": 400, "message": "missing prompt"}}), flush=True)
            raise SystemExit(0)
        print(json.dumps({"id": request_id, "result": {"turn": {"id": "turn_fake"}}}), flush=True)
        print(json.dumps({"method": "turn/completed", "params": {"turn": {"id": "turn_fake"}, "status": "completed"}}), flush=True)
        raise SystemExit(0)
PY
chmod +x "$fake_codex"

./bin/shipguard ios codex-handoff \
  --prompt-file "$prompt_file" \
  --out "$executed_out" \
  --cwd "$repo_root" \
  --codex-bin "$fake_codex" \
  --execute \
  --timeout-sec 5 >/dev/null

grep -q '"status": "executed"' "$executed_out/codex-app-server-plan.json"
grep -q '"threadId": "thr_fake"' "$executed_out/codex-app-server-plan.json"
grep -q '"method":"initialize"' "$executed_out/codex-app-server-transcript.jsonl"
grep -q '"method":"turn/completed"' "$executed_out/codex-app-server-transcript.jsonl"

echo "ios codex handoff tests passed"
