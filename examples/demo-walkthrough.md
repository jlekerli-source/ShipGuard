# Demo Walkthrough

This walkthrough proves the toolkit without private Ringly code.

## From A Clone

```bash
./bin/shipguard validate
./bin/shipguard init ios fixtures/demo-ios-repo --force
./bin/shipguard doctor fixtures/demo-ios-repo
./bin/shipguard init web /tmp/demo-web-repo --force
./bin/shipguard doctor web /tmp/demo-web-repo
./bin/shipguard score examples/scored-run.md
./bin/shipguard autopsy \
  --run fixtures/autopsy/good-run/run.md \
  --task fixtures/autopsy/good-run/task.md \
  --diff fixtures/autopsy/good-run/diff.patch \
  --tests fixtures/autopsy/good-run/tests.log \
  --out /tmp/autopsy-good
```

## From A Release Package

```bash
tar -xzf shipguard-v3.122.0.tar.gz
cd shipguard-v3.122.0
./bin/shipguard version
PREFIX="$HOME/.local" ./scripts/install.sh
"$HOME/.local/bin/shipguard" init ios /tmp/demo-ios-repo
"$HOME/.local/bin/shipguard" doctor /tmp/demo-ios-repo
"$HOME/.local/bin/shipguard" init web /tmp/demo-web-repo
"$HOME/.local/bin/shipguard" doctor web /tmp/demo-web-repo
"$HOME/.local/bin/shipguard" autopsy \
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
