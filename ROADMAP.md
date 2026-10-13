# Roadmap

The steps that build fab0, in the order set by risk rather than completeness. Each step has an exit check, and it is done when that check has passed on a real run, not when its files exist.

This file holds the steps and their checks. Open work is tracked as Stories in this repository; the board shows where each one is. How fab0 works is in the [docs](https://github.com/fab0-dev/docs).

## A. Core in one repository

- **A.1 Resolver.** `fab0-resolve` with `validate`, `next` and `record`; the ledger; hash-based staleness; schemas for the core artifact types. *Exit:* the next-stage rule, staleness and write scope pass on fixtures of a small fake project.
  Done: fab0-dev/fab0-core#1.
- **A.2 Core agents and skills.** `spec-author`, `implementer`, `reviewer`; skills `spec-format` and `github`; the `/fab0:run` orchestrator and `/fab0:inbox`. *Exit:* `claude plugin validate` passes, and each agent returns schema-valid JSON on a fixture brief (`fab0-core/scripts/check-agents.py`).
  Done: fab0-dev/fab0-core#2.
- **A.3 The `story` recipe.** `fab0-recipes` with the `story` recipe, its README and the GitHub setup checklist. *Exit:* the recipe copied into an empty repository passes the resolver's validation.
  Done.
- **A.4 First run on fab0 itself.** The `story` recipe copied into this repository, and a Story about fab0 run interactively. *Exit:* the spec pull request, plan, one task pull request and the delivery pull request are all merged, with no manual stage selection.
  Passed on 12 October 2026 with Story #5. Its findings became Stories #9 and #10, both delivered.
- **A.5 First project other than fab0.** One real Story end to end, interactively, in a project that isn't fab0. *Exit:* the Story is delivered, and every problem found is filed as a generic issue in the fab0 repository that owns the concern.
- **A.6 Headless run.** `claude -p` under `dontAsk` with a budget. *Exit:* the cost of each stage is read from Claude Code's OpenTelemetry metrics and recorded.

## B. Team and repositories

- **B.1 Handoff in one repository.** The product owner's spec pull request is merged; the developer's `/fab0:inbox` suggests the pending `plan`; `/fab0:run` runs it; the developer's task pull request closes the task. *Exit:* no message outside GitHub was needed.
- **B.2 Two repositories.** One spec in the home repo, tasks in two code repositories, in parallel. *Exit:* both task pull requests merged from the same spec.
- **B.3 Three people across three repositories.** It includes a task blocked by another and a spec change after implementation started. *Exit:* the stale tasks are listed and reconciled by `plan`.
- **B.4 Nesting.** Two repositories each run their own `delivery` pipeline; one breaks down in parallel and implements only after the other's contract is merged. *Exit:* the join fires only after both children are done.

## C. Extensions

- **C.1 Documentation factory.** It comes earlier than first planned, because the docs need it now. The `fab0-dev/docs` repository, with its own `.fab0/` running a `docs` pipeline for issues of type Docs:
  - stages: brief, plan, write, deliver;
  - agents: `docs-planner`, `docs-writer`, `docs-reviewer`;
  - skills: Anthropic's `doc-coauthoring` and a project `docs-style` skill.

  Steps:
  - **C.1a Seed.** The first docs, written by hand. *Exit:* the docs checks pass in CI and every reference field matches the fab0-core schemas.
  - **C.1b Factory.** The pipeline, agents and skill in `fab0-dev/docs`. *Exit:* `fab0-resolve validate` passes there; each agent returns schema-valid JSON on a fixture brief.
  - **C.1c First docs run.** An audit of the reference against fab0-core. *Exit:* the brief pull request, plan, at least one write pull request (passed by the reviewer gate) and the delivery pull request are merged, and every finding that needs a code change is filed as a Story here.
- **C.2 Domain modelling plugin** (`fab0-ddd`) and its recipe, copied into a project that already runs `story`. It creates `fab0-plugins`. *Exit:* the plugin's checks are schemas and an auditor agent, and any script left over is measured.
- **C.3 Discovery plugin** (`fab0-discovery`) with the `exploration` and `feature` pipelines. *Exit:* a Feature's `plan` creates Story sub-issues that run on their own.
- **C.4 Design and BDD plugins** (`fab0-design`, `fab0-bdd`), each only when a project needs it.
