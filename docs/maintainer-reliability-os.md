# Maintainer Reliability OS

The toolkit now has a full evidence loop:

```text
policy -> autopsy -> sarif -> arena -> review-comment -> ci-gate -> ci-summary -> leaderboard -> self-audit -> next-goal
```

That loop gives maintainers a way to:

- configure project-specific risk rules
- audit individual AI coding runs
- export findings into SARIF for CI consumers
- benchmark public fixture packs
- turn reports into PR comments and badge JSON
- fail CI only when the project opts in
- make workflow-run evidence readable through GitHub step summaries
- publish stable leaderboard data
- audit the toolkit itself before release
- generate the next slash-goal plan after release verification

The project remains deliberately small: public fixtures, plain config, Bash scripts, markdown docs, and release tarballs.
