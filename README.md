# fab0

fab0 runs software delivery as pipelines of Claude Code agents. Each pipeline is wired in a few short YAML files and carried on GitHub.

- **Plugins carry behaviour.** Agents, skills and standards are ordinary Claude Code plugins. fab0 adds no conventions to them.
- **The project carries the wiring.** Stages, pipelines and artifact types are short files in the project's `.fab0/` directory.
- **A script routes, not the model.** The deterministic resolver `fab0-resolve` picks the next stage from the pipeline, the ledger in git and the facts on GitHub.
- **Each fact has one home.** Git holds content. GitHub holds human decisions; merging a stage's pull request is its approval. The Projects board only shows the state.

## Status

Pre-alpha. The resolver, the core agents and skills, and the `story` recipe exist; fab0 now runs its own changes as Stories. Expect breaking changes.

## Repositories

fab0 is built with fab0. This repository is the home repo of the fab0 product. It holds the product's wiring, its run ledgers and its documentation. Code lives in its own repositories:

| Repository | Contents |
|---|---|
| [`fab0-dev/fab0`](https://github.com/fab0-dev/fab0) | Home repo: this README, the rules, `.fab0/` (fab0's own wiring), and the specs and ledgers of fab0's own runs |
| [`fab0-dev/fab0-core`](https://github.com/fab0-dev/fab0-core) | The `fab0` plugin marketplace and the core plugin: the resolver, the schemas, and the core agents and skills |
| [`fab0-dev/fab0-recipes`](https://github.com/fab0-dev/fab0-recipes) | Ready-made `.fab0/` setups to copy into a project |
| `fab0-dev/fab0-plugins` | Optional extension plugins (planned) |

## Installing

Install the core plugin through Claude Code's plugin system:

```
/plugin marketplace add fab0-dev/fab0-core
/plugin install fab0@fab0
```

In this repo, `.claude/settings.json` already declares the `fab0` marketplace, with auto-update, and enables the plugin. That declaration alone isn't enough for every client: the desktop app, for example, doesn't load a plugin that is enabled but not installed. Install it once for this repo, from the repo root:

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

The resolver needs [`uv`](https://docs.astral.sh/uv/) and an authenticated [`gh`](https://cli.github.com/).

## Licence

[Apache 2.0](LICENSE)
