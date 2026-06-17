#!/usr/bin/env python3
"""Prepare or execute a guarded Codex app-server handoff."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import subprocess
import sys
import time
from pathlib import Path
from typing import Any


MAX_PROMPT_CHARS = 20000
SCHEMA_VERSION = 1


def utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def fail(message: str) -> None:
    print(f"ios-codex-handoff: {message}", file=sys.stderr)
    raise SystemExit(1)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Prepare or explicitly execute a Codex app-server handoff from a ShipGuard preview event."
    )
    prompt_group = parser.add_mutually_exclusive_group(required=True)
    prompt_group.add_argument("--prompt", help="Prompt text to send to Codex.")
    prompt_group.add_argument("--prompt-file", help="File containing prompt text to send to Codex.")
    parser.add_argument("--out", required=True, help="Output directory for handoff artifacts.")
    parser.add_argument("--cwd", default=".", help="Working directory for the Codex turn. Default: current directory.")
    parser.add_argument("--model", help="Optional model override for thread/start.")
    parser.add_argument("--codex-bin", default="codex", help="Codex executable path. Default: codex.")
    parser.add_argument("--execute", action="store_true", help="Actually start codex app-server and turn/start.")
    parser.add_argument("--timeout-sec", type=int, default=60, help="Maximum seconds to wait for execution.")
    return parser.parse_args()


def json_line(payload: dict[str, Any]) -> str:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"))


def read_prompt(args: argparse.Namespace) -> str:
    if args.prompt_file:
        path = Path(args.prompt_file).expanduser().resolve()
        if not path.is_file():
            fail(f"prompt file not found: {path}")
        prompt = path.read_text(encoding="utf-8")
    else:
        prompt = args.prompt or ""
    prompt = prompt.strip()
    if not prompt:
        fail("prompt must not be empty")
    if len(prompt) > MAX_PROMPT_CHARS:
        fail(f"prompt exceeds {MAX_PROMPT_CHARS} characters")
    return prompt


def base_artifacts(args: argparse.Namespace, prompt: str, out_dir: Path, cwd: Path) -> dict[str, Any]:
    thread_params: dict[str, Any] = {}
    if args.model:
        thread_params["model"] = args.model

    turn_params: dict[str, Any] = {
        "threadId": "$THREAD_ID",
        "input": [{"type": "text", "text": prompt}],
        "cwd": str(cwd),
    }
    return {
        "schemaVersion": SCHEMA_VERSION,
        "createdAt": utc_now(),
        "status": "prepared",
        "execute": bool(args.execute),
        "cwd": str(cwd),
        "promptFile": str(out_dir / "codex-handoff-prompt.md"),
        "transcriptFile": str(out_dir / "codex-app-server-transcript.jsonl"),
        "codexAppServer": {
            "transport": "stdio",
            "command": [args.codex_bin, "app-server"],
            "explicitExecutionRequired": True,
            "executeCommand": [
                "./bin/shipguard",
                "ios",
                "codex-handoff",
                "--prompt-file",
                str(out_dir / "codex-handoff-prompt.md"),
                "--out",
                str(out_dir),
                "--cwd",
                str(cwd),
                "--execute",
            ],
        },
        "requests": {
            "initialize": {
                "method": "initialize",
                "id": 0,
                "params": {
                    "clientInfo": {
                        "name": "shipguard_devspace",
                        "title": "ShipGuard Devspace",
                        "version": "0.1.0",
                    }
                },
            },
            "initialized": {"method": "initialized", "params": {}},
            "threadStart": {"method": "thread/start", "id": 1, "params": thread_params},
            "turnStartTemplate": {"method": "turn/start", "id": 2, "params": turn_params},
        },
    }


def write_prepared(out_dir: Path, artifacts: dict[str, Any], prompt: str) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    prompt_file = out_dir / "codex-handoff-prompt.md"
    plan_file = out_dir / "codex-app-server-plan.json"
    messages_file = out_dir / "codex-app-server-messages.jsonl"

    prompt_file.write_text(prompt + "\n", encoding="utf-8")
    plan_file.write_text(json.dumps(artifacts, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    requests = artifacts["requests"]
    messages_file.write_text(
        "\n".join(
            [
                json_line(requests["initialize"]),
                json_line(requests["initialized"]),
                json_line(requests["threadStart"]),
                json_line(requests["turnStartTemplate"]),
            ]
        )
        + "\n",
        encoding="utf-8",
    )


def send(proc: subprocess.Popen[str], handle: Any, payload: dict[str, Any]) -> None:
    line = json_line(payload)
    handle.write(json_line({"direction": "client", "message": payload, "timestamp": utc_now()}) + "\n")
    handle.flush()
    if not proc.stdin:
        raise RuntimeError("app-server stdin is closed")
    proc.stdin.write(line + "\n")
    proc.stdin.flush()


def read_message(proc: subprocess.Popen[str], handle: Any, *, timeout_at: float) -> dict[str, Any]:
    if not proc.stdout:
        raise RuntimeError("app-server stdout is closed")
    while True:
        if time.monotonic() > timeout_at:
            raise TimeoutError("timed out waiting for app-server response")
        line = proc.stdout.readline()
        if line:
            try:
                message = json.loads(line)
            except json.JSONDecodeError as exc:
                raise RuntimeError(f"app-server emitted invalid JSON: {line.strip()}") from exc
            if not isinstance(message, dict):
                raise RuntimeError("app-server emitted non-object JSON")
            handle.write(json_line({"direction": "server", "message": message, "timestamp": utc_now()}) + "\n")
            handle.flush()
            return message
        if proc.poll() is not None:
            raise RuntimeError(f"app-server exited with code {proc.returncode}")
        time.sleep(0.05)


def wait_for_response(proc: subprocess.Popen[str], handle: Any, response_id: int, timeout_at: float) -> dict[str, Any]:
    while True:
        message = read_message(proc, handle, timeout_at=timeout_at)
        if message.get("id") == response_id:
            if "error" in message:
                raise RuntimeError(f"app-server error for id {response_id}: {message['error']}")
            return message


def wait_for_turn_completed(proc: subprocess.Popen[str], handle: Any, timeout_at: float) -> dict[str, Any]:
    while True:
        message = read_message(proc, handle, timeout_at=timeout_at)
        if message.get("method") == "turn/completed":
            return message


def execute_handoff(args: argparse.Namespace, artifacts: dict[str, Any], out_dir: Path) -> dict[str, Any]:
    transcript_file = out_dir / "codex-app-server-transcript.jsonl"
    timeout_at = time.monotonic() + args.timeout_sec
    requests = artifacts["requests"]
    proc = subprocess.Popen(
        [args.codex_bin, "app-server"],
        cwd=artifacts["cwd"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    try:
        with transcript_file.open("w", encoding="utf-8") as transcript:
            send(proc, transcript, requests["initialize"])
            wait_for_response(proc, transcript, 0, timeout_at)
            send(proc, transcript, requests["initialized"])
            send(proc, transcript, requests["threadStart"])
            thread_response = wait_for_response(proc, transcript, 1, timeout_at)
            thread_id = thread_response.get("result", {}).get("thread", {}).get("id")
            if not isinstance(thread_id, str) or not thread_id:
                raise RuntimeError("thread/start response did not include result.thread.id")
            turn_start = json.loads(json.dumps(requests["turnStartTemplate"]))
            turn_start["params"]["threadId"] = thread_id
            send(proc, transcript, turn_start)
            turn_response = wait_for_response(proc, transcript, 2, timeout_at)
            completed = wait_for_turn_completed(proc, transcript, timeout_at)
        return {
            "status": "executed",
            "threadId": thread_id,
            "turnStart": turn_response.get("result", {}),
            "turnCompleted": completed.get("params", {}),
        }
    finally:
        if proc.poll() is None:
            proc.terminate()
            try:
                proc.wait(timeout=3)
            except subprocess.TimeoutExpired:
                proc.kill()
                proc.wait(timeout=3)


def main() -> int:
    args = parse_args()
    if args.timeout_sec < 1:
        fail("--timeout-sec must be at least 1")
    prompt = read_prompt(args)
    out_dir = Path(args.out).expanduser().resolve()
    cwd = Path(args.cwd).expanduser().resolve()
    if not cwd.is_dir():
        fail(f"cwd not found: {cwd}")

    artifacts = base_artifacts(args, prompt, out_dir, cwd)
    write_prepared(out_dir, artifacts, prompt)

    if args.execute:
        try:
            execution = execute_handoff(args, artifacts, out_dir)
        except Exception as exc:  # noqa: BLE001 - command boundary must summarize failure.
            artifacts["status"] = "failed"
            artifacts["error"] = str(exc)
            (out_dir / "codex-app-server-plan.json").write_text(
                json.dumps(artifacts, indent=2, sort_keys=True) + "\n",
                encoding="utf-8",
            )
            fail(str(exc))
        artifacts.update(execution)
        (out_dir / "codex-app-server-plan.json").write_text(
            json.dumps(artifacts, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )

    print(f"wrote: {out_dir / 'codex-handoff-prompt.md'}")
    print(f"wrote: {out_dir / 'codex-app-server-plan.json'}")
    print(f"wrote: {out_dir / 'codex-app-server-messages.jsonl'}")
    if args.execute:
        print(f"wrote: {out_dir / 'codex-app-server-transcript.jsonl'}")
    print(f"status: {artifacts['status']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
