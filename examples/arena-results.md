# Maintainer Arena Example

Run the public fixture pack:

```bash
./bin/shipguard arena run --fixture fixtures/arena --out /tmp/arena
```

Expected summary:

```text
average: 6.00/12
```

Expected aggregate fields in `results.json`:

```json
{
  "case_count": 12,
  "average_total": 6.00,
  "high_risk_finding_count": 12,
  "validation_evidence_cases": 5,
  "validation_evidence_ratio": 0.42,
  "validation_quality_average": 0.83,
  "scope_control_average": 1.25
}
```

The case reports are written under `runs/<case-id>/`.
