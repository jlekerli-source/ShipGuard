# Maintainer Arena Example

Run the public fixture pack:

```bash
./bin/codex-maintainer arena run --fixture fixtures/arena --out /tmp/arena
```

Expected summary:

```text
average: 7.00/12
```

Expected aggregate fields in `results.json`:

```json
{
  "case_count": 10,
  "average_total": 7.00,
  "high_risk_finding_count": 8,
  "validation_evidence_cases": 5,
  "validation_evidence_ratio": 0.50,
  "validation_quality_average": 1.00,
  "scope_control_average": 1.40
}
```

The case reports are written under `runs/<case-id>/`.
