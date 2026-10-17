---
name: spec-format
description: The format of a spec (Markdown) and its task list (YAML) in the story example, with the rules a good one follows. Use when writing, revising or reviewing a spec or a task list.
user-invocable: false
---
<!-- from fab0-dev/fab0-examples story--v0.3.0 -->

# Spec and task list

A work item's spec says **what must be true when the work is done**. Its task list says **how the work splits into pull requests**. Both are reviewed together and approved by merging one pull request, so neither has a status field.

## The spec

Use these sections, in this order. The headings are fixed: the factory checks that each is there, and reviewers find them by name. A section with nothing to say contains `None`, so an empty section can't be mistaken for a forgotten one.

```markdown
# <Title of the work item>

## Intent

Two to four sentences: who needs what, and why. No solution language.

## Scope

- In: <what this work item delivers>
- Out: <what it deliberately doesn't, even if it looks close>

## Scenarios

### S1: <short name>

- Given <state>
- When <action>
- Then <observable result>

### S2: <short name, a failure case>

- Given …
- When …
- Then …

## Constraints

Security, privacy, performance and compatibility limits the result must respect, or None.

## Decisions

- <decision>: <the choice, and a one-line reason>. Implementers don't reopen these.

## Open questions

- <question> — <answered here | deferred to <where> | asked of <role>>
```

Rules:
- **Scenarios are the contract.** Each is concrete and testable, and names an observable result. Ids are `S1`, `S2`, …, unpadded, never renumbered and never reused. Cover the failure cases.
- **Keep design out of Intent and Scenarios.** No module names, storage or signatures. What an implementer must not re-decide goes in Decisions, briefly.
- **Out of scope is explicit.** It stops scope creep in implementation and review.
- **Short.** Past about 30 scenarios the work item is too big; say so under Open questions instead of writing on.

## The task list

A YAML list. Each entry is one task: one repository, one pull request.

```yaml
- id: T1
  title: Booking API accepts an extension
  repo: backend
  files: [src/booking/extend.py, tests/booking/test_extend.py]
  scenarios: [S1, S2]
- id: T2
  title: Booking screen offers an extension
  repo: web
  files: ["src/screens/booking/**", "tests/screens/booking/**"]
  depends_on: [T1]
  scenarios: [S1]
```

| Field | Rule |
|---|---|
| `id` | `T1`, `T2`, …, unpadded, stable across revisions, never reused |
| `title` | What the task delivers, as a short sentence. It becomes the task's issue title |
| `repo` | A repository name from the project's `fab0.yaml` |
| `files` | Every file the task creates or changes, tests included. Globs such as `dir/**` are allowed. These are the task's claims: the factory refuses changes outside them |
| `depends_on` | Tasks that must be merged before this one starts (optional) |
| `scenarios` | The scenarios this task delivers (optional only for groundwork) |

Rules:
- **Every in-scope scenario is delivered by at least one task.** Before replying, list the scenario ids and find each in some task's `scenarios`.
- **One repository per task.** Work across repositories is one task per repository, ordered by `depends_on`.
- **Small.** One concern, one reviewable pull request. Split a task that needs more than about six files.
- **Vertical over horizontal.** Prefer a task that delivers a scenario end to end within its repository. Put shared groundwork (a migration, a module skeleton) in its own first task.
- **Disjoint files for parallel work.** Tasks whose files overlap can't run at the same time; the factory runs them one after another. When the order matters, say so with `depends_on`.
- **No cycles.** `depends_on` names existing tasks and forms no loop.
- **Docs travel with code.** A README or doc that a change makes wrong is in the same task's `files`.
