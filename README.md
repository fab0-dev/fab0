# fab0

> **This is the home repo of fab0, not its code.** It holds the product's rules, roadmap and decisions, and the factory that builds fab0. The engine lives in [`fab0-core`](https://github.com/fab0-dev/fab0-core), the example factories in [`fab0-examples`](https://github.com/fab0-dev/fab0-examples), and the documentation in [`docs`](https://github.com/fab0-dev/docs).

## Where to go

| You want to | Go to |
|---|---|
| Learn fab0 and set it up in your project | [The docs](https://github.com/fab0-dev/docs/blob/main/docs/index.md) |
| Read or change the engine, the schemas, the git and tracker utilities | [`fab0-dev/fab0-core`](https://github.com/fab0-dev/fab0-core) |
| Copy a ready-made factory (`story`, `triage`) | [`fab0-dev/fab0-examples`](https://github.com/fab0-dev/fab0-examples) |
| See what comes next | [`ROADMAP.md`](ROADMAP.md) |
| Understand why fab0 is built as it is | [`DECISIONS.md`](DECISIONS.md) |
| Propose a change to fab0 | [An issue in this repo](https://github.com/fab0-dev/fab0/issues) |
| Watch fab0 build itself | [This repo's pull requests](https://github.com/fab0-dev/fab0/pulls), [`specs/`](specs) and `work/` |

## What fab0 is

fab0 is a toolkit for building and operating software factories. A factory is one or more pipelines of steps, logical operators and gates, wired in short YAML files, run by Claude Code agents and delivered through git and an issue tracker. fab0 provides the engine that runs a pipeline end to end, the git workflow, tracker utilities and examples; which agents and skills a factory uses is up to the factory.

- **Building blocks, not a factory.** fab0 holds only what runs, checks and connects pipelines. Agents, skills, artifact formats and processes belong to the factory.
- **The project carries the wiring.** Pipelines, steps, gates and artifacts are short files in the project's `.fab0/` directory. Agents and skills are ordinary Claude Code agents, skills and plugins, and need no fab0 conventions.
- **A script routes, not the model.** A deterministic engine picks the next steps from the pipeline, the ledger in git and the facts in the tracker.
- **Agents do the work the gates allow.** Every transition is a gate: none, automatic or human. A run works on its own branch, with sub-branches for parallel steps, and the dependencies it declares or the tracker carries decide what can run at once.
- **Each fact has one home.** Git holds content and delivery. The tracker holds human decisions. A board only shows the state.

## Status

fab0 0.6 is the toolkit, rebuilt from the 0.5 delivery factory that had its own agents built in. fab0 builds itself with it: fab0's own factory and the docs factory have each delivered real runs end to end. The [docs](https://github.com/fab0-dev/docs/blob/main/docs/index.md) describe 0.6, and the [`story` and `triage` examples](https://github.com/fab0-dev/fab0-examples) are ready to copy. Next comes use beyond fab0: first projects other than fab0, headless runs and teams, as laid out in the [roadmap](ROADMAP.md).

## What this repo is for

fab0 is built with a factory made from fab0, and this repo is where that factory runs. It holds no product code: the tasks of a run land as pull requests in the code repositories.

| Path | Contents |
|---|---|
| `README.md`, `ROADMAP.md`, `DECISIONS.md` | What fab0 is, the steps ahead with their exit checks, and why fab0 is built as it is |
| `CLAUDE.md` | The working rules and principles, for the people and agents working on fab0 |
| `.fab0/` | fab0's own factory, copied from the `story` example: pipelines, steps, artifacts and schemas |
| `.claude/` | The factory's agents, its `spec-format` skill, the merge guard and the settings |
| `specs/<run>.md` | The spec each run wrote |
| `work/<run>/ledger/` | Each run's ledger: what ran, when, and with what result |

The product is spread over four repositories:

| Repository | Contents |
|---|---|
| [`fab0-dev/fab0`](https://github.com/fab0-dev/fab0) | Home repo (this one): the rules, the roadmap, the decisions and fab0's own factory |
| [`fab0-dev/fab0-core`](https://github.com/fab0-dev/fab0-core) | The `fab0` plugin marketplace and the core plugin: the engine, the schemas, the git and tracker utilities, and the skills fab0 itself needs |
| [`fab0-dev/fab0-examples`](https://github.com/fab0-dev/fab0-examples) | Example factories to copy, with their agents and skills, also a plugin marketplace: `story` (delivery) and `triage` |
| [`fab0-dev/docs`](https://github.com/fab0-dev/docs) | The user documentation |

### How a change to fab0 is made

1. A change starts as a **Story** issue in this repo.
2. A maintainer runs it with `/fab0:run <issue>`. The `spec-author` agent writes `specs/<run>.md` and a task list, and the product owner reviews that pull request.
3. Each task becomes a sub-issue, is implemented by the `implementer` agent in its own repository, reviewed by the `reviewer` agent, and merged into that repository's run branch. Tasks that change behaviour include the docs change.
4. When the run ends, a person merges each repository's run pull request into `main`.

So a pull request here usually carries a spec, a ledger or a change to the rules, and the matching code change is a pull request in `fab0-core`, `fab0-examples` or `docs` from the same run.

## Using fab0

Install the core plugin through Claude Code's plugin system:

```
/plugin marketplace add fab0-dev/fab0-core
/plugin install fab0@fab0
```

Then follow [the docs](https://github.com/fab0-dev/docs/blob/main/docs/index.md) to wire a factory into your project, or start from one of the [examples](https://github.com/fab0-dev/fab0-examples).

The engine needs [`uv`](https://docs.astral.sh/uv/) and an authenticated [`gh`](https://cli.github.com/).

## Running fab0's own factory

The rest of this README is for maintainers who run fab0's factory from a checkout of this repo. Clone `fab0`, `fab0-core`, `fab0-examples` and `docs` as siblings under one parent directory: the factory's `repos` point at them. Runs start from this checkout on `main`.

### Installing the plugin

This repo's `.claude/settings.json` declares the `fab0` marketplace, with auto-update, and enables the plugin. That declaration alone isn't enough for every client: the desktop app, for example, doesn't load a plugin that is enabled but not installed. Install it once for this repo, from the repo root:

```bash
claude plugin install fab0@fab0 --scope project
```

The command can rewrite `.claude/settings.json` in a different order; keep the committed version with `git checkout -- .claude/settings.json`. Restart open sessions afterwards, since plugins load when a session starts. `claude plugin list` should then show `fab0@fab0` with scope `project`, and headless `claude -p` runs load it too.

Plugins you enabled for all your projects load here as well. To keep one out of this repo's agents' context, turn it off for this repo only; that writes the gitignored `.claude/settings.local.json`:

```bash
claude plugin disable <plugin>@<marketplace> --scope local
```

### Updating

The marketplace points at the latest `fab0` release, and auto-update fetches a new one in the background during a session; it loads at the next start. Nothing in this repo changes for a release. To update at once:

```bash
claude plugin marketplace update fab0
```

```bash
claude plugin update fab0@fab0 --scope project
```

## Licence

[Apache 2.0](LICENSE)
