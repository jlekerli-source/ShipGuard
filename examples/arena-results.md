# Maintainer Arena Example

Run the public fixture pack:

```bash
./bin/shipguard arena run --fixture fixtures/arena --out /tmp/arena
```

Expected summary:

```text
average: 6.36/12
```

Expected aggregate fields in `results.json`:

```json
{
  "case_count": 11,
  "average_total": 6.36,
  "high_risk_finding_count": 11,
  "validation_evidence_cases": 5,
  "validation_evidence_ratio": 0.45,
  "validation_quality_average": 0.91,
  "scope_control_average": 1.27
}
```

The case reports are written under `runs/<case-id>/`.
