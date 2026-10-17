# Migration: the run store (fab0 0.6 → 0.7)

**Status:** M6 and M7 in review. Next step: **M8**.

This guide governs the work on fab0 until 0.7 is released and has passed a real run. Sessions read it, do one step and edit it in the same pull request. It takes precedence over `ROADMAP.md` until step M9 is done, and it is removed then, as `REFACTOR.md` was. Git history keeps it.

## How to use this guide

1. Read this file top to bottom before you change anything. `CLAUDE.md` still applies, except where its "Migration mode" section says otherwise.
2. Take the first step in [Steps](#steps) whose box isn't ticked.
3. Do the step by hand in an ordinary session. Nobody uses `/fab0:run` until M9. The plugin stays at the released 0.6.5 until M8.
4. One step is one pull request in the repository it changes. A step too large for one PR is first split here into lettered sub-steps (M2a, M2b, …).
5. In the same pull request:
   - tick the step;
   - write its exit check result under it: what was run and what it showed;
   - append the decisions it made to `DECISIONS.md` ("Made in Mn"), naming any decision they replace.

   When the step's PR is in another repository, open a small companion PR here with those edits, or include them in the next home-repo PR.
6. If the work shows the target model is wrong, change [Target model](#target-model) in its own PR and say why.

People merge every pull request during the migration.

## Why

fab0 0.6 keeps everything a run produces for itself on the branches of the product repos. Runs 36 to 55 show what that costs:

- **Files.** 93 ledger files sit on the base branches of the four repos, and nothing ever removes them: `keep: run` covers only the task list. In `docs`, 43 of its 90 tracked files are ledger files.
- **Pull requests.** Every run PR in this repo carried no product change: each one landed only `specs/<run>.md` and a ledger entry. A Story took about 8 PRs (run 55). Docs run 8 opened three empty run PRs in repos it never changed.
- **Commits.** Each gate decision is a commit of its own. Each unit starts with an empty claim commit, and a run with an empty `start run` commit. The run ends with a commit that only removes the task list. A rework that changes no code is a commit with only a ledger file. Bringing the base into a run branch also brings in other runs' ledgers.
- **Reading.** The engine reads run state from git branches in every repo: a unit is done when its ledger file is in its parent branch's tree, cross-run claims come from other runs' unit branches, and the inbox lists folders on a ledger branch.

The fix: **a product repo receives only product changes.** What a run produces for itself goes into one runs repository per product, through a store interface that only the engine calls.

## Target model

### Where content lives

| Content | Home | Gets there by |
|---|---|---|
| Code, tests, docs, and any artifact a factory declares `kind: file` | a product repo | the unit's pull request |
| Artifacts a factory declares `kind: store` | the run store, as objects | `record` |
| Attempts, gate decisions, claims: the ledger | the run store, as facts | `record`, `next` |
| Intent, approvals, hierarchy, done | the tracker and GitHub | people, actions |
| Brief, inbox, an artifact's latest version | computed | the engine |

An artifact type picks its home, and the engine predefines nothing. A factory that wants a per-run spec reviewed and then compacted into durable specs declares the spec `kind: store` and adds a step that writes the durable file. One that wants the spec in a repo keeps `kind: file`.

### The store

- **Configuration.** `fab0.yaml` gets `store: {github: <owner>/<repo>, project: <key>, path: <local repo>}`, which replaces `ledger: {path, branch}`. `project` defaults to the home repository's name on GitHub (`fab0-dev/docs` → `docs`), so several factories of one product share a runs repository without their run numbers colliding. `path` is optional, for tests and for people who want to browse. By default the engine keeps its own clone in `<home git dir>/fab0/store`.
- **Layout** of the runs repository:

  ```text
  runs/<project>/<run>/
    ledger/<unit>-<n>.yaml          an attempt
    ledger/<unit>-<n>-gate.yaml     a gate decision
    ledger/<unit>-<n>-claim.yaml    a claim
    objects/sha256-<hex>.<ext>      a store artifact
    review/<unit>/<artifact>.<ext>  arrives only through a review pull request
  ```

- **Objects** are immutable and addressed by their hash. Writing the same content twice is a no-op, and a read fails if the content doesn't match its hash.
- **Facts** are create-only. Writing a fact whose name exists answers `exists`. That is the store's only concurrency control.
- **Interface** (`store.py`): `put`, `get`, `append` (`ok` or `exists`), `facts(run)`, `runs()`, `sync(pull)`, `sync(push)`, and `review(run, unit, files)`. Only the engine calls it. Agents read what the brief gives them and write to their outbox.
- **The git backend.**
  - There is one pull before `next`, and one push after each `record` or claim.
  - A push rejected as non-fast-forward fetches, puts the local writes back on top of the remote and pushes again, at most three times. Nothing in the store changes or goes, so this replay conflicts only on a fact another machine wrote first: the remote's fact stands, and the writer is told.
  - A file lock serialises parallel records on one machine.
  - The runs repository's ruleset blocks force pushes and the deletion of `main`, so history stays append-only. It has no required-PR rule and no CI.
  - People push with their own credentials, so a commit's author is the actor.
  - No LFS until a run needs it. Other backends are reserved, not built (P8).

### A unit's life

1. **`next`** pulls the store and appends a claim fact for each unit it hands out, pushed before the hand-out. A claim refused with `exists` means another machine has the unit. Without a remote, the local fact is the claim. The unit branch is created from the parent head, with no commit.
2. **The brief** names the unit's worktree and its outbox, `<home git dir>/fab0/out/<run>/<unit>-<n>/`. The agent writes product files in the worktree and store artifacts in the outbox.
3. **`record`**, in order:
   1. validates the return and the outbox files, and runs the verifiers;
   2. checks write scope;
   3. commits the product changes in each written worktree;
   4. `put`s the objects, `append`s the attempt fact with `heads` (the commit in each repo), and pushes.

   A refused record commits nothing. The session no longer commits.
4. **Gates.** An agent gate or command gate is recorded as a gate fact, with no commit. A command gate receives the attempt fact as a file, `{attempt}`.
5. **Done.**
   - A unit with product changes is done when its latest attempt's heads are reachable from its parent branch, or when GitHub reports its pull request merged. The second case covers a person's squash merge.
   - A unit without product changes is done when its gate passes: `none`, an `auto` approval, a label (D54), or a review pull request merged by an owner.

### Review pull requests

A unit with a `human` gate whose outputs are all in the store gets its pull request in the runs repository:

- It is on branch `fab0/<project>/<run>/<unit>`, one per unit, not one per attempt. The branch adds readable copies of the outputs under `review/<unit>/`.
- Each attempt adds a commit, so the pull request shows what changed since the last review.
- Reviews and a person's conversation comments feed the next attempt, as for any unit (D62, D72).
- The merge is the approval only if the person who merged holds the gate's owner role. Branch protection can't limit who merges one path, so the engine checks this. Otherwise it reports the merge and the gate doesn't pass.
- Files a person changed on the branch before merging are recorded as an attempt by that person. A product owner can still edit a spec in its pull request.

### Run pull requests

- `git.run-branch` creates run branches with no commit.
- `pr.open-run` opens a repository's run pull request only once its run branch is ahead of the base.
- Each run pull request closes the run's item (`Closes <home>#<run>`). A run that changes nothing in the home repo has no run pull request there.

### What goes

- `keep`, `git.remove-run-artifacts`, and reading a removed artifact from history (D38).
- `ledger.path`, `ledger.branch`, the ledger branch, and `publish_ledger`.
- The ledger exclusion in gate briefs, and the ledger exemption in the write-scope check.
- Empty claim and start commits, and run pull requests in repositories with no change.

### Decisions already taken

They are recorded in `DECISIONS.md` by the step that implements them.

- fab0's own factory keeps the spec and the task list in the store. Spec compaction comes later, as a roadmap item.
- One runs repository for fab0, `fab0-dev/fab0-runs`, shared by the home and docs factories through `store.project`.
- Ledger files from past runs are deleted at cutover, not imported. Git history keeps them.
- 0.7 also removes empty commits and empty pull requests.
- A person's conversation comments keep counting as feedback (D72).
- Questions stay in the attempt fact. No separate message facts until a run needs them (P8).
- The word "ledger" stays, for the facts of a run in the store.

## Steps

- [x] **M0. This guide (fab0).** Add `MIGRATION.md`, the "Migration mode" section in `CLAUDE.md` and a pointer in `ROADMAP.md`.
  *Exit:* the pull request is merged.
  *Result:* fab0-dev/fab0#75, merged on 17 Oct 2026.

- [x] **M1. The store adapter (fab0-core).** Pull `main` first; the local checkout was behind.
  - New `plugins/fab0/lib/fab0_engine/store.py`: the interface, and `GitStore` with the managed clone, the lock, create-only `append`, and a push that replays onto the remote and retries.
  - `schemas/project.json` accepts the `store` block, still beside `ledger`. The schema alone checks it, so `wiring.py` needed no change. Nothing calls the store yet.
  - New `tests/test_store.py`, on a bare origin with two clones.

  *Exit:* the tests show that:
  - `put` twice keeps one object;
  - a hash mismatch fails `get`;
  - two clones appending the same fact get `ok` and `exists`;
  - a concurrent push replays and succeeds.

  *Result:* fab0-dev/fab0-core#58. `uv run pytest -q` passes: 372 passed and 1 xfailed (the xfail was already there). Ruff and the fixtures' `validate` pass too. `tests/test_store.py` covers each point of the exit check. It also shows that the loser of a fact race still pushes its other writes, that 8 threads writing into one clone lose nothing, that an empty remote takes the first push, and that two projects share one runs repository. Decision D74.

- [x] **M2. The ledger in the store (fab0-core).**
  - Writes:
    - `handout.record` and `gates.record_gate` append facts.
    - `record` commits the product changes and records `heads`.
    - `ledger-entry.json` gets `heads`, and keeps no absolute local paths.
  - Reads: the store replaces the branch reads in `schedule.py` (`sources`, `load_latest`, `recorded`, `other_claims`, `on_branch` and `status`) and in `inbox.candidates`. The inbox's traces become runs in the store, run branches, and items that match a trigger.
  - Removed:
    - `ledger` from `project.json`; `validate` refuses it, saying to use `store`;
    - the ledger branch and its `validate` rule;
    - `publish_ledger` and `ledger_repo`;
    - the gate-brief exclusion and the write-scope exemption.
  - Command gates get `{attempt}`.
  - `skills/run/SKILL.md` drops its commit step.
  - The test fixtures move off `work/`. The triage fixture loses its ledger branch.

  *Exit:*
  - the suite and `scripts/e2e-triage.py` pass;
  - in a fixture story run, `git log --name-only` over every product branch shows no ledger file;
  - triage runs with no ledger branch;
  - a squash-merged unit counts as done.

  *Result so far:* fab0-dev/fab0-core#59.
  - `uv run pytest -q` passes: 375 passed and 1 xfailed (the xfail was already there). Ruff and the fixtures' `validate` pass too.
  - Three tests cover the exit check: `test_the_ledger_stays_out_of_the_product_repositories` (no ledger file on any branch, and no gate commit), `test_a_run_without_files_records_into_the_run_store` and `test_a_squash_merged_unit_is_done`.
  - `scripts/e2e-triage.py` passed in M5, after a fix to the script itself (see M5), so the box is ticked.

  Found while doing it, now part of the step:
  - A unit that writes no repository, such as a command check, still works on a branch of the home repo, because it must read its parent's state. It just records no `heads`. M4 decides whether a detached checkout can replace that branch.
  - `heads` counts a branch only when its content differs from the parent's at the hand-out, because every unit branch carries the empty claim commit until M4.
  - A squash merge counts only when GitHub reports the pull request merged at the recorded head. A pull request merged at an older attempt doesn't make the newer one done.
  - A command gate's fact keeps `{attempt}`, not the local path it ran with.

  Decisions D75 to D78.

- **M3. Store artifacts and review pull requests (fab0-core),** split in two.

- [x] **M3a. Store artifacts.**
  - `artifact.json` gets `kind: store` with a `format`.
  - `keep` goes, and so does `git.remove-run-artifacts` (`catalogue.py`, `actions.py`, `apply.py`). `validate` refuses both, with a hint.
  - The brief names the outbox. `record` verifies the outbox files against their schema and verifiers, and `put`s them. Any other file in the outbox is a finding.
  - An artifact's latest version is the output of the most recent attempt that produced it and passed verification. Briefs inline it, and `foreach` reads its elements from it.

  *Exit:* `foreach` fans out from a task-list object, the task list reaches no product repository, and a missing or extra outbox file is a finding.

  *Result:* fab0-dev/fab0-core#60.
  - `uv run pytest -q` passes: 381 passed and 1 xfailed. Ruff and the fixtures' `validate` pass too.
  - `test_a_store_artifact_is_an_object_in_the_run_store_and_never_in_a_repository` covers the object, the fan-out and the home repo's history (spec, no task list).
  - `test_the_outbox_holds_only_the_steps_outputs`, `test_a_version_that_failed_its_checks_is_never_the_latest` and `test_keep_and_the_removal_action_are_refused_with_a_hint` cover the rest.
  - The fixtures' task lists are store artifacts. Their specs stay `kind: file` until M3b gives a store-only human gate a review surface.
  - Found while doing it: a store artifact has one latest version per run, not one per branch. A new version is seen at once by every unit that reads it, wherever it works. Decision D79.

- [x] **M3b. Review pull requests.**
  - Review pull requests, as in the target model, including the owner check and a person's edits. A `pr` artifact of the unit resolves to its review pull request.

  *Exit:* in a fixture story run with the spec and the task list in the store:
  - a review pull request opens in the runs fixture;
  - a Comment review brings a new attempt with the review in its brief;
  - a merge by a non-owner is reported, and a merge by the owner passes the gate;
  - a person's edit on the branch is recorded as an attempt;
  - the product repos receive only the implementation's changes.

  *Result:* fab0-dev/fab0-core#61.
  - `uv run pytest -q` passes: 386 passed and 1 xfailed. Ruff and the fixtures' `validate` pass too.
  - `tests/test_review.py` covers the exit check. Its tests switch the story fixture's spec to `kind: store`, give the store `github`, and give the spec step `reviews` as an input:
    - `test_a_store_only_unit_is_reviewed_in_a_pull_request_of_the_runs_repository` covers the first, second, fourth and fifth points. The review pull request opens in the runs fixture. A Comment review brings attempt 2, with the review in its brief. A person's commit is recorded once, as attempt 3 by that person, and the next step reads that version. `git log --all --name-only` shows nothing of the run in the home repository, and only the implementation's file in the other one.
    - `test_only_the_gates_owner_approves_by_merging` covers the third point.
    - `test_a_merge_of_an_older_attempt_doesnt_pass_the_newer_one` covers a merge at an older attempt.
  - Two mutations each fail a test: an owner check that always passes, and edits that are never seen.
  - The fixtures keep their spec `kind: file`; the examples switch in M6. `scripts/e2e-triage.py` was not run.
  - Found while doing it, now part of the step:
    - Only a step that writes no repository is reviewed in the runs repository. A human-gated step that writes one keeps its product pull request.
    - A merge by someone outside the owner role would otherwise leave the run stuck. An owner's approving review on that pull request now passes the gate.
    - A rework brief shows a store output's latest version, since it is on no branch to build on.

  Decision D80.

- [x] **M4. No empty commits or pull requests (fab0-core).**
  - Claims: a claim is a create-only claim fact, pushed before the hand-out. The unit branch is created from the parent head, and pushed by the first `record` or by `apply`. With no claim commit, `heads` can go back to "the branch has commits its parent lacks" (M2).
  - A unit that writes no repository: decide whether it reads its parent from a detached checkout instead of a branch (M2).
  - `git.run-branch` makes no commit. `pr.open-run` waits until the run branch is ahead of the base. Every run pull request closes the run's item.

  *Exit:*
  - in a fixture run that reads one repository without writing it, no product repository has an empty commit, and the read-only one gets no pull request;
  - two clones racing for one unit give one hand-out.

  *Result:* fab0-dev/fab0-core#62.
  - `uv run pytest -q` passes: 389 passed and 1 xfailed. Ruff, `claude plugin validate --strict plugins/fab0` and the fixtures' `validate` pass too.
  - `tests/test_empty.py` covers the exit check:
    - `test_a_run_that_only_reads_a_repository_leaves_no_trace_in_it`: the story fixture, with its spec and task list in the store and its one task in the backend, runs to its end through `apply`. No product repository has a commit that changes nothing, home's run branch stays at `main`, and home gets no pull request. The backend's run pull request closes the run's item.
    - `test_two_clones_racing_for_one_unit_give_one_hand_out`: two machines run `next` at once, and one hand-out results (5 runs out of 5). `test_a_claim_pushed_first_elsewhere_wins_over_one_written_here` covers the narrow race, where a clone that hasn't seen the other's claim loses at the push.
  - Two mutations each fail a test: a claim that always wins, and run pull requests opened without work.
  - Decided: a unit that writes no repository keeps a local branch with no commit. A detached checkout would change the session's checkout steps for nothing this step needs.
  - Found while doing it, now part of the step:
    - Every attempt is claimed, reworks included.
    - `pr.open-run` is checked again by `apply` after its last round, since a run branch gets work only after the run starts. Only `apply` reads for it, so `status`, `next` and `inbox` read no more than before.
    - A unit whose attempt changed nothing has no pull request now, so its questions or escalation go on the run's item.

  Decisions D81 and D82.

- [x] **M5. Skills and setup (fab0-core).**
  - `/fab0:run` and `/fab0:inbox` follow the store.
  - The `fab0:github` skill checks the runs repository and creates it on request: private, the ruleset, write access for the project's people.
  - `validate` checks that the store is reachable.

  *Exit:* `validate` passes on every fixture, and `scripts/e2e-triage.py` passes.

  *Result:* fab0-dev/fab0-core#63.
  - `validate` passes on the three fixtures. `uv run pytest -q` passes: 392 passed and 1 xfailed. Ruff and `claude plugin validate --strict plugins/fab0` pass too.
  - `scripts/e2e-triage.py` passes all 15 checks, for $0.20 over two sessions. It now also checks that `classify` was claimed in the run store, and that the product repository has no commit that changes nothing.
  - `validate` reaches the store with `git ls-remote`, through its clone's remote or else `store.github`, and an unreachable store is invalid wiring. New tests cover a reachable and an unreachable store, one with no checkout yet, and a folder that isn't a repository. The tests send `https://github.com/` to a local folder, so none reaches GitHub.
  - Found while doing it, now part of the step:
    - The e2e script had never run since M2. An installed fab0 plugin's `bin` came before `--plugin-dir`'s on the session's PATH, so the session ran the released 0.6.5 engine. The script now puts the engine under test first.
    - `/fab0:inbox` listed units another machine claimed as ready to run. They now wait on that machine.
  - Left open: the inbox evaluates every run the store holds, finished ones included. No cheap signal tells a finished run from an open one, since a triage run's onStart removes its trigger label, and nobody runs `apply` after a person merges a run's pull requests. It stays until a run needs it (P8).

  Decision D83.

- [x] **M6. The examples (fab0-examples).**
  - `story`:
    - the spec and the task list become `kind: store`;
    - `onEnd: [git.sync-base, pr.ready]`;
    - the `store` block replaces `ledger`;
    - the agents write where the brief says;
    - the README's setup adds the runs repository and its ruleset, and shows how to keep the spec in a repo with `kind: file`.
  - `triage`: no ledger branch, and `.fab0/checks/classification.py` reads `{attempt}`.
  - CI checks against fab0-core's `main` until M8, as it did before 0.6.

  *Exit:* each example copied into an empty repository validates, and `scripts/check-agents.py` passes end to end.

  *Result:* fab0-dev/fab0-examples#11. The examples are `story` 0.3.0 and `triage` 0.2.0, to be tagged in M8.
  - `scripts/check-examples` copies each example into an empty repository and validates it: `PASS story`, `PASS triage`. It stands up the runs repository the wiring names in a local folder, since `validate` checks it can be reached.
  - `scripts/check-agents.py` passes end to end: 13 checks out of 13, $0.82 over two sessions. The spec is reviewed in the runs repository and merged by its owner, and both tasks are reviewed and merged. The run branch's tests pass. The run's commits touch only code and tests, with no empty commit, and the ledger and the approved spec are in the runs repository.
  - Found while doing it, now part of the step:
    - The check's codebase had no `.gitignore`, so the `__pycache__` its tests leave counted as writes outside a task's claims, and `record` would have committed it. It now ignores them, as a project does.
    - Its "only code and tests" check compared against the start's files, so it passed with an empty list. It now checks every file the run's commits touched. That version was checked against the kept run, not in a new run.
    - `spec-author` starts a rework from the version the brief shows when its files aren't in place, and keeps a person's edits.
    - The story README says how to keep the spec in a repository with `kind: file`. The task list then isn't in the spec's pull request.

- [x] **M7. The docs (docs).**
  - Reference:
    - `project.md`: the `store` block;
    - `artifact.md`: `kind: store`, no `keep`;
    - `ledger.md`: where facts live, `heads`, claim facts;
    - `actions.md`.
  - Explanation:
    - `artifacts-and-ledger.md`;
    - `branching.md`: no "Runs that write no files"; claims;
    - `execution.md`: the loop and the inbox;
    - `dependencies.md`;
    - `gates.md`: review pull requests;
    - `pipelines.md`;
    - the glossary in `overview.md`: run store, runs repository.
  - How-to:
    - `use-an-example.md`;
    - `github-setup.md`: a section on the runs repository;
    - `choose-git-workflow.md`: no ledger branch;
    - `build-your-first-factory.md`.
  - `index.md` says the docs describe 0.7 ahead of its release. CI reads the schemas from fab0-core's `main` until M8.

  *Exit:* `scripts/check-reference.py`, the linters and the link check pass.

  *Result:* fab0-dev/docs#28.
  - Against fab0-core `main`, `scripts/check-reference.py` finds that every field of the 6 reference pages matches its schema. It found 6 problems before the change. It now also checks `ledger.md` against `claim.json`.
  - `uvx pymarkdownlnt scan` and `uvx codespell` are clean.
  - Links: lychee isn't installed locally, so a script checked every relative link and fragment, and all resolve. CI's offline lychee run is the check of record. The weekly full check will fail on one link into the story README until fab0-dev/fab0-examples#11 is merged.
  - Every page the step lists is updated, plus `step.md`, `commands.md`, `tracker.md` and `examples.md`, where they were stale.
  - `CONTRIBUTING.md` still describes the docs repository's own factory on 0.6. That factory moves in M8.

- [ ] **M8. Release and cutover (every repository).**
  - fab0-core: release 0.7.0 (`plugin.json`, the marketplace entry, the tag `fab0--v0.7.0`). Tag the examples `story--v0.3.0` and `triage--v0.2.0`. Docs and examples CI go back to the release the marketplace points at.
  - Create `fab0-dev/fab0-runs` with the `fab0:github` skill.
  - fab0:
    - copy `.fab0/` again from `story--v0.3.0`, with `store: {github: fab0-dev/fab0-runs, project: fab0}`;
    - remove `work/` and `specs/`;
    - update "What this repo holds" in `README.md` and `CLAUDE.md`.
  - docs:
    - its factory gets `store: {github: fab0-dev/fab0-runs, project: docs}`;
    - the brief and the task list become `kind: store`;
    - remove `work/` and `briefs/`;
    - update `CONTRIBUTING.md` and the `docs-style` skill.
  - fab0-core and fab0-examples: remove `work/`.
  - Update the plugin in the fab0 and docs checkouts.

  *Exit:*
  - `fab0-resolve --version` shows 0.7.0 in a fresh session;
  - `validate` passes in both factories;
  - no `work/`, `specs/` or `briefs/` is left on any base branch;
  - `/fab0:inbox` runs clean.

- [ ] **M9. The first real run on 0.7 (fab0, and docs if a Docs issue is ready).**
  - A real Story runs with `/fab0:run` in a person's session.

  *Exit:*
  - over the run's pull requests, `git log --name-only` shows product files only;
  - no product repository has an empty commit;
  - no pull request lacks a product change;
  - the spec's review pull request and the run's facts are in `fab0-runs` under `runs/fab0/<run>/`;
  - `/fab0:inbox` finds the run from the store.

  Record two numbers: process files in product repos (target 0), and pull requests per Story (run 55 took 8). Then:
  - remove this guide and the "Migration mode" section;
  - update `ROADMAP.md`, adding spec compaction as an item.

  Fixes that runs find ship as 0.7.x patch releases (D70).

## Decisions the steps record

| Step | Decision | Replaces |
|---|---|---|
| M1 | The run store: one runs repository per product, its layout, immutable objects and create-only facts | — |
| M2 | `record` commits; a unit is done when its heads are reached or GitHub reports it merged | D24, D34 in part |
| M2 | No ledger branch: runs that write no files record in the store | D18, D20, D55's ledger-branch trace |
| M2 | Claims across runs are read from the store | D47 in part |
| M2 | Command gates receive the attempt fact | — |
| M3a | `kind: store`; no `keep` and no `git.remove-run-artifacts` | D38 |
| M3b | Review pull requests in the runs repository, the owner check, a person's edits | — |
| M4 | A claim is a store fact; unit branches start without a commit | D46, D69 |
| M4 | Run pull requests open only where the run changes something | D43's empty start commit |
