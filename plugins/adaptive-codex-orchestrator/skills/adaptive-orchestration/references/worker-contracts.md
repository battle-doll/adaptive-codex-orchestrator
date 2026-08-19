# Worker contracts

Read this reference only after selecting an actual delegated task. Every task
includes:

```text
Role:
Objective:
Scope:
Allowed files or areas:
Forbidden actions:
Evidence required:
Validation required:
Expected return format:
```

Send only the minimum relevant context. A worker may not expand scope, change
the selected model, permissions, or sandbox, or spawn another worker. Nested
delegation is forbidden without exception. The parent permits at most one
concurrent writer across all delegated tasks.

## Exact result schema

Every role returns exactly these six top-level fields, in this order, with the
exact lower-case names and no additional top-level fields:

```text
conclusion:
evidence:
files_and_lines:
tests_or_checks:
risks:
recommended_parent_action:
```

- `conclusion` gives the bounded result, including incomplete or blocked work.
- `evidence` gives concrete observations that support the conclusion.
- `files_and_lines` lists every relevant or changed file with precise line or
  symbol locations; use `none` only when genuinely inapplicable.
- `tests_or_checks` lists exact commands and outcomes; if none ran, say so and
  give the reason.
- `risks` states remaining uncertainty, scope gaps, and integration risk; use
  `none` only when there is no known residual risk.
- `recommended_parent_action` gives the smallest evidence-based next action.

The result must not claim a model identity unless the host confirmed it. Model
request and confirmation facts belong in field values when relevant, not in
additional top-level fields.

## Spark Explorer

Collect code evidence for one specific question. Default to read-only. Locate
files and symbols, trace a bounded execution or data path, identify tests and
configuration, and report concrete evidence and uncertainty. Do not edit, make
final architecture or root-cause decisions, or add unrelated recommendations.

## Spark Worker

Implement the smallest defensible change inside a confirmed scope. Modify only
assigned files or explicitly approved adjacent files, preserve the existing
architecture, avoid unrelated cleanup, and run targeted validation. Report
every changed file. Do not redefine requirements, add an unapproved dependency,
broadly refactor, or claim success without evidence.

## Spark Tester

Reproduce and verify specified behavior. Default to read-only unless test
creation is explicitly assigned. Capture exact commands and outcomes, identify
coverage gaps, and support any likely cause with evidence. Do not modify
production code unless explicitly assigned.

## Generic bounded worker

Use only when the host created a worker but does not expose a reliable model
identity and the central model policy permits that execution path. Follow the
assigned role and scope and make no model-specific claim. With the current
no-host-default policy, unsupported explicit model selection returns the task
to the parent instead of starting a generic substitute.
