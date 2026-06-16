# Maintainer Reliability OS

The toolkit now has a full evidence loop:

```text
policy -> autopsy -> sarif -> arena-import -> arena-sign -> arena -> review-comment -> ci-gate -> ci-summary -> check-run -> check-run-post -> leaderboard -> release-manifest -> release-index -> self-audit -> next-goal
```

That loop gives maintainers a way to:

- configure project-specific risk rules
- audit individual AI coding runs
- export findings into SARIF for CI consumers
- import external fixture packs with basic safety checks
- sign and verify fixture-pack integrity metadata
- benchmark public fixture packs
- turn reports into PR comments and badge JSON
- fail CI only when the project opts in
- make workflow-run evidence readable through GitHub step summaries
- prepare GitHub Check Run payloads and optionally post them with an explicit token
- publish stable leaderboard data
- write release manifests and proof ledgers from release tarballs
- catalog release proof manifests across releases
- audit the toolkit itself before release
- generate the next slash-goal plan after release verification

The project remains deliberately small: public fixtures, plain config, Bash scripts, markdown docs, and release tarballs.
