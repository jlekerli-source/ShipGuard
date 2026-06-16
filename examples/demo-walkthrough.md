# Demo Walkthrough

This walkthrough proves the toolkit without private Ringly code.

## From A Clone

```bash
./bin/codex-maintainer validate
./bin/codex-maintainer init ios fixtures/demo-ios-repo --force
./bin/codex-maintainer doctor fixtures/demo-ios-repo
./bin/codex-maintainer init web /tmp/demo-web-repo --force
./bin/codex-maintainer doctor web /tmp/demo-web-repo
./bin/codex-maintainer score examples/scored-run.md
./bin/codex-maintainer autopsy \
  --run fixtures/autopsy/good-run/run.md \
  --task fixtures/autopsy/good-run/task.md \
  --diff fixtures/autopsy/good-run/diff.patch \
  --tests fixtures/autopsy/good-run/tests.log \
  --out /tmp/autopsy-good
```

## From A Release Package

```bash
tar -xzf codex-maintainer-v3.14.0.tar.gz
cd codex-maintainer-v3.14.0
./bin/codex-maintainer version
PREFIX="$HOME/.local" ./scripts/install.sh
"$HOME/.local/bin/codex-maintainer" init ios /tmp/demo-ios-repo
"$HOME/.local/bin/codex-maintainer" doctor /tmp/demo-ios-repo
"$HOME/.local/bin/codex-maintainer" init web /tmp/demo-web-repo
"$HOME/.local/bin/codex-maintainer" doctor web /tmp/demo-web-repo
"$HOME/.local/bin/codex-maintainer" autopsy \
  --run fixtures/autopsy/dangerous-run/run.md \
  --task fixtures/autopsy/dangerous-run/task.md \
  --diff fixtures/autopsy/dangerous-run/diff.patch \
  --out /tmp/autopsy-dangerous
```

## What The Demo Shows

- `validate` checks this workflow-bundle repo.
- `init ios` copies starter workflow files into a target repo.
- `init web` copies the web workflow starter into a target repo.
- `doctor` confirms copied workflow files exist.
- `score` turns a run summary into a maintainer-quality verdict.
- `autopsy` checks whether an agent's claims are backed by task, diff, and test evidence.
