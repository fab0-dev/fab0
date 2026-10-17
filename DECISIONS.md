# Decisions

The design decisions behind fab0, numbered and dated. The code cites them by number (`D34`). They were made during the rebuild of fab0 as a toolkit, recorded in `REFACTOR.md` until it ended with fab0 0.6, and continue here.

Append only. To reverse a decision, add a new one that names the one it replaces. Mentions of "this guide" and of steps R0 to R8 refer to `REFACTOR.md`, which git history keeps.

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
- **D66. The docs describe fab0 0.6 from R7 on.** They are rewritten for the toolkit, not patched, and say so until R8 releases it. The only status marker is **Planned**, for what `validate` accepts or refuses but the engine doesn't run. *Made in R7, 15 Oct 2026.*
- **D67. The reference is checked against the schemas, both ways, in CI.** `scripts/check-reference.py` in the docs repository uses only Python's standard library. Each property a schema defines must appear on its page, and each field a page lists in a `Field` table must exist in its schemas. Until R8, CI reads the schemas from fab0-core's `main`. *Made in R7, 15 Oct 2026.*
- **D68. `pr.merge` obeys the merge policy.** `validate` refuses it unless `git.auto_merge` has `into: [base]` and `allow_base: true`, and `apply` checks again. Before, it merged the run into the base branch with no check, unlike unit merges. *Made in R7, 15 Oct 2026.*
- **D69. A claim another machine pushed holds once fetched.** A first attempt whose branch exists, with no hand-out on this machine, is taken (D46). Before, a machine that had fetched another machine's claim handed the unit out again. *Made in R7, 15 Oct 2026.*
- **D70. Fixes that real runs find ship at once, as patch releases.** The factories run the released plugin, and the docs describe the latest release. So R8's fixes went out as 0.6.1, 0.6.2 and 0.6.3, each found by a run and each with a test. *Made in R8, 15 Oct 2026.*
- **D71. Only a person merges into the base branch, unless the policy allows it, for every kind of merge.** That includes gate `none` and label-decided units under flat branching (0.6.1), and completes D68. *Made in R8, 15 Oct 2026.*
- **D72. A person's conversation comments on a unit's pull request count as feedback, like Comment reviews.** fab0's own comments don't count, and comments stop counting once the unit is merged. This settles the R6 backlog item. It was delivered by fab0's own factory as Story fab0-dev/fab0#36, and released in 0.6.2. *Made in R8, 15 Oct 2026.*
- **D73. The decision log moves to `DECISIONS.md`, and this guide is removed when R8 ends.** The engine cites decisions by number, so they need a lasting home. Git history keeps this guide. *Made in R8, 15 Oct 2026.*
- **D74. What a run produces for itself goes into a run store, not into the product repositories.**
  - One runs repository per product (`store.github`) serves every factory of the product, each under `runs/<project>/`. `project` defaults to the home repository's name on GitHub.
  - A run's folder holds objects, immutable bytes named by their hash (`objects/sha256-<hex>.<ext>`), and facts, create-only YAML records (`ledger/<name>.yaml`). Writing a fact whose name exists answers `exists`, the store's only concurrency control.
  - Only the engine calls the store: `put`, `get`, `append`, `facts`, `runs` and `sync`.
  - The git backend commits each write in a clone the engine keeps in the home repo's git directory, or in `store.path`, under a lock for parallel writers. A push that loses a race fetches, puts its own files back on top of the remote and pushes again, at most three times. A fact another machine wrote first stands, and the writer is told.

  *Made in M1, 17 Oct 2026.*
- **D75. `record` commits the unit's work, and a unit is done when its commits are in its parent.**
  - `record` verifies the result and checks write scope, then commits what the unit changed in its checkout. It then appends the attempt to the run store with `heads`: per repository, the commit its branch is at, when the branch's content differs from its parent's at the hand-out. A refused record commits nothing, and the session no longer commits.
  - A unit is done when its latest attempt's heads are in the branch it merges into, or when GitHub reports its pull request merged at those heads, which covers a person's squash merge. Whoever merges still decides.
  - An attempt with no heads changed nothing, so nothing is merged: its gate is the decision, as on the ledger branch before.
  - This replaces the part of D24 where `record` writes the entry in the unit's checkout, and the part of D34 where done means the entry is on the parent branch.

  *Made in M2, 17 Oct 2026.*
- **D76. There is no ledger branch.** A run that writes no files records in the run store like any other, so `ledger.branch` and its `validate` rule go. This replaces D18, D20 and D55's ledger-branch trace: `inbox` finds runs in the store instead. A unit that writes no repository still works on a branch of the home repo, because it reads its parent's state there. *Made in M2, 17 Oct 2026.*
- **D77. The ledger is read from the run store, after one pull.** The latest attempts, whether a run has started (D53), other runs' claims (D47), durations and the inbox's runs all come from the store. `status`, `next`, `apply` and `inbox` pull it first. Offline, they read the local copy with a warning. `record` pushes, and `apply` pushes what a record couldn't. *Made in M2, 17 Oct 2026.*
- **D78. A command gate reads the attempt it judges at `{attempt}`,** the path of that attempt's entry in the local store. The gate's fact keeps `{attempt}`, because the path is this machine's and the ledger is everyone's. *Made in M2, 17 Oct 2026.*
