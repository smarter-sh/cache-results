# cache-results Agent Skills

This folder holds the [Agent Skills](https://agentskills.io/specification) for
working on cache-results with an AI coding agent such as Claude Code. This
README is written mostly for people.

A skill is a folder of written know-how that an agent loads only when a task
needs it. Each one contains a `SKILL.md` file, and sometimes a `references/`
folder. These skills cover how this repository is built, tested, documented,
released and committed. They are developer tooling, like the `Makefile` and
`.pre-commit-config.yaml`, and the package never loads them.

They are adapted from the skills of
[Smarter](https://github.com/smarter-sh/smarter/tree/main/skills), where this
package's code began, so that both are developed the same way. Smarter's skills
that only concern its platform (Docker, Kubernetes, React, migrations, ...)
have no counterpart here. Load them from `../smarter/skills/` when a task leads
into Smarter, e.g. to bump Smarter's pin of this package or change its hooks.

## What's here

Start with `cache-results-development`. It sets out the rules that apply to
every change, the package's architecture, and which narrower skill to load.

| Skill                        | Use it when                                                                      |
| ---------------------------- | -------------------------------------------------------------------------------- |
| `cache-results-development`  | You're making any change. Start here.                                            |
| `cache-results-testing`      | You're writing or running tests, against either cache, or raising coverage.      |
| `cache-results-docstrings`   | You're writing docstrings, which become the api reference.                       |
| `cache-results-typing`       | You're writing type annotations, especially with `Any`.                          |
| `cache-results-code-quality` | You're about to finish a change and need to run the pre-commit hooks.            |
| `cache-results-git-commits`  | You've been asked to write a commit message.                                     |
| `cache-results-release`      | You're working on CI, Codecov, requirements, semantic-release or PyPI.           |
| `cache-results-sphinx-docs`  | You're editing the docs or ADRs, publishing the site, or changing its Terraform. |

## Claude Code

Claude Code looks for project skills in `.claude/skills/`. This repository
connects the two folders with a committed symlink, `.claude/skills -> ../skills`,
as Smarter's does:

```bash
mkdir -p .claude
ln -s ../skills .claude/skills
```

Other agents that read `SKILL.md` folders can be pointed at this folder, or told
to read `skills/cache-results-development/SKILL.md` at the start of a session.

## When to add or change a skill

Add to a skill when you've explained the same thing to an agent twice, when a
mistake is costly (e.g. a change that makes every cached entry unreadable), when
a pattern isn't obvious from the code, or when checking a change takes a fragile
series of steps. Don't add one for what the code, the linters or CI already
enforce, for one-off facts, or for personal preferences. Prefer editing an
existing skill to adding one, and keep each `SKILL.md` short.

## Security considerations

A skill is a set of instructions that an agent follows, often without asking.
**Review a change to this folder as carefully as a change to CI.**

- **Some instructions forbid things on purpose**, e.g. never running
  `git commit`, or applying Terraform without a plan the user has seen. Don't
  remove a rule like that unless you mean to give agents that power.
- **The docs site's Terraform changes live AWS resources** in a shared account
  and DNS zone. The skills require a reviewed plan before every apply.
- **Skills can carry prompt injection.** Look for instructions unrelated to a
  skill's purpose, new scripts with network calls, and text that tells an agent
  to skip confirmations, hooks or safety rules.
- **Keep secrets out.** This repository is public: no credentials, account ids,
  private hostnames or customer data in a skill or an example.
