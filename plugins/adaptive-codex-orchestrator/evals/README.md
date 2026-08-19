# Offline policy evals

`prompts.jsonl` is a deterministic routing-policy fixture set. It does not call
an LLM, spawn a worker, score generated prose, or make a network request. Each
line records a scenario and the acceptable orchestration envelope that the
parent policy should preserve.

`reviewer-cases.json` is the public-review companion: exactly five positive
and three negative cases with reproducible setup, expected behavior, expected
result shape, and a safety rationale for every negative case. It is formatted
for manual entry in the OpenAI plugin submission portal and does not replace
the broader 31-scenario offline policy set.

Run the checker from the plugin root:

```text
python scripts/evaluate_policies.py
```

An alternate JSONL file can be checked explicitly:

```text
python scripts/evaluate_policies.py path/to/prompts.jsonl
```

## Record schema

Every line is one JSON object with exactly these fields:

- `id`: stable lower-case hyphenated scenario identifier.
- `prompt_or_scenario`: prompt text or a concrete host/worker situation.
- `expected_delegation_decision`: `parent-only`, `delegate`, `conditional`, or
  `disabled`.
- `expected_worker_count_range`: `{ "min": integer, "max": integer }`, bounded
  by the profile ceiling and any lower host, user, useful-task, or task-specific
  safety cap. Profile ceilings reach six, but canonical task-specific caps are
  zero, one, or two where applicable.
- `expected_worker_role`: an array containing any of `Spark Explorer`,
  `Spark Worker`, `Spark Tester`, or `Generic bounded worker`.
- `expected_writer_count`: maximum expected concurrent writers for the
  scenario.
- `expected_parent_responsibility`: non-empty array of decisions or integration
  duties retained by the parent.
- `expected_fallback`: explicit fallback behavior, or `none`.
- `expected_safety_behavior`: non-empty array of observable safety invariants.

The checker requires all 31 baseline scenarios, unique IDs, valid types, and
cross-field invariants. In particular, parent-only and disabled cases cannot
create workers; delegated cases require at least one worker; writer counts
cannot exceed worker counts; only worker-role scenarios can write; and every
profile remains limited to one concurrent writer, including disjoint files.
The maintained scenarios also cover explicit task caps zero/one, no nested
delegation, one Spark spawn attempt followed by parent return with no host-
default substitution, requested versus confirmed model facts, targeted parent
spot-checking without broad duplicate exploration, and the exact worker-result
fields `conclusion`, `evidence`, `files_and_lines`, `tests_or_checks`, `risks`,
and `recommended_parent_action`.

These fixtures encode the boundaries in
[routing-policy.md](../skills/adaptive-orchestration/references/routing-policy.md)
and [worker-contracts.md](../skills/adaptive-orchestration/references/worker-contracts.md).
They validate the maintained policy dataset, not the quality or availability
of a host model. Behavioral forward tests should compare actual decisions with
these envelopes without changing the expected data merely to make a result
pass.
