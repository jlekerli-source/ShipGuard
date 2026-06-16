# Maintainer Arena Example

Run the public fixture pack:

```bash
./bin/codex-maintainer arena run --fixture fixtures/arena --out /tmp/arena
```

Expected summary:

```text
average: 6.50/12
```

Expected aggregate fields in `results.json`:

```json
{
  "case_count": 6,
  "average_total": 6.50,
  "high_risk_finding_count": 5,
  "validation_evidence_cases": 2,
  "validation_evidence_ratio": 0.33,
  "validation_quality_average": 0.67,
  "scope_control_average": 1.33
}
```

The case reports are written under `runs/<case-id>/`.
