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

In this repo, `.claude/settings.json` already declares the `fab0` marketplace (pinned to a release tag) and enables the plugin. Claude Code offers it once you trust the folder. The resolver needs [`uv`](https://docs.astral.sh/uv/) and an authenticated [`gh`](https://cli.github.com/).

## Licence

[Apache 2.0](LICENSE)
