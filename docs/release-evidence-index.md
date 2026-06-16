# Release Evidence Index

`codex-maintainer release-evidence index` collects multiple release evidence site exports into one static release history.

Use it after generating one or more evidence sites:

```bash
./bin/codex-maintainer release-evidence index \
  --site /tmp/codex-maintainer-previous-site \
  --site /tmp/codex-maintainer-v3.19.0-site \
  --out /tmp/codex-maintainer-evidence-history \
  --title "Codex Maintainer Release Evidence"
```

Outputs:

- `index.html`
- `evidence-index.json`
- `README.md`
- `sites/<release>/index.html`
- `sites/<release>/evidence.json`
- copied source files from each included evidence site

The index sorts semantic versions from newest to oldest, links to each copied evidence site, and records release status, artifact SHA-256, asset counts, required missing counts, and release-diff status. It blocks when any included evidence site is not passing.

Use `codex-maintainer release-evidence bundle` when you want the local command to build the evidence site and index together from downloaded release assets. See `release-evidence-bundle.md`.

For GitHub Actions, set `build-index: true` on `jlekerli-source/ringly-codex-workflows/actions/release-evidence@v3.19.0`. See `release-evidence-action.md`.
