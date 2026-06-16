# Maintainer Reliability OS

The toolkit now has a full evidence loop:

```text
policy -> autopsy -> arena -> review-comment -> ci-gate -> leaderboard -> self-audit
```

That loop gives maintainers a way to:

- configure project-specific risk rules
- audit individual AI coding runs
- benchmark public fixture packs
- turn reports into PR comments and badge JSON
- fail CI only when the project opts in
- publish stable leaderboard data
- audit the toolkit itself before release

The project remains deliberately small: public fixtures, plain config, Bash scripts, markdown docs, and release tarballs.
