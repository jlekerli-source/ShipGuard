# Docs Check

`codex-maintainer docs-check` scans Markdown files for broken local links.

Use it before publishing docs-heavy releases:

```bash
./bin/codex-maintainer docs-check . --out /tmp/codex-maintainer-docs-check
```

The command ignores external URLs and in-page anchors. It checks relative links such as `docs/cli.md`, `../fixtures/arena`, and local image or report paths.

For GitHub Actions, use `actions/docs-check` to run the same audit and upload the generated report directory as an artifact. See `docs-check-action.md`.

With `--out`, it writes:

- `docs-check.json`
- `docs-check.md`

The command exits non-zero with `status: blocked` when any local Markdown link points at a missing file or directory.
