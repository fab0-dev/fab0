# fab0: home repo

This is the home repo of the fab0 product. fab0 is a toolkit for building and operating software factories: principles, directives and tools, not a factory itself. fab0 is built with a factory made from fab0.

## Refactor mode

fab0 is being refactored from a delivery factory into that toolkit. Until step R8 of [`REFACTOR.md`](REFACTOR.md):
- `REFACTOR.md` is the plan, the tracker and the decision log. Read it before any change, and update it in the same PR as the step you do.
- Work is done by hand in ordinary sessions. Don't use `/fab0:run` or `/fab0:inbox`: the 0.5 factories are broken against the coming core. The `fab0` plugin is disabled in `.claude/settings.json`.
- `ROADMAP.md` is suspended.
- The docs change in one step, R7, instead of with each change (working rule 1).
- Exit checks before R6 run on fixtures; a real run ends the refactor (working rule 4).

## What this repo holds

- the README, these rules and `REFACTOR.md`;
- `.claude/settings.json`;
- `ROADMAP.md`: the steps that build fab0 and their exit checks, suspended until R8;
- after R8, `.fab0/` (fab0's own factory, copied from the `story` example) and what its runs write.

Code goes elsewhere:
- the engine, the schemas, the action catalogue, the tracker adapters and the skills fab0 itself needs go in `fab0-dev/fab0-core`;
- example factories, with their agents and skills, go in `fab0-dev/fab0-examples` (formerly `fab0-recipes`);
- the user documentation goes in `fab0-dev/docs`.

The checkouts are siblings under one parent directory.

## Working on fab0 with fab0

Suspended until R8. Afterwards, changes to fab0 start as a Story issue here and run with `/fab0:run <issue>` in a trusted Claude Code session, with the sibling checkouts in place.

## Working rules

1. One step is one PR. If a step changes the design, the PR description says so. A Story that changes behaviour or the design includes a task in the `docs` repo, so the docs change with the code.
2. The predecessor project is read, never copied. Everything carried over is rewritten in fab0's terms. No noun from the predecessor or from a consuming project may reach a public repo, its issues or its commits.
3. A part is ported only when a step needs it.
4. A step is done when its exit check has passed on a real run, not when its files exist.
5. A problem found in a consuming project comes back as a generic issue in the fab0 repo that owns the concern. If it can't be written generically, it belongs to the project.

`.claude/settings.json` declares the `fab0` marketplace (`fab0-dev/fab0-core`, auto-update), with the plugin disabled during the refactor. It denies merging PRs, force pushes, pushes to `main` and edits under `.github/`: people merge during the refactor. From R8, an `auto` gate may merge a reviewer-approved PR into a run branch, never into `main` unless a pipeline allows it; see `REFACTOR.md`, "Agent review and merge".

`guides/` is local seed material, superseded by `fab0-dev/docs` and `REFACTOR.md`. It is gitignored. Never cite it in a committed file.

## Principles

- P0. fab0 ships building blocks, not a factory. Core holds only what executes, validates and connects pipelines, plus the agents and skills fab0 itself needs. Every other agent, skill, artifact format and process belongs to a factory.
- P1. Plugins carry behaviour; the project carries wiring. fab0 is agent-agnostic: any agent or skill can be a step without knowing about fab0.
- P2. The model does not route. The engine picks the next steps, and the orchestrating session only executes them.
- P3. Git is the truth for content and delivery; the tracker is the truth for human decisions. Branches, PRs and merges carry the work. The board is a projection.
- P4. Verify at the source, cheaply, with standard tools: schemas on return, linters on write, a review agent for judgment.
- P5. Recommend artifacts a tool can check; don't prescribe formats. Examples show good practice; factories choose.
- P6. No compile step. The YAML is read at run time and validated before anything runs.
- P7. Name capabilities, not vendors. A step asks for a model class, and the project maps classes to models.
- P8. Add a rule only when a run has needed it.
- P9. Agents do as much of the work as the gates allow. Every transition is a gate: `none`, `auto` or `human`. People take part where a gate is `human`, or where an `auto` gate escalates.
- P10. A run works on its own branch. Steps work on sub-branches that merge into the run branch, so work runs in parallel. Only the run's final result merges into the base branch, unless the pipeline is configured otherwise.
- P11. Parallelism is bounded by dependencies, and the factory respects them wherever they are declared: in the pipeline's artifacts (data flow, `after`, path claims) and in the tracker's own relations (blocked-by, parent and sub-issue). The engine checks them before work starts and raises blocking signals. It serializes what would conflict and waits on what must come first.
