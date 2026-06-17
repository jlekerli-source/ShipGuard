# Maintainer Arena Example

Run the public fixture pack:

```bash
./bin/shipguard arena run --fixture fixtures/arena --out /tmp/arena
```

Expected summary:

```text
average: 5.62/12
```

Expected aggregate fields in `results.json`:

```json
{
  "case_count": 13,
  "average_total": 5.62,
  "high_risk_finding_count": 14,
  "validation_evidence_cases": 5,
  "validation_evidence_ratio": 0.38,
  "validation_quality_average": 0.77,
  "scope_control_average": 1.23
}
```

The case reports are written under `runs/<case-id>/`.
