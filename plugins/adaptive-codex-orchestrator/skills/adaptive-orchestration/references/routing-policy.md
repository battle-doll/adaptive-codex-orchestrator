# Routing policy

Read this reference only after the compact task-time gate has selected at least
one actual delegated task. If the detailed checks below invalidate that choice,
return the task to the parent.

## Post-selection checks

Every delegated task must be clear, bounded, independently useful, and
independently verifiable. Its expected benefit must exceed startup, context,
review, and integration overhead. Give it limited context and a firm file or
question boundary. Evidence-gathering slices may support sensitive or
ambiguous work, but workers do not own the final judgment.

## Effective task caps

Effective task worker cap = minimum of the active profile cap, any lower host
cap, the explicit user cap, and the independently useful task count. Treat an
omitted limit as absent from the calculation. A user cap of zero or an explicit
no-worker request means parent-only. Never raise an explicit user cap, even
when the selected profile or host permits more workers.

| Profile | Worker cap | Concurrent writer cap | Spawn attempts per subtask |
| --- | ---: | ---: | ---: |
| conservative | 2 | 1 | 1 |
| balanced | 4 | 1 | 1 |
| fast | 6 | 1 | 1 |

Use parallelism primarily for independent read-only tasks. At most one worker
may write at a time in every profile, including disjoint files and worktrees.
Nested delegation is forbidden without exception; all decomposition stays with
the parent.

## Task-aware caps

| Task shape | Effective cap and ownership |
| --- | --- |
| One-word, documentation typo, or clear single-file edit | 0 workers; parent executes directly |
| Local reproducible bug | Default 0; at most 1 read-only Explorer only when independent evidence materially helps |
| Four independent modules to map | Default 0 for small or obvious modules and paired tests; at most 2 read-only Explorers over disjoint module sets only when each slice requires substantial independent evidence and the expected saving clearly exceeds spawn and integration cost; fixed six-field results |
| Shared state or common-fixture conflict | At most 1 read-only Explorer; parent is the only writer |
| Authentication, permission, or tenant boundary | At most 1 read-only security Explorer; parent makes changes and performs final security validation |
| Unsupported worker completion report | 0 workers; parent checks the repository, diff, and test evidence directly |

Module count alone does not make delegation useful. Estimate the independent
evidence burden against spawn, worker startup, and parent integration cost. For
delegated mapping, partition modules without overlap. The parent verifies
cross-module boundaries and a sample of cited evidence, rather than reading all
modules again from the beginning.

## Suitable bounded work

- Locate files, symbols, entry points, tests, or configuration.
- Trace a limited call path, data flow, exception path, or stack trace.
- Reproduce or classify one focused failure.
- Implement one confirmed, low-blast-radius function or fix.
- Add focused tests for already-defined behavior.
- Perform a mechanical rename or narrow type update.
- Compare bounded documentation with code.
- Inspect independent modules or run targeted checks in parallel.

## Parent-only judgment

The parent retains architecture and product decisions; ambiguous requirements;
broad root-cause analysis; public API and major dependency decisions; database
migration, authentication, authorization, cryptographic, destructive, or
data-loss-sensitive design; complex concurrency or distributed transactions;
integration; final validation judgment; and the final answer.

## Model request and failure

- Request only the configured model and reasoning effort from
  [model-policy.json](model-policy.json).
- Record the requested model separately from any host-confirmed model. A
  request, accepted setting, role name, or successful result is not proof of
  the worker's actual model identity.
- Make one spawn attempt for each delegated subtask. If that attempt fails, is
  rate-limited, reaches a usage or host cap, or cannot honor explicit model
  selection, return the subtask to the parent.
- Do not retry the spawn and do not substitute a host-default worker.
- Never report requested worker use as confirmed without reliable host evidence.

## No-worker path

When the gate selects no worker, record one concise internal reason such as
`direct work is cheaper`, `user cap is zero`, `no independent slice`, `context
is unsuitable`, `risk stays with parent`, or `worker unavailable`. Then work
directly. Do not load the worker, model, or detailed routing references and do
not add user-facing ceremony unless the reason materially affects the result
or the user asks.

## Result review

The parent checks scope compliance, the exact result schema, evidence, file
ownership, commands, test outcomes, unsupported assumptions, and remaining
risk. Missing evidence makes a result incomplete. Conflicting results trigger
targeted parent verification, never majority voting.

After delegated exploration, the parent may spot-check cited evidence and
investigate gaps or conflicts. It must not repeat the same broad exploration
end to end, because that defeats the bounded delegation decision.
