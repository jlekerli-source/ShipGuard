# Maintainer Arena Example

Run the public fixture pack:

```bash
./bin/codex-maintainer arena run --fixture fixtures/arena --out /tmp/arena
```

Expected summary:

```text
average: 6.25/12
```

Expected aggregate fields in `results.json`:

```json
{
  "case_count": 8,
  "average_total": 6.25,
  "high_risk_finding_count": 8,
  "validation_evidence_cases": 3,
  "validation_evidence_ratio": 0.38,
  "validation_quality_average": 0.75,
  "scope_control_average": 1.25
}
```

The case reports are written under `runs/<case-id>/`.
