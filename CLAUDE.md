# fab0: home repo

This is the home repo of the fab0 product. fab0 is built with fab0.

This repo holds only what a home repo needs:
- the README and these rules;
- `.fab0/`, the wiring: the `story` recipe, with `fab0.yaml` naming this repo as home and `fab0-core` and `fab0-recipes` as code repos;
- `specs/` and `work/{run}/`, which fab0's own runs write;
- `.claude/settings.json`;
- later, the user documentation.

Code goes elsewhere:
- the resolver, the schemas, and the core agents and skills go in `fab0-dev/fab0-core`;
- recipes go in `fab0-dev/fab0-recipes`;
- extension plugins go in `fab0-dev/fab0-plugins`.

The checkouts are siblings under one parent directory.

## Working on fab0 with fab0

Changes to fab0 start as a Story issue here (fab0-dev/fab0, type Story) and run with `/fab0:run <issue>` in a trusted Claude Code session in this repo. The sibling checkouts must be in place. `/fab0:inbox` shows what is waiting. Don't hand-edit `specs/` or `work/`: they belong to runs, and runs revise them.

## Working rules

1. One step is one PR. If a step changes the design, the PR description says so.
2. The predecessor project is read, never copied. Everything carried over is rewritten in fab0's terms. No noun from the predecessor or from a consuming project may reach a public repo, its issues or its commits.
3. A part is ported only when a step needs it.
4. A step is done when its exit check has passed on a real run, not when its files exist.
5. A problem found in a consuming project comes back as a generic issue in the fab0 repo that owns the concern. If it can't be written generically, it belongs to the project.

`.claude/settings.json` enables the `fab0` plugin from `fab0-dev/fab0-core`, pinned to a release tag. To move to a new release, change the `ref` in a PR. The same file denies merging PRs, force pushes, pushes to `main` and edits under `.github/`: people merge, and fab0 never does.

`guides/` is local seed material. It is gitignored. Never cite it in a committed file.

## Principles

- P1. Plugins carry behaviour; the project carries wiring. Any plugin can join a pipeline without knowing about fab0.
- P2. The model does not route. The resolver picks the next stage, and the orchestrating session only executes it.
- P3. Git is the truth for content, GitHub for human decisions. The Projects board is a projection.
- P4. Verify at the source, cheaply, with standard tools: schemas on return, linters on write, a review agent for judgment.
- P5. Prefer an artifact a tool can check over a section of prose: tasks are YAML, a verdict is JSON, scenarios are `.feature` files.
- P6. No compile step. The YAML is read at run time and validated before anything runs.
- P7. Name capabilities, not vendors. A stage asks for a model class, and the project maps classes to models.
- P8. Add a rule only when a run has needed it.
