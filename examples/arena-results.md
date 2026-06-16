# Maintainer Arena Example

Run the public fixture pack:

```bash
./bin/codex-maintainer arena run --fixture fixtures/arena --out /tmp/arena
```

Expected summary:

```text
average: 6.67/12
```

Expected aggregate fields in `results.json`:

```json
{
  "case_count": 9,
  "average_total": 6.67,
  "high_risk_finding_count": 8,
  "validation_evidence_cases": 4,
  "validation_evidence_ratio": 0.44,
  "validation_quality_average": 0.89,
  "scope_control_average": 1.33
}
```

The case reports are written under `runs/<case-id>/`.
