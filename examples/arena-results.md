# Maintainer Arena Example

Run the public fixture pack:

```bash
./bin/codex-maintainer arena run --fixture fixtures/arena --out /tmp/arena
```

Expected summary:

```text
average: 5.00/12
```

Expected aggregate fields in `results.json`:

```json
{
  "case_count": 3,
  "average_total": 5.00,
  "high_risk_finding_count": 4,
  "validation_evidence_cases": 1,
  "validation_evidence_ratio": 0.33,
  "validation_quality_average": 0.67,
  "scope_control_average": 1.00
}
```

The case reports are written under `runs/<case-id>/`.
