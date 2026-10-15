# fab0

fab0 is a toolkit for building and operating software factories. A factory is one or more pipelines of steps, logical operators and gates, wired in short YAML files, run by Claude Code agents and delivered through git and an issue tracker. fab0 provides the engine that runs a pipeline end to end, the git workflow, tracker utilities and examples; which agents and skills a factory uses is up to the factory.

- **Building blocks, not a factory.** fab0 holds only what runs, checks and connects pipelines. Agents, skills, artifact formats and processes belong to the factory.
- **The project carries the wiring.** Pipelines, steps, gates and artifacts are short files in the project's `.fab0/` directory. Agents and skills are ordinary Claude Code agents, skills and plugins, and need no fab0 conventions.
- **A script routes, not the model.** A deterministic engine picks the next steps from the pipeline, the ledger in git and the facts in the tracker.
- **Agents do the work the gates allow.** Every transition is a gate: none, automatic or human. A run works on its own branch, with sub-branches for parallel steps, and the dependencies it declares or the tracker carries decide what can run at once.
- **Each fact has one home.** Git holds content and delivery. The tracker holds human decisions. A board only shows the state.

## Status

Pre-alpha. fab0 0.6 is the toolkit; 0.5 was a delivery factory with its own agents built in. The [docs](https://github.com/fab0-dev/docs/blob/main/docs/index.md) describe 0.6, and the [`story` and `triage` examples](https://github.com/fab0-dev/fab0-examples) are ready to copy. What comes next is in the [roadmap](ROADMAP.md), and why fab0 is built as it is, in [the decisions](DECISIONS.md).

## Repositories

fab0 is built with a factory made from fab0. This repository is the home repo of the fab0 product. It holds the rules and fab0's own factory, copied from the `story` example, in `.fab0/`. Code and documentation live in their own repositories:

| Repository | Contents |
|---|---|
| [`fab0-dev/fab0`](https://github.com/fab0-dev/fab0) | Home repo: this README, the rules, and fab0's own factory |
| [`fab0-dev/fab0-core`](https://github.com/fab0-dev/fab0-core) | The `fab0` plugin marketplace and the core plugin: the engine, the schemas, the git and tracker utilities, and the skills fab0 itself needs |
| [`fab0-dev/fab0-examples`](https://github.com/fab0-dev/fab0-examples) | Example factories to copy, with their agents and skills, also a plugin marketplace: `story` (delivery) and `triage` |
| [`fab0-dev/docs`](https://github.com/fab0-dev/docs) | The user documentation |

## Installing

Install the core plugin through Claude Code's plugin system:

```
/plugin marketplace add fab0-dev/fab0-core
/plugin install fab0@fab0
```

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

A clone that installed fab0 0.3.0 or earlier registered the marketplace pinned to a tag, and keeps that pin. Register it once more, from the repo root, then restore the committed settings:

```bash
claude plugin marketplace remove fab0
```

```bash
claude plugin marketplace add fab0-dev/fab0-core --scope project
```

```bash
claude plugin install fab0@fab0 --scope project
```

```bash
git checkout -- .claude/settings.json
```

### Requirements

The engine needs [`uv`](https://docs.astral.sh/uv/) and an authenticated [`gh`](https://cli.github.com/).

## Licence

[Apache 2.0](LICENSE)
