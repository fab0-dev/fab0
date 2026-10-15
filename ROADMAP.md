# Roadmap

The steps that build fab0 from here, in the order set by risk rather than completeness. Each step has an exit check, and it is done when that check has passed on a real run, not when its files exist.

This file holds the steps and their checks. The work itself runs through fab0's own factory: each step becomes one or more Stories in this repository, and the board shows where each one is. Why fab0 is built the way it is lives in [DECISIONS.md](DECISIONS.md); how it works, in the [docs](https://github.com/fab0-dev/docs/blob/main/docs/index.md).

## Where fab0 is

fab0 0.6 is a toolkit for building and operating software factories. It was rebuilt from the 0.5 delivery factory in steps R0 to R8, recorded in `REFACTOR.md`, which git history keeps (it was removed with fab0-dev/fab0#43's merge). The 0.5 roadmap, with steps A.1 to C.4, is at commit `931a406`.

Done since 0.5:
- the engine on schema 2: pipelines, operators, gates, artifacts, the ledger, `apply`, `inbox`;
- run branches with parallel sub-branches, claims, and the tracker's dependencies;
- `/fab0:run` and `/fab0:inbox`, checked end to end headlessly;
- the `story` and `triage` examples, and the docs rewritten for the toolkit;
- fab0's own factory and the docs factory, each with a real run delivered end to end (R8).

## A. Use beyond fab0

- **A.1 First project other than fab0.** The `story` example copied into a project that isn't fab0, and one real Story run there. *Exit:* the Story is delivered, and every problem found is filed as a generic issue in the fab0 repository that owns the concern.
- **A.2 Headless runs with a budget.** `/fab0:run` under `claude -p` with `dontAsk` and a budget, started by a trigger rather than a person. *Exit:* the cost of each unit is read from Claude Code's OpenTelemetry metrics and recorded with its ledger entry.
- **A.3 Updates take effect.** After a plugin update, a new session can still run an older engine: Claude Code keeps an orphaned version's `bin/` on the `PATH` ahead of the new one (seen in R8). *Exit:* `/fab0:run` detects an engine older than the installed plugin and says how to fix it.
  Done: Story #44, released in 0.6.4 (fab0-dev/fab0-core#40, fab0-dev/docs#21). The check protects updates from 0.6.4 on; an orphaned engine older than 0.6.4 has no check and still has to be removed by hand once.

- **A.4 Escalations carry their findings.** After a person answers an escalated unit, the next attempt's brief has the person's feedback but not the gate's findings, which live only in fab0's own escalation comment (seen in R8). *Exit:* a reworked attempt after an escalation sees the gate's last findings in its brief.

## B. Teams

- **B.1 Handoff between two people.** A product owner and a developer on different machines. The developer's `/fab0:inbox` shows the run's ready work once the spec is merged, `/fab0:run` claims it, and escalations reach the right person. *Exit:* no message outside GitHub was needed.
- **B.2 A spec that changes mid-run.** A spec revised after some tasks are merged. *Exit:* the affected tasks go stale and are reworked, and the rest stand.
- **B.3 An identity for agents.** A GitHub App for the agents' writes, so GitHub tells people from agents, and rulesets can restrict merges into `main` to people. *Exit:* a ruleset on `main` refuses a merge by the agents' identity, and a real run still completes.

## C. Composition

- **C.1 Nested pipelines.** `call` runs another pipeline as a child run, for example one repository's delivery inside another's. *Exit:* two repositories each run their own pipeline from one parent run, and the parent's join waits for both children.
- **C.2 More examples, each when a project needs it:** domain modelling, discovery (a Feature that breaks down into Stories), design and behaviour-driven development. *Exit, for each:* the example copied into an empty repository validates, and its agents pass an end-to-end run.
