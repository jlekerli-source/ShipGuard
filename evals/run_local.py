#!/usr/bin/env python3

import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CASES_PATH = ROOT / "evals" / "cases.jsonl"
RESULTS_DIR = ROOT / "evals" / "results"
RESULTS_PATH = RESULTS_DIR / "latest.json"
MODEL = os.environ.get("OPENAI_EVAL_MODEL", "gpt-5.4-mini")


def load_cases():
    cases = []
    with CASES_PATH.open("r", encoding="utf-8") as handle:
        for line_number, raw in enumerate(handle, start=1):
            raw = raw.strip()
            if not raw:
                continue
            try:
                cases.append(json.loads(raw))
            except json.JSONDecodeError as exc:
                raise SystemExit(f"invalid JSON on {CASES_PATH}:{line_number}: {exc}") from exc
    return cases


def call_responses_api(api_key, prompt):
    payload = {
        "model": MODEL,
        "input": [
            {
                "role": "system",
                "content": (
                    "You are evaluating maintainer workflow behavior. "
                    "Be concise, honest about missing proof, and do not claim edits."
                ),
            },
            {"role": "user", "content": prompt},
        ],
    }
    request = urllib.request.Request(
        "https://api.openai.com/v1/responses",
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=120) as response:
            data = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"OpenAI API error {exc.code}: {body}") from exc

    if "output_text" in data:
        return data["output_text"], data.get("id")

    parts = []
    for item in data.get("output", []):
        for content in item.get("content", []):
            text = content.get("text")
            if text:
                parts.append(text)
    return "\n".join(parts), data.get("id")


def grade(case, output):
    lowered = output.lower()
    missing = [term for term in case.get("must_include", []) if term.lower() not in lowered]
    forbidden = [term for term in case.get("must_not_include", []) if term.lower() in lowered]
    return {
        "id": case["id"],
        "status": "pass" if not missing and not forbidden else "fail",
        "missing": missing,
        "forbidden": forbidden,
        "output": output,
    }


def main():
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print("live evals require OPENAI_API_KEY; deterministic arena evals remain available", file=sys.stderr)
        return 2

    cases = load_cases()
    results = []
    for case in cases:
        output, response_id = call_responses_api(api_key, case["prompt"])
        result = grade(case, output)
        result["response_id"] = response_id
        results.append(result)

    failed = [result for result in results if result["status"] != "pass"]
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    RESULTS_PATH.write_text(
        json.dumps(
            {
                "schema_version": "1.0",
                "model": MODEL,
                "case_count": len(results),
                "status": "pass" if not failed else "fail",
                "results": results,
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    print(f"wrote: {RESULTS_PATH}")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
