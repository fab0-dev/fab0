# Refactor: fab0 as a toolkit for building software factories

**Status:** R5 done; R6 in review (fab0-dev/fab0-core#30, fab0-dev/fab0-examples#6). Next step: **R7**.

This guide governs all work on fab0 until the refactor is done. It replaces `ROADMAP.md` and the "Working on fab0 with fab0" flow in `CLAUDE.md` until step R8. Sessions read it, do one step and edit it in the same pull request.

## How to use this guide

1. Read this file top to bottom before you change anything. `CLAUDE.md` still applies, except where its "Refactor mode" section says otherwise.
2. Take the first step in [Steps](#steps) whose box isn't ticked. If it depends on a decision marked *proposed*, settle the decision first and record the answer in [Decisions](#decisions).
3. Do the step by hand in an ordinary session. Nobody uses `/fab0:run` until R8; the fab0 plugin is disabled in this repo.
4. One step is one pull request in the repository it changes. A step too large for one PR is split into lettered sub-steps here first (R2a, R2b, …).
5. In the same pull request:
   - tick the step;
   - write its exit check result under it: what was run and what it showed;
   - add a line to the [Session log](#session-log).
   When the step's PR is in another repository, open a small companion PR here with those edits, or include them in the next home-repo PR.
6. Decisions are appended, never rewritten. To reverse one, add a new decision that names the one it replaces.
7. If the work shows the target model is wrong, change [Target model](#target-model) in its own PR, and say why in the log.

People merge every pull request during the refactor.

## Why

fab0 started as a delivery factory. Its core plugin, `fab0-core` 0.5.0, ships the engine and one way of delivering software together:
- the agents `spec-author`, `implementer` and `reviewer`;
- the `spec-format` skill;
- the `tasks.json` schema and the delivery parts of `review.json`;
- the `plan` and `deliver` actions, hard-coded in the resolver.

The resolver has a generic engine underneath: wiring, profiles, artifact types, hash-based staleness, the ledger, gates, write scope, `foreach` and lanes. Delivery semantics run through it:
- `action ∈ {plan, deliver}`;
- task ids `T\d+` and `task_rules`;
- `traces_to` and "scenarios" in the gate brief;
- the `## Delivered` table;
- a run is a GitHub issue, and every human gate is a merge into `main`.

The 0.5 pipeline also made a person merge every step and task pull request, even where a review agent had already approved it.

fab0 is not a factory. It is a set of principles, directives and tools for building and operating software factories. Everything not needed for that leaves the core. The existing factories, the `story` recipe here and the `docs` factory in `fab0-dev/docs`, count as broken until they are rebuilt on the new version. After the refactor, fab0 is developed again by a factory built with fab0 (step R8).

## Principles

They replace P1–P8 in `CLAUDE.md`, which carries the same list.

- **P0. fab0 ships building blocks, not a factory.** Core holds only what executes, validates and connects pipelines, plus the agents and skills fab0 itself needs. Every other agent, skill, artifact format and process belongs to a factory.
- **P1. Plugins carry behaviour; the project carries wiring.** fab0 is agent-agnostic: any agent or skill can be a step without knowing about fab0.
- **P2. The model does not route.** The engine picks the next steps; the session only executes them.
- **P3. Git is the truth for content and delivery; the tracker is the truth for human decisions.** Branches, pull requests and merges carry the work. The board is a projection.
- **P4. Verify at the source, cheaply, with standard tools:** schemas on return, linters on write, a review agent for judgment.
- **P5. Recommend artifacts a tool can check; don't prescribe formats.** Examples show good practice; factories choose.
- **P6. No compile step.** The YAML is read at run time and validated before anything runs.
- **P7. Name capabilities, not vendors.** A step asks for a model class, and the project maps classes to models.
- **P8. Add a rule only when a run has needed it.**
- **P9. Agents do as much of the work as the gates allow.** Every transition is a gate: `none`, `auto` or `human`. People take part only where a gate is `human`, or where an `auto` gate escalates.
- **P10. A run works on its own branch.** Steps work on sub-branches that merge into the run branch, so work runs in parallel at scale. Only the run's final result merges into the base branch, unless the pipeline is configured otherwise.
- **P11. Parallelism is bounded by dependencies, and the factory respects them wherever they are declared.** Dependencies come from the pipeline's artifacts (data flow, `after`, path claims) and from the tracker's own relations (blocked-by, parent and sub-issue). The engine checks all of them before work starts and raises blocking signals. It serializes what would conflict and waits on what must come first.

## Target model

This is the design R1 turns into schemas. The names are proposals until R1 confirms them.

### What fab0 provides

- **The engine.** `fab0-resolve` validates the wiring, computes which units are ready, renders briefs, records results and applies deterministic actions. Its subcommands are `validate`, `next`, `record`, `apply` and `status`.
- **The core schemas:** project, pipeline, step, artifact, gate verdict, ledger entry, return.
- **The action catalogue:** `git.*`, `pr.*` and `tracker.*`. Each action is an idempotent check plus apply.
- **Tracker adapters,** GitHub first.
- **The git workflow:** run branches, sub-branches, pull requests, merges.
- **The session skills fab0 itself needs:** `/fab0:run` executes, `/fab0:inbox` shows what is ready or blocked, and `fab0:github` covers whatever `apply` doesn't.
- **Examples** in `fab0-dev/fab0-examples`: complete factories to copy, which show good practice and are never required.

### Building blocks

| Block | File in `.fab0/` | Purpose |
|---|---|---|
| Project | `fab0.yaml`, `schema: 2` | repos, roles, tracker, model classes, profiles, pipelines, ledger path, `git` policy |
| Pipeline | `pipelines/<name>.yaml` | `trigger`, required `onStart` and `onEnd` (`[]` allowed), the `steps` tree |
| Step | `steps/<name>.yaml`, or inline | exactly one executor, plus `inputs`, `outputs`, `paths`, `after`, `owner`, `gate` |
| Operator | inside `steps` | a list is a sequence; `foreach`, `parallel`, `when`, and later `call` |
| Gate | `gate:` on a step or block node in the pipeline, never in a step file (D13) | the transition after it: `none`, `auto` or `human` |
| Artifact | `artifacts/<name>.yaml` | a typed piece of state that steps pass on, with a `kind` |

A step has exactly one executor:
- `agent`: any Claude Code agent by name (`plugin:agent`, or a file in `.claude/agents/`), with a model class and skills;
- `action`: a built-in fab0 action from the catalogue;
- `command`: a deterministic shell command;
- `tool`: an MCP or other tool call, made by the session and recorded like an agent's return.

Operators:
- **sequence:** a list of steps runs in order.
- **`foreach: <artifact>`:** fans out over the elements of a list artifact. Elements need an `id`, and may carry `after` (ids they wait for) and `paths` (what they write).
- **`parallel`:** named branches that run at once and join when all are done.
- **`when`:** runs its steps only if a condition holds. The condition language is closed and small: an artifact exists or has a value, a verdict is something, a tracker item has a label or field.
- **`call`:** runs another pipeline as a child. It is validated but refused until a factory needs it (P8).

Gates:
- `none`: the default, the work moves on.
- `auto`: `{agent: <name>, model: <class>}`, a review agent returning the core verdict (`approve`, `reject`, `escalate`, with reasons and findings), or `{command: "<cmd>"}`, a check whose exit code decides.
- `human`: a person decides by merging the unit's pull request or, for units without one, through the tracker.
- Options:
  - `merge: auto | human`: who merges the unit's pull request once the gate passes.
  - `retry: <n>`: how often a rejected unit re-runs with the findings in its brief.
  - `then: human`: what happens when the retries run out.

Artifact kinds, each with a hasher so staleness stays generic:
- `file`: a repository, a path template (`{run}`, `{unit}`), a format, an optional schema, `verify` and `keep`.
- `issue`: a tracker record: an item's body, a field or a comment.
- `pr`: a pull request's body or reviews.
- `tool`: a value read through an MCP or tool call.
- `none`: a step that hands nothing on.

Lifecycle:
- `onStart` and `onEnd` are required on every pipeline. They are optional on any block.
- Each is a list of actions.
- Today's `plan` becomes `foreach: tasks` with `onStart: [tracker.child.sync]`.
- Today's `deliver` becomes the pipeline's `onEnd`, for example `[git.sync-base, git.remove-run-artifacts, pr.ready, tracker.close]`.

### A sketch

```yaml
# .fab0/fab0.yaml
schema: 2
repos:
  home: {path: ., github: acme/shop}
  api:  {path: ../shop-api, github: acme/shop-api, key: API}
people:
  product-owner: {github: [po-user]}
tracker: {kind: github, owner: acme, project: 7}
git:
  base: main
  branching: run                # run | flat
  auto_merge: {into: [run]}     # base only with allow_base: true
models: {claude-code: {deep: opus, balanced: sonnet, fast: haiku}}
pipelines: [story]
```

```yaml
# .fab0/pipelines/story.yaml
pipeline: story
trigger: {issue: {type: Story}}
onStart: [git.run-branch, pr.open-run-draft, tracker.field: {Stage: started}]
steps:
  - step: spec
    gate: {human: {}}
  - foreach: tasks
    onStart: [tracker.child.sync]          # Task sub-issues, with blocked-by from `after`
    steps:
      - step: implement
        gate: {auto: {agent: reviewer, model: deep}, merge: auto, retry: 2, then: human}
  - when: {artifact: spec, section: Docs}
    steps: [docs]
onEnd: [git.sync-base, git.remove-run-artifacts, pr.ready, tracker.close]
```

```yaml
# .fab0/steps/implement.yaml
step: implement
agent: implementer            # a project agent; fab0 doesn't care where it comes from
model: balanced
inputs: [spec, unit]          # `unit` is the foreach element
outputs: []
repos: {write: [unit.repo], read: [all]}
paths: unit.paths             # the write claim the engine serializes on
owner: repo-owner
```

```yaml
# .fab0/artifacts/tasks.yaml       # the factory's format, not fab0's
artifact: tasks
kind: file
file: {repo: home, path: "work/{run}/tasks.yaml", format: yaml}
schema: schemas/tasks.json         # project-relative
keep: run
```

### Branching

- **`run`, the default:**
  - `onStart` cuts `fab0/<run>/base` from the base branch in every repository the run writes, and opens the run pull request into `main` as a draft, so the run is visible from its start.
  - Each step, or each element of a fan-out, works on its own sub-branch `fab0/<run>/<unit>`, cut from its parent branch, in its own worktree.
  - A unit's pull request targets its parent branch.
  - A unit that fans out again is the parent of its children, named `<unit>--<child>`. A git ref can't be both a file and a directory, which is why the run branch is `…/base` and children aren't `<unit>/<child>`.
  - A block (`foreach`, `parallel`, `when`) that has a gate gets a branch of its own: its children branch from it, and the block's gate governs the block's pull request into its parent. A block without a gate adds no branch; its children target the block's parent (D14).
  - The run's pull request into `main` is the last gate, `human` by default.
- **`flat`:** each unit's pull request targets the base branch. This is the 0.5 behaviour, for factories that want each step on `main`.
- **No force-push, anywhere.** A child is synced by merging its parent into it, never by a rebase.

### Dependencies and blocking

Before it hands work out, the engine gives each unit a state: `ready`, `running`, `blocked(<reason>)`, `waiting(<gate>)` or `done`. The reasons:

- **data:** an input artifact isn't produced yet, or is stale. Inferred from `inputs` and `outputs`; nothing to declare.
- **order:** an `after` dependency isn't merged into the parent yet. The unit branches from the parent only after that merge, so it builds on the result.
- **claim:** its `paths` overlap those of a running unit. Overlapping units are serialized into lanes; disjoint ones run in parallel.
- **cross-run claim:** another open run claims overlapping paths, read from its declared claims and its pull request's changed files. A policy chooses whether this warns or blocks.
- **tracker:** a relation the tracker itself carries, such as GitHub's blocked-by or parent and sub-issue:
  - The engine reads these on every `next`, through the tracker adapter. They count whether they point inside the run or outside it, at another run or a plain issue.
  - When an action creates tracker items for units, it projects their `after` as blocked-by relations.
  - From then on the tracker relation is the truth for that unit (P3). A person who adds or removes a blocked-by on the board changes what the engine hands out next.
  - Units without a tracker item use the artifact's declarations only.
- **conflict:** before a unit's pull request merges, the engine merges the parent into the sub-branch, re-runs the step's checks and tests mergeability (`git merge-tree`). A conflict is rework for the producing step, with the conflict in its brief. A second conflict escalates to `human`.
- **invalid dependency:** a cycle, or a dependency on an item closed without its work merged. Reported, never guessed around.

How states are handled:
- **Signals are projected, not stored twice.** `next` and `status` print them, and the tracker shows them as blocked-by relations and a field.
- **Claim of execution.** Pushing a unit's sub-branch to the remote is the lock. If the branch already exists, the unit is taken, so two machines can't run one unit. Assignment still says whose turn a `human` gate is.
- **Questions and human gates block only their unit** and what depends on it. Every other ready unit keeps going.
- **Limits.** `max_parallel` per run and the session's budget cap the fan-out.

### Agent review and merge

- `gate: {auto: {agent: reviewer}, merge: auto}`:
  - on `approve`, with the required checks green, `apply` merges the unit's pull request into its parent branch (`pr.merge`, with GitHub's auto-merge so it waits for checks);
  - `reject` re-runs the step with the findings;
  - `escalate`, or running out of retries, turns the gate into `human`.
- **Policy:** `git.auto_merge.into` defaults to `[run]`, meaning run branches only. Auto-merging into the base branch needs `allow_base: true` in `fab0.yaml`.
- **Enforcement.** Agents and people use the same GitHub identity, so GitHub alone can't tell them apart. The layers are:
  1. the pipeline's gate configuration;
  2. the policy check inside `apply`;
  3. a Claude Code `PreToolUse` hook, the merge guard, that blocks any `gh pr merge` issued by the model into the default branch, shipped in the examples' settings;
  4. GitHub rulesets on `main` (no direct push, no force-push).
  Later, a bot identity (a GitHub App) lets GitHub's own rules limit merges into `main` to people.

### Architecture check

What the model above changes from 0.5, and what to watch:

1. **Where inputs are read.** In 0.5 a merged spec on `main` was the input of later stages. Now the engine reads inputs at the parent branch's head, and pins that SHA in the brief and the ledger. Hashes and staleness are computed there.
2. **Several repositories.** Each written repository gets the same run branch name and its own run pull request. The run is done when all of them are merged. Reads across repositories are pinned to the other run branch's SHA.
3. **The base branch moves during a run.** The pipeline's `onEnd` merges the base branch into the run branch before the final pull request is marked ready. If an input artifact changed on the base branch, the affected steps go stale and run again.
4. **The ledger.** Entries are written on sub-branches and reach the run branch, then `main`, through merges. The 0.5 names (`<step>[-<unit>]-<attempt>.yaml`) can't collide. A gate's merge is read as "the entry is on that gate's target branch", no longer only "on base".
5. **Write scope** is checked per worktree, with one snapshot per parallel unit. Writes outside every listed repository are reported too (from fab0-dev/fab0#20).
6. **The engine writes.** In 0.5 the resolver never wrote to GitHub; a model applied actions by following the `fab0:github` skill. Merges, branch claims and syncs must be exact, so `apply` performs them itself (D5).
7. **Open:** cross-run claims across different projects, and runs started by triggers other than tracker items. Decided when a run needs them (P8).

## Inventory

What happens to each part, by repository. Paths are as of the baseline.

| Repository | Part | Fate | Step |
|---|---|---|---|
| fab0-core | `plugins/fab0/bin/fab0-resolve` | generalise into the engine; split into modules (D6) | R2, R3 |
| fab0-core | `schemas/{fab0,pipeline,stage,artifact,ledger-entry,return}.json` | replace with schema 2 (`stage` becomes `step`) | R1 |
| fab0-core | `schemas/review.json` | keep as the core gate verdict, without `unmet` | R1 |
| fab0-core | `schemas/tasks.json` | move to the `story` example | R5 |
| fab0-core | `agents/{spec-author,implementer,reviewer}.md` | move to the `story` example | R4, R5 |
| fab0-core | `skills/spec-format` | move to the `story` example | R4, R5 |
| fab0-core | `skills/run`, `skills/inbox` | rewrite for the new model | R4 |
| fab0-core | `skills/github` | shrink to what `apply` doesn't do | R4 |
| fab0-core | `scripts/check-agents.py` | move to the examples repo | R5 |
| fab0-core | `tests/`, `tests/fixtures/workspace` | rebuild on three fixture factories | R1, R2 |
| fab0-core | `work/` | delete (0.5 run records) | R2 |
| fab0-recipes | the repository | rename to `fab0-examples`; a marketplace | R5 |
| fab0-recipes | `story/` | rewrite as the `story` example on schema 2 | R5 |
| fab0-recipes | `scripts/check-recipes` | becomes `check-examples` | R5 |
| docs | `docs/` | rewrite for the toolkit | R7 |
| docs | `.fab0/`, `briefs/`, `work/` | archived in R0; the docs factory is rebuilt on schema 2 | R0, R7 |
| docs | `.claude/agents/docs-*`, `.claude/skills/docs-style` | keep: the docs repo's own factory (D9) | R7 |
| fab0 | `.fab0/`, `specs/`, `work/` | archived in R0; `.fab0/` returns as the `story` example | R0, R8 |
| fab0 | `ROADMAP.md` | suspended; rewritten from what remains | R0, R8 |
| — | `fab0-dev/fab0-plugins` | not created (D8) | — |

## Decisions

Append only. *Made* decisions are settled; *proposed* ones are settled at the step named.

- **D1. Delivery parts leave core for an examples repository.** `fab0-recipes` is renamed `fab0-examples`. Each example is a directory with its `.fab0/`, its agents and skills, and a README. *Made, 14 Oct 2026.*
- **D2. Pipelines run inside Claude Code.** The engine is deterministic and harness-neutral; a thin `/fab0:run` executes its steps, interactively or with `claude -p`. A stand-alone runner isn't planned. *Made, 14 Oct 2026.*
- **D3. This guide is the only tracker of the refactor.** No issues are opened for its steps. *Made, 14 Oct 2026.*
- **D4. The 0.5 run history and the issues that assume the 0.5 model are archived and closed.** Their findings are carried into this guide. *Made, 14 Oct 2026.*
- **D5. `apply` performs deterministic actions itself,** with `gh` and `git`, instead of a model following a skill. This reverses the 0.5 rule that the resolver never writes to GitHub. *Proposed; settle in R1.*
- **D6. The resolver is split into modules** under `plugins/fab0/lib/`, with a shim in `bin/`. It stays a uv PEP 723 script whose only dependencies are `pyyaml` and `jsonschema`. *Proposed; settle in R1.*
- **D7. The release is `fab0--v0.6.0`, with `schema: 2`.** Schema 1 is refused with a pointer to the docs, and there is no migration tool: the only schema 1 factories are fab0's own. No core release is made before R8, so auto-update can't break a project mid-refactor. *Proposed; settle in R1.*
- **D8. `fab0-plugins` isn't created.** Extensions that a factory needs become examples. *Proposed; settle in R1.*
- **D9. The docs repository keeps its local agents and skill** as its own factory, and rebuilds its wiring on schema 2. *Proposed; settle in R7.*
- **D10. Run branches, dependencies and blocking, and agent merges** are part of the core, as described in [Target model](#target-model). *Made, 14 Oct 2026; details confirmed in R1.*
- **D11. A factory's agents are distributed by copying.** An example ships its agents and skills as files to copy into `.claude/agents/` and `.claude/skills/`, each with a provenance line (`# from fab0-dev/fab0-examples <example>--v<version>`), as recipes already do. They also ship as a plugin in the examples marketplace, for teams that want updates without owning the files. Rejected: user-level agents, which aren't shared through git, and submodules, which are heavy. fab0's own factory copies the `story` example in R8. *Made, 14 Oct 2026.*
- **D12. D5, D6, D7 and D8 are made as written.** The owner chose each in R1. *Made, 14 Oct 2026.*
- **D13. Gates belong to the pipeline, never to a step file.** A gate is a transition between steps, and the same step may be gated differently in two pipelines. *Made in R1, 14 Oct 2026.*
- **D14. A gated block has a branch of its own.** A `foreach`, `parallel` or `when` with a gate gets a sub-branch; its children branch from it, and the block's gate governs the block's pull request into its parent. A block without a gate adds no branch. *Made in R1, 14 Oct 2026.*
- **D15. A factory keeps its own list formats.** A list artifact maps its element fields in `elements` (`id`, `title`, `repo`, `after`, `paths`, and `at` for a nested list). The engine reads those, and the factory's schema checks the rest. *Made in R1, 14 Oct 2026.*
- **D16. State passes between steps through artifacts, or through return `data`.** A step's return may carry `data`, checked against the step's `return.schema`. Later steps read it in `with` templates as `{<step>.<field>}`. Other placeholders are `{run}`, `{run.<field>}` (the run's tracker item), `{unit}` and `{unit.<field>}`. *Made in R1, 14 Oct 2026.*
- **D17. The core verdict has no delivery fields.** `unmet` is gone. A factory's own review conventions go in `details`, which fab0 records and doesn't read. *Made in R1, 14 Oct 2026.*
- **D18. Runs that open no pull request keep their ledger on a branch.** That branch (`ledger.branch`) is pushed and never merged, because the ledger must live in git (P3) and nothing may push to `main`. The alternative, ledger entries as tracker comments, would split the record. *Proposed; settle in R2e.*
- **D19. Schema 2 sits beside schema 1 until R2a.** It lives in `plugins/fab0/schemas/v2/`, so the 0.5 resolver and its tests keep working. R2a moves schema 2 into `plugins/fab0/schemas/` and deletes schema 1. *Made in R1, 14 Oct 2026.*
- **D20. D18 is made as written.** The owner chose the ledger branch in R2a. `validate` requires `ledger.branch` when no step of a pipeline writes files. *Made, 14 Oct 2026.*
- **D21. `validate` refuses what the engine won't run yet:**
  - `call`;
  - pipeline `inputs` and `outputs`;
  - `foreach` inside `foreach`.

  It also refuses three things for good, because the model needs them:
  - a step used twice in one pipeline, because its ledger names would collide;
  - `after` outside a `parallel` block, because a sequence already orders its steps;
  - a `{<step>.<field>}` template that doesn't point at an earlier agent or tool step.

  *Made in R2a, 14 Oct 2026.*
- **D22. Until they are built, the run commands refuse with exit 4 and name the step that builds them.** These are `next`, `record`, `status` (R2b), `apply` (R3) and `inbox` (R4). The 0.5 skills and agents in the plugin don't work with the engine until R4. *Made in R2a, 14 Oct 2026.*
- **D23. A unit's id names its branch and its ledger files.**
  - The id is `<step>[-<element>]`, prefixed with `<block>--` inside a gated block.
  - A gated block's id is its `id`, or else `<kind>-<position>`.
  - Branches come from `git.branches`, and ledger files are `<unit>-<attempt>.yaml`.

  *Made in R2b, 14 Oct 2026.*
- **D24. A hand-out names the worktree a unit works in.** That is the checkout that already has its branch, or else `<git-common-dir>/fab0/worktrees/<run>/<unit>`, where the session adds one. So parallel units in one repository never share a checkout, and `record` finds the unit's checkout through `git worktree list`. *Made in R2b, 14 Oct 2026.*
- **D25. A unit's inputs are read at its parent branch's head.** The ledger entry pins that commit in `base`. When the parent doesn't exist yet, the hand-out lists the chain of branches to create, oldest first, and `base` is the commit they are cut from. *Made in R2b, 14 Oct 2026.*
- **D26. Claims replace lanes.**
  - A unit claims its `paths` in each repository it writes, or the whole repository when it declares none.
  - Claims are taken in tree order, with `foreach` units in list order.
  - A ready unit overlapping an earlier unit that isn't done waits.
  - Units waiting on a gate keep their claims until merged.

  *Made in R2b, 14 Oct 2026.*
- **D27. A command step is recorded with its exit code.** A non-zero code blocks the unit (`failed`) until R2d's retry policy decides what follows. *Made in R2b, 14 Oct 2026; retry settled in R2d.*
- **D28. A unit with gate `none` merges into its parent without a pull request.** `apply` merges it, so it waits in `waiting(merge)` until then. *Proposed; settle in R3.*
- **D29. A tool artifact is read by the agent, not the engine.** The engine can't call tools. A tool input is hashed by its call (name and rendered arguments), so a change of the outside value doesn't make work stale. `foreach` lists, `elements` and `when` conditions therefore read file artifacts only. *Made in R2c, 14 Oct 2026.*
- **D30. Questions are answered through the inputs.** An attempt that returns questions waits until a person changes an input: the issue, the pull request's reviews, or a file. Its failed checks don't count against it meanwhile. *Made in R2c, 14 Oct 2026.*
- **D31. A recorded attempt stays while its inputs and outputs stand.** It is reworked when its checks failed, an input's hash changed, or an output it wrote is gone. A person's edit of an output keeps it: the edit is reviewed with the rest, and anything that reads the output goes stale. Reviews count as an input only when they ask for changes or comment. *Made in R2c, 14 Oct 2026.*
- **D32. Claims are enforced at `record`.**
  - A file the unit changed outside its claims is a finding for the next attempt.
  - A change in a repository the unit may not write refuses the record, because it can't be told apart from a person's own work there.
  - Writes outside every repository of the workspace (from #20) remain open for R3.

  *Made in R2c, 14 Oct 2026.*
- **D33. A failed command step waits for a changed input.** A command is deterministic, so running it again unchanged gives the same result. It stays `blocked(failed)` until one of its inputs changes. This settles D27. *Made in R2d, 14 Oct 2026.*
- **D34. Whoever merges decides.** A unit whose entry is on the branch it merges into is done, whatever its gate said: a person merging an escalated or rejected unit overrides the gate (P3). On the ledger branch, where nothing is merged, an auto gate's approval is the decision. *Made in R2d, 14 Oct 2026.*
- **D35. A gated block isn't retried as a whole.**
  - Its gate judges the block's units as they are; the entry records a hash of their attempts.
  - A unit that moves on asks for a new decision.
  - A reject or an escalation waits for a person, because which unit to redo can't be told from the block's verdict.

  *Made in R2d, 14 Oct 2026.*
- **D36. An agent gate runs on its own model class.** It uses the gate's model class, else the step's, else the project's first. Reviewing on a different class from the producer is the factory's choice. *Made in R2d, 14 Oct 2026.*
- **D37. Actions are applied, not recorded.** An action is done when its read-only check passes, because its result is a fact in git or the tracker (P3). So it writes no ledger entry, and doing it twice does no harm. `next` hands out actions whose check fails, and `apply` (R3) performs them. Run-level actions (`git.*`, `pr.open-run`, `pr.ready`, `pr.merge`) belong in the pipeline's `onStart` and `onEnd`, and `tracker.child.sync` in a foreach's `onStart`. *Made in R2e, 14 Oct 2026.*
- **D38. Finished work survives the run's clean-up.** A `keep: run` artifact that the run's end removed is read as it was before its removal. Without this, the removal would undo every unit that read or wrote the artifact. *Made in R2e, 14 Oct 2026.*
- **D39. A run ends with its run pull request's merge.** Its states run `units`, then `waiting` (only the merge of the run branch into the base is left; a person merges it), then `done` (the run branch is in the base of every repository that has it). Making that last merge configurable waits until a factory needs it (P8). *Made in R2e, 14 Oct 2026.*
- **D40. A run finds its pipeline by its trigger.** Without `--pipeline`, the engine picks the one listed pipeline whose trigger matches the run: the item's issue type and label, or the manual id pattern. None or several is an error that names them. *Made in R2e, 14 Oct 2026.*
- **D41. D28 is made as written.** The owner chose it in R3a: a unit with gate `none` merges into its parent directly, without a pull request. The merge commit and the ledger record it. *Made, 14 Oct 2026.*
- **D42. `apply` never moves anybody's checkout.**
  - It changes a branch through plumbing (`merge-tree`, `commit-tree`, `update-ref`), or in the branch's own checkout only when that checkout is clean.
  - A merge that conflicts changes nothing.
  - It pushes only when there is an `origin`.

  *Made in R3a, 14 Oct 2026.*
- **D43. A pull request that a person can act on exists for every unit waiting on a person or a gate.**
  - It is a draft until the unit's gate approves, and `apply` never turns it back into a draft, so a person's "ready" stands (from #17).
  - Questions and escalations are posted once, each marked by unit and attempt.
  - A run branch with nothing in it gets an empty start commit, so its pull request can open.

  *Made in R3a, 14 Oct 2026.*
- **D44. `merge: auto` waits for the pull request's required checks.** A pending check leaves the unit waiting for the merge. A failing check is reported, and what follows a failing check is decided in R3b along with conflicts. *Made in R3a, 14 Oct 2026.*
- **D45. Merge trouble goes back to the producer once.**
  - A unit ready to merge whose branch conflicts with its parent, or whose required checks fail (completing D44), is reworked once, with the files or the checks in its brief. The ledger records why each attempt was made (`rework`).
  - If the attempt made to fix it has the same trouble, a person decides.
  - `apply` brings a reworked branch up to date when it merges cleanly. Otherwise the session merges and the agent resolves the markers.
  - Claims are measured from the merge-base with the parent.

  *Made in R3b, 14 Oct 2026.*
- **D46. A unit is claimed by creating its branch.**
  - `next` creates the branch with an empty commit naming who took it, and pushes it to `origin` create-only.
  - A refused push means another machine has the unit, and it gets no hand-out.
  - Without a remote, the local branch is the claim.
  - This replaces assignment as the lock for agent work. Assignment still says whose turn a human gate is.

  *Made in R3b, 14 Oct 2026.*
- **D47. Claims hold across runs until the work is in the base.**
  - Another open run's unit branches that aren't in their repository's base claim what their latest ledger entry says.
  - An overlap warns, or blocks with `parallel.cross_run: block`.
  - Claims across different projects stay open (P8).

  *Made in R3b, 14 Oct 2026.*
- **D48. Writes outside the repositories are reported where they can be seen.** `record` lists files that appeared or changed beside the repositories in the workspace's parent directory. Writes anywhere else can't be seen. This closes the #20 backlog item. *Made in R3b, 14 Oct 2026.*
- **D49. The tracker's relations, as the engine reads them.**
  - A foreach element's item is the sub-issue that `tracker.child.sync` made for it, matched by title and type.
  - Once that item exists, its blocked-by relations replace the element's `after` (P3). A blocker inside the run is an order dependency on that element. A blocker outside the run blocks with `tracker` until it closes.
  - An `after` that names no element can't be projected, so it stays and is reported.
  - Blocked-by on the run's own item holds back every unit of the run that isn't under way.
  - The run item's sub-issues, other than its elements' items, hold back the pipeline's `onEnd`.
  - Invalid, and reported as `invalid-dependency`: a cycle; an item blocked by its own run's item; a blocker closed as not planned; a blocker inside the run whose item was closed while its work isn't merged.
  - Sub-issues of an element's item aren't read until a run needs them (P8).
  - *Made in R3c, 14 Oct 2026.*
- **D50. `after` is projected once.** `tracker.child.sync` adds blocked-by from `after` only for items it creates, both to and from the new item. It never re-adds a relation between items that already existed, so a relation a person removed stays removed. *Made in R3c, 14 Oct 2026.*
- **D51. Signals go in one board field.** With `tracker.fields.signal` set, `apply` writes into that text field, for the run's item and each element's item, either `done` or the first unfinished unit and why. It writes only when the text changes, and the engine never reads the field back. Blocked-by relations are the other half of the projection. *Made in R3c, 14 Oct 2026.*
- **D52. Core ships no agents (P0).** The delivery agents, `spec-format` and `tasks.json` left the plugin in R4. So did `scripts/check-agents.py`, which no longer ran: it was built on the 0.5 test workspace. R5 rewrites them in the `story` example from fab0-core's history before R4 (`7e29840`). *Made in R4, 14 Oct 2026.*
- **D53. A pipeline's `onStart` is done once the run has a ledger entry.** Before that, its actions are checked like any other. After it, what they did may be undone on purpose, by `onEnd` or a person, and must not be redone. The end-to-end check found this: the triage `onStart` adds a label that its `onEnd` removes, and `apply` re-added it until it gave up. A block's `onStart` is still always checked (P8). *Made in R4, 14 Oct 2026.*
- **D54. A `human: {via: label}` gate is decided by the label.** When the run's item carries the gate's label, the unit is done on a ledger branch, or `apply` merges it like gate `none` when it has a branch to merge. *Made in R4, 14 Oct 2026.*
- **D55. `inbox` finds open runs from their traces, with no registry:**
  - run branches that aren't in the base yet;
  - run folders on a ledger branch;
  - open items that match an issue trigger.
  It sorts units into what waits on the asker's roles, what anyone can run, what waits on others, and what is blocked by a signal a person may act on. Units that only wait their turn aren't listed.
  *Made in R4, 14 Oct 2026.*
- **D56. Core's skills are checked end to end, by hand.** `scripts/e2e-triage.py` runs `/fab0:run` headlessly on a copy of the `triage` fixture, against `GhFake` and stand-in MCP servers, through a person's label to the end. It costs tokens, so it runs when a skill, a hand-out or a brief changes, not in CI. *Made in R4, 14 Oct 2026.*
- **D57. An example is a directory that is also a plugin.** The directory holds:
  - `.fab0/`;
  - `agents/`, `skills/` and `hooks/`;
  - `claude-settings.json`;
  - its README;
  - `.claude-plugin/plugin.json`.

  The repository's marketplace lists each example as a plugin, so one set of files serves both ways of using it (D11). Copying puts the agents, skills and hooks under `.claude/`, and the steps name them plainly (`spec-author`). Installing the plugin needs the prefix (`story:spec-author`). The wiring is always copied. Every copied file names its source and release on its first line: a comment, a JSON `"$comment"`, or an HTML comment after a Markdown file's front matter.

  *Made in R5, 14 Oct 2026.*
- **D58. The merge guard is a `PreToolUse` hook on Bash.** It blocks commands the model issues that would:
  - merge a pull request, with `gh pr merge` or through the API;
  - push to the base branch;
  - force-push.

  It reads the base branch from `fab0.yaml`. `apply` merges through its own git calls, which don't pass through the hook, so agent merges into run branches still work. It backs up the settings' deny rules, which a compound command can slip past. *Made in R5, 14 Oct 2026.*
- **D59. Examples aren't tagged before fab0 0.6.** They need schema 2, which the 0.5 release refuses. Until R8, their CI checks against fab0-core's `main`. From R8 it checks against the release the marketplace points at, and the examples are tagged `story--v0.2.0` and `triage--v0.1.0`. *Made in R5, 14 Oct 2026.*
- **D60. The agent check is an end-to-end run.** `check-agents.py` in the examples repository runs the `story` example through `/fab0:run` on a small codebase, rather than each agent alone on a canned brief. So the agents are checked with the briefs the engine really renders, the gate that really judges them, and the merges `apply` really makes. A script stands in for the product owner's merge. *Made in R5, 14 Oct 2026.*
- **D61. A merged unit isn't sent back for its own pull request's reviews.** Its reviews were its gate, and the merge decided (D34). Its other inputs still count. *Made in R6, 14 Oct 2026.*
- **D62. A unit's reviews come from every pull request of its branch into its parent.** A person may merge a pull request at an older attempt, after which a new attempt needs a new pull request. The reviews on the merged one, such as answers to the agent's questions, still reach the new attempt. `apply` opens a new pull request when the newest one is merged or closed. *Made in R6, 14 Oct 2026.*
- **D63. The home checkout's wiring governs a run.** Called from inside a unit's worktree, the engine reads the main checkout's `.fab0/`, not the copy on the unit's branch. When the home checkout isn't on the base branch, `status`, `next` and `apply` warn, and `/fab0:run` stops to ask. In the sandbox, a checked-out pull request had silently run older wiring. *Made in R6, 14 Oct 2026.*
- **D64. A foreach closes its elements' items with `tracker.child.close`, in its `onEnd`.** Unit pull requests merge into the run branch, which closes no issue. This closes the R6 backlog item from R3c. *Made in R6, 14 Oct 2026.*
- **D65. `apply` marks an approved unit's pull request ready before it merges it,** so GitHub's record shows the gate passed (D43). *Made in R6, 14 Oct 2026.*

## Steps

Each step has an exit check. A step is done when its check has passed, not when its files exist. The final check (R8) is a real run.

- [x] **R0. Base and freeze.**
  - Home repo:
    - this guide;
    - `CLAUDE.md` in refactor mode, with P0–P11;
    - `README.md` status;
    - `ROADMAP.md` suspended;
    - `.fab0/`, `specs/` and `work/` archived;
    - the fab0 plugin disabled in `.claude/settings.json`.
  - A freeze note in fab0-core and fab0-recipes. In docs: a banner, its factory archived, the plugin disabled.
  - Close fab0-dev/fab0#17, #18 and #20, and fab0-dev/docs#3.
  - *Exit:* the four pull requests are merged, and a fresh session here no longer loads the `fab0:*` agents and skills.
  - *Result:* fab0-dev/fab0#21, fab0-dev/fab0-core#18, fab0-dev/fab0-recipes#4 and fab0-dev/docs#5 merged on 14 Oct 2026; the four issues closed with pointers to the backlog.
- [x] **R1. Model spec** (fab0-core).
  - Settle D5–D8.
  - Write the schema 2 files: project, pipeline, step, artifact, gate verdict, ledger entry, return.
  - Build three fixture factories under `tests/fixtures/`:
    - a story-like one: fan-out with `after` and `paths`, an `auto` gate with `merge: auto`, `run` branching, tracker items;
    - a docs-like one;
    - a non-delivery triage pipeline: `issue` and `none` artifacts, `when`, a `command` gate, `flat`, no pull requests.
  - *Exit:* each fixture validates against the schemas with a plain JSON Schema validator, and every operator, gate option, artifact kind and branching mode appears in at least one of them.
  - *Result:* fab0-dev/fab0-core#19. Schema 2 is in `plugins/fab0/schemas/v2/`, the fixtures in `tests/fixtures/v2/{story,docs,triage}`. `tests/test_schema_v2.py` (19 tests) validates every fixture file and inline step with `jsonschema`, checks references resolve, checks that the fixtures together use every operator (`call` is reserved and excluded), gate option, artifact kind, executor, trigger and branching mode, and checks that 11 kinds of invalid wiring are refused. Full suite: 99 passed; ruff clean.
- [x] **R2. Engine core** (fab0-core). One PR per sub-step.
  - [x] **R2a.** The module split (D6). The schema 2 loader and `validate`, which refuses schema 1.
    - *Result:* fab0-dev/fab0-core#20.
      - The engine is in `plugins/fab0/lib/fab0_engine/`, behind a `bin/fab0-resolve` shim.
      - Schema 2 replaced schema 1 in `plugins/fab0/schemas/`, and the fixtures moved to `tests/fixtures/{story,docs,triage}`.
      - `validate` passes on the three fixtures and refuses about 60 kinds of invalid wiring, each named. 95 tests pass and ruff is clean.
      - The PR carries a CI workflow patch that a person applies.
  - [x] **R2b.** The step kinds, sequence, `foreach`, `parallel` and `when`. Unit states, with every blocking reason except cross-run claims and tracker relations. Lanes, generalised from the 0.5 union-find to `paths` and `after`.
    - *Result:* fab0-dev/fab0-core#21.
      - `status`, `next` and `record` work on schema 2.
      - Units get the states `ready`, `running`, `waiting(merge|human|gate|questions)`, `blocked(order|data|claim|limit|invalid-dependency|condition|failed|start)` and `done`; gated blocks get `open`.
      - Lanes became claims taken in tree order (D26).
      - `tests/test_run.py` drives the three fixtures through real git repositories, including a gated parallel block with its own branch and a ledger-branch run. 107 tests pass and ruff is clean.
  - [x] **R2c.** The artifact kinds and their hashers, the verify ladder, staleness pinned to the parent branch's SHA.
    - *Result:* fab0-dev/fab0-core#22.
      - Every kind has a reader and a hasher.
      - `record` hashes the outputs and runs the checks: parse, schema, `sections`, `lint` and `script`.
      - Changes outside the unit's claims are findings. Changes in a repository the unit may not write refuse the record (the in-workspace half of #20).
      - Failed checks, changed inputs and removed outputs hand out a new attempt with a Rework brief. Checks that keep failing stop after `retry`.
      - `tests/test_rework.py` covers each case. 120 tests pass and ruff is clean.
  - [x] **R2d.** Gates with retry and escalation, and the core verdict.
    - *Result:* fab0-dev/fab0-core#23.
      - `next` hands out auto gates: an agent with a review brief and the verdict schema, or a command.
      - `record --gate` writes `<unit>-<attempt>-gate.yaml`.
      - What follows each decision:
        - approve: the merge;
        - reject: a rework with the findings, until `retry` runs out, then `then: human` escalates and `then: fail` fails;
        - escalate: a person decides.
      - Gated blocks are judged once on their units' attempts. On the ledger branch the approval is the decision.
      - `tests/test_gates.py` covers each case. 130 tests pass and ruff is clean.
  - [x] **R2e.** Lifecycle actions, triggers, and the generic ledger with a configurable path.
    - *Result:* fab0-dev/fab0-core#24.
      - Lifecycle actions and action steps are units, done when their read-only check passes (D37).
      - A run is `units`, then `waiting` for its run pull request's merge, then `done`.
      - Run artifacts removed at the end are read as they were (D38).
      - Triggers pick the pipeline.
      - `validate` places run-level and per-element actions.
      - The ledger path and branch were already configurable (R2b, D18).
      - `tests/test_lifecycle.py`, plus an end-to-end run in `test_run.py`. 141 tests pass and ruff is clean.
  - [x] **R2f.** Remove every delivery hard-code.
    - *Result:* nothing left to remove. The engine was rewritten in R2a–R2e without the 0.5 resolver, and the search below finds nothing in `plugins/fab0/lib`, `bin` or `schemas`. The one exception is the 0.5 `schemas/tasks.json`, which R4 removes with the agents that use it. No PR.
  - Reuse from the 0.5 script: `merge_patch`, `sha_json` and `sha_content`, the `Wiring` cross-checks, `Repo` (ledger discovery, `scope_state`), `GhCli` and `GhFake`, the lanes union-find.
  - *Exit:*
    - pytest runs on the three fixtures and `ruff` is clean;
    - a search of the engine for `plan`, `deliver`, `tasks.json`, task ids, `traces_to` and `scenario` finds no delivery logic.
  - *Result:* passed on 14 Oct 2026 with R2e: 141 tests over the `story`, `docs` and `triage` fixtures, ruff clean, and the search finds nothing.
- [x] **R3. Git workflow and tracker** (fab0-core). One PR per sub-step.
  - [x] **R3a.** `apply` with the action catalogue (`git.*`, `pr.*` including `pr.merge` and its policy check, `tracker.*`), unit merges, unit pull requests, and #17.
    - *Result:* fab0-dev/fab0-core#25.
      - `apply` performs every action whose check fails.
      - It merges units: gate `none` directly (D28), `merge: auto` after approval within `git.auto_merge` and once the required checks pass.
      - It gives units waiting on people a pull request, a draft until approved and never drafted again.
      - It posts questions and escalations once. A conflicting merge changes nothing.
      - Every action was applied twice on the fake with no change the second time. 150 tests pass (in parallel now) and ruff is clean.
  - [x] **R3b.** Conflicts and claims:
    - a merge that conflicts becomes rework for the unit, with the conflict in its brief, and escalates on a second conflict;
    - `apply` syncs a reworked unit's branch with its parent by merge;
    - pushing a unit's branch claims it, across machines;
    - claims across open runs (`parallel.cross_run`);
    - writes outside every repository of the workspace are reported (the rest of #20).
    - *Result:* fab0-dev/fab0-core#26.
      - Conflicts and failing checks rework a unit once, then escalate (D45). `apply` syncs a reworked branch when it merges cleanly.
      - `next` claims units by pushing their branch create-only (D46).
      - Claims of other open runs warn or block (D47).
      - `record` reports files written beside the repositories (D48).
      - `tests/test_conflicts.py` covers each, using a bare `origin` and a second clone. 157 tests pass and ruff is clean.
  - [x] **R3c.** The tracker's dependencies:
    - blocked-by and sub-issue relations read as dependencies, with `blocked(tracker)` and `blocked(invalid-dependency)`;
    - `tracker.child.sync` projects `after` as blocked-by;
    - blocking signals shown on the tracker.
    - *Result:* fab0-dev/fab0-core#27.
      - Blocked-by and sub-issues are read as D49 says.
      - `after` is projected once (D50).
      - The signal field is in place (D51).
      - `when` conditions on board fields are decided now.
      - `tests/test_dependencies.py` covers each. 165 tests pass and ruff is clean.
  - *Exit:*
    - every action passes on `GhFake`, twice in a row with no change the second time;
    - a simulated conflict between two units ends in rework, then escalation;
    - adding or removing a blocked-by on `GhFake` changes what `next` hands out.
  - *Result:* passed on 14 Oct 2026, on the fixtures:
    - `test_apply.py` applies every action twice;
    - `test_conflicts.py` takes a conflict through rework to escalation;
    - `test_a_blocked_by_on_the_board_changes_what_next_hands_out` adds and removes relations on the fake.
    - The real `gh` write and relation paths are first exercised in R6.
- [x] **R4. Session skills** (fab0-core).
  - `/fab0:run` executes the four step kinds, runs ready units in parallel as subagents in their own worktrees, and calls `apply`.
  - `/fab0:inbox` shows units and their blocking signals.
  - `fab0:github` keeps only what `apply` doesn't do.
  - The delivery agents and the `spec-format` skill leave the plugin.
  - *Exit:*
    - `claude plugin validate --strict` passes;
    - a headless `claude -p` runs the triage fixture end to end on `GhFake`.
  - *Result:* fab0-dev/fab0-core#28, 14 Oct 2026.
    - `/fab0:run` loops `apply`, `next`, checkouts, execution, `record` and commit. Agent hand-outs of a round run as parallel subagents in their own worktrees. Commands run in their worktree, and tools are called by the session.
    - `/fab0:inbox` renders the new `inbox` command (D55).
    - `fab0:github` now covers only setup (scopes, labels, issue types, board fields, the base branch ruleset) and the rules.
    - The delivery parts left (D52).
    - Changes to the engine:
      - `apply` pushes the ledger branch;
      - label gates are decided (D54);
      - `onStart` isn't redone once the run has records (D53);
      - pending hand-outs live in the shared git directory, so `record` works from any checkout.
    - Exit: `claude plugin validate --strict` passes for the marketplace, the plugin and its skills. `scripts/e2e-triage.py` passed all twelve checks over two headless sessions (Sonnet orchestrating, Haiku classifying), for about $0.26:
      - the agent read related issues through a tool;
      - a command gate approved;
      - `apply` labelled the item and pushed the ledger;
      - the page tool posted once and waited on the label;
      - after the label, `onEnd` removed the working label and commented.
    - The first attempt failed and showed D53. 170 tests pass and ruff is clean.
- [x] **R5. Examples repository.**
  - Rename `fab0-dev/fab0-recipes` to `fab0-dev/fab0-examples`, after asking the owner. Make it a marketplace.
  - The `story` example:
    - the three agents and `spec-format`, made to work both from a brief and by hand;
    - `tasks.json` with `after` and `paths`;
    - `.fab0/` on schema 2, with `run` branching and a reviewer gate that merges;
    - a settings snippet with the merge guard;
    - a README with the setup checklist.
  - A small non-delivery example.
  - `check-examples` in CI, and `check-agents.py` rewritten here (D52). Carry #18 over: an implementer's `questions` may be absent or empty, never `null`, and gaps go in `questions`.
  - *Exit:*
    - each example, copied into an empty repository, passes `fab0-resolve validate`;
    - `check-agents.py` passes for the `story` agents.
  - *Result:* fab0-dev/fab0-examples#5 and fab0-dev/fab0-core#29, 14 Oct 2026.
    - The repository is renamed and is a marketplace of its examples (D57).
    - `story` (`v0.2.0`):
      - schema 2 wiring with `run` branching and a reviewer gate that merges;
      - the three agents, rewritten for schema 2 briefs and for use by hand. #18 is carried over: the implementer sees the whole task list, and `questions` is never `null`;
      - `spec-format` with `scenarios`;
      - the merge guard (D58);
      - a README with the setup checklist.
    - `triage` (`v0.1.0`) delivers no code. It has a command gate that checks the classification against the project's areas.
    - `check-examples` replaces `check-recipes`, and nothing is tagged yet (D59).
    - Exit:
      - `scripts/check-examples` passes for both examples, copied into empty repositories: source lines, JSON, the merge guard against ten commands, and `fab0-resolve validate`;
      - `claude plugin validate --strict` passes for the marketplace and each plugin;
      - `check-agents.py` (D60) passed all nine checks for $0.93. The spec author wrote seven scenarios and two ordered tasks. Each task was implemented, approved by the reviewer and merged into the run branch by `apply`. The run branch's tests pass, and the run waits for a person.
    - The first attempt found only a fault in the check script itself: it hid the project's agents.
- [x] **R6. First real run, on a sandbox.** Run the `story` example on a real Story in a throwaway repository (`fab0-dev/sandbox`, created after asking the owner), with two parallel tasks and one task that depends on them.
  - *Exit:*
    - the task pull requests are reviewed and merged into the run branch by agents;
    - the dependent task starts only after its dependencies are merged;
    - a blocked-by added by hand on the board holds a task back;
    - one human-merged pull request reaches `main`.
  - Problems found go back into R2–R5 before R7.
  - *Result:* fab0-dev/fab0-core#30 and fab0-dev/fab0-examples#6, 14 Oct 2026. Every exit check passed on `fab0-dev/sandbox` (private), on real GitHub, for about $2.30 over six headless sessions:
    - The Story (#1) was specced by `spec-author`. The owner reviewed it twice through Comment reviews: once to split the work, once to answer the agent's question about where the tool gets its data. The spec (#4) was then merged into the run branch.
    - `apply` created three Task sub-issues (#5–#7), with T3 blocked by T1 and T2.
    - T1 and T2 ran in parallel. Each was implemented, approved by the `reviewer` agent, and merged into the run branch by `apply` (#9, #10).
    - T3 started only after both were merged. A blocked-by the owner added by hand (#7 blocked by #8) then held it as `blocked (tracker)` until #8 was closed. T3 was then implemented, approved and merged (#11).
    - `onEnd` brought `main` in, removed the task list and marked the run pull request ready. The owner merged #2 into `main`, which closed the Story. `status` says `done`, and `inbox` shows no open run.
  - What the run found, all fixed:
    - **Validation:** a step outside a foreach couldn't read its own pull request's reviews. The `story` example's spec step didn't list them either.
    - **Reviews and merges:** D61 and D62.
    - **The wrong wiring:** D63.
    - **Open Task items** after the run: D64.
    - **Draft pull requests merged as drafts:** D65.
  - Not changed, and logged: GitHub refuses a request for changes on one's own pull request, so with one account for people and agents only Comment reviews work. A conversation comment isn't read as feedback. See the backlog.
- [ ] **R7. Docs** (fab0-dev/docs).
  - Rewrite explanation and reference for the toolkit: building blocks, operators, gates, branching, dependencies, artifact kinds, lifecycle, the tracker.
  - Add the how-to "Build your first factory" and a page on the examples.
  - Rebuild the docs factory on schema 2 (D9).
  - *Exit:*
    - the docs checks pass in CI;
    - every reference field matches the schema 2 files.
- [ ] **R8. Release, and back to the factory.**
  - Release `fab0--v0.6.0`.
  - Copy the `story` example into this repository as fab0's factory, and enable the plugin again.
  - Restore the "Working on fab0 with fab0" flow in `CLAUDE.md`, with the new merge rule.
  - *Exit:*
    - a real Story here is delivered end to end;
    - a Docs issue in fab0-dev/docs is delivered end to end.
  - Then rewrite `ROADMAP.md` from what remains (the 0.5 roadmap's A.5, A.6 and B steps), and delete this guide.

## Backlog

Findings from 0.5 runs that still apply, and the step that takes them:

- **R3, from fab0-dev/fab0#17.** A pull request's draft state changes only when its review changes. A person who marks an unreviewed draft ready keeps it ready on a repeated run. *Done in R3a: D43.*
- **R5, from fab0-dev/fab0#18.** The `story` implementer's reply means what it says:
  - leaving `questions` out, or returning it empty, is never an error;
  - the reply schema accepts no `null`;
  - a scenario that no task delivers is a question, not a remark in the summary.
- **R2c and R3b, from fab0-dev/fab0#20.** Writes outside every listed repository are reported, not only writes in the listed ones. *Done: D32, D48.*
- **R6, from R3c.** Element items stay open after their units are done, because unit pull requests merge into the run branch and don't close them. The sandbox run decides how they close, for example with an action in the foreach's `onEnd` (P8). *Done in R6: D64.*
- **Later, from R6.** With one GitHub account for people and agents, a person can't request changes on a unit's pull request, only leave a Comment review. Comment reviews count (D62). A conversation comment doesn't, though people reach for it first. Decide whether a unit's conversation comments are feedback, or whether a bot identity for agents (a GitHub App) is the answer, when a run needs it (P8).
- **Later, from fab0-dev/docs#3.** The ledger reference is rewritten from the schema 2 ledger entry in R7, not patched.

## Baseline

The last commits before the refactor, for reading the 0.5 design and run history:

| Repository | Commit | Note |
|---|---|---|
| fab0-dev/fab0 | `931a406` | last `.fab0/`, `specs/`, `work/` and `ROADMAP.md` |
| fab0-dev/fab0-core | `c7bd1ff` | tag `fab0--v0.5.0` |
| fab0-dev/fab0-recipes | `e56da52` | tag `story--v0.1.1` |
| fab0-dev/docs | `4998843` | the 0.5 docs and the docs factory |

## Session log

Newest last. One line per session: date, step, what happened.

- 14 Oct 2026, R0. Architecture direction set; this guide written; base change and freeze PRs opened.
- 14 Oct 2026, R0 merged. R1: D5–D8 made as proposed (D12); schema 2 and three fixture factories written (fab0-dev/fab0-core#19); D13–D19 recorded, D18 open for R2e.
- 14 Oct 2026, R1 merged; D18 made (D20). R2a: engine package and schema 2 `validate` (fab0-dev/fab0-core#20); D21–D22 recorded; CI workflow patch left to a person.
- 14 Oct 2026, R2a merged with the CI workflow patch. R2b: units, states, hand-outs and records (fab0-dev/fab0-core#21); D23–D27 made, D28 open for R3.
- 14 Oct 2026, R2b merged. R2c: artifact kinds, checks, staleness and rework (fab0-dev/fab0-core#22); D29–D32 made.
- 14 Oct 2026, R2c merged. R2d: auto gates, retry and escalation (fab0-dev/fab0-core#23); D33–D36 made.
- 14 Oct 2026, R2d merged. R2e: lifecycle actions, action checks and triggers (fab0-dev/fab0-core#24); R2f needed no change; R2 complete; D37–D40 made.
- 14 Oct 2026, R2e merged. R3 split into R3a–R3c. R3a: `apply` (fab0-dev/fab0-core#25); D28 made (D41); D42–D44 made; tests run in parallel.
- 14 Oct 2026, R3a merged. R3b: conflicts, failing checks and claims (fab0-dev/fab0-core#26); D45–D48 made; the #17 and #20 backlog items are done.
- 14 Oct 2026, R3b merged. R3c: the tracker's dependencies and signals (fab0-dev/fab0-core#27); D49–D51 made; R3 is done.
- 14 Oct 2026, R3c merged. R4: session skills, `inbox`, the delivery parts out, an end-to-end check (fab0-dev/fab0-core#28); D52–D56 made.
- 14 Oct 2026, R4 merged. `fab0-recipes` renamed `fab0-examples` with the owner's approval. R5: the `story` and `triage` examples, the marketplace, the merge guard, `check-examples` and `check-agents.py` (fab0-dev/fab0-examples#5, fab0-dev/fab0-core#29); D57–D60 made.
- 14 Oct 2026, R5 merged. `fab0-dev/sandbox` created with the owner's approval. R6: the first real run passed every exit check (fab0-dev/fab0-core#30, fab0-dev/fab0-examples#6); D61–D65 made.
