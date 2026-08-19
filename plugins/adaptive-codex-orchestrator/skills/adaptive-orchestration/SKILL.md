---
name: adaptive-orchestration
description: Configure and apply Ultra Orchestration when users enable, disable, query, or profile adaptive delegation for a task, session, project, or global scope. Use for explicit $adaptive-orchestration requests and recognized Korean or English orchestration commands; do not activate merely because ordinary work could be delegated.
---

# Adaptive Orchestration

Use this skill to operate the **Ultra Orchestration** runtime mode supplied by
Adaptive Codex Orchestrator. The plugin is an independent, community-created
developer tool and is not affiliated with or endorsed by OpenAI.

## Control and state

For enable, disable, status, scope, or profile requests, read
[command-language.md](references/command-language.md). Treat deterministic hook
state and injected state facts as authoritative when they are available. Never
claim that a parent model or Ultra reasoning was verified unless the host
provides a reliable fact for that exact property.

The plugin never changes the selected parent model, reasoning level,
permissions, sandbox, or global Codex configuration. If persistent hooks are
unavailable, an explicit skill invocation may apply orchestration to the
current request only; state that limitation and do not claim persistent mode
activation.

## Task-time gate

Apply this compact gate on an ordinary active turn without loading detailed
routing references:

1. Delegate only a clear, bounded, independently useful, independently
   verifiable slice when its material benefit exceeds orchestration overhead.
2. Effective task worker cap = minimum of the active profile cap, any lower
   host cap, the explicit user cap, and the independently useful task count.
3. A user cap of zero or an explicit no-worker request means parent-only.
   Never raise an explicit user cap.
4. Permit at most one concurrent writer. Nested delegation is forbidden.
5. If no worker is selected, record a concise internal no-worker reason and
   continue directly without user-facing orchestration ceremony.

Apply lower task caps before any profile ceiling: clear one-word, typo, or
single-file edits and unsupported-completion verification use zero workers; a
local reproducible bug defaults to zero and permits at most one read-only
evidence Explorer when that evidence materially helps. Four independent
modules also default to zero when the modules and paired tests are small or
obvious; permit at most two disjoint read-only Explorers only when each slice
requires substantial independent evidence and the expected saving clearly
exceeds spawn and integration cost. Shared-state or common fixture conflicts
and authentication/permission/tenant boundaries permit at most one read-only
Explorer. The parent is the only writer and final security validator for those
capped categories.

The parent retains requirements, architecture, integration, final validation,
and the final answer.

## After selecting delegation

Only after the gate selects at least one actual delegated task:

1. Read [routing-policy.md](references/routing-policy.md) for decomposition,
   task caps, and parent review boundaries.
2. Read [worker-contracts.md](references/worker-contracts.md) and give every
   worker a bounded contract with the exact six-field result schema.
3. Read [model-policy.json](references/model-policy.json) as the single source
   of requested worker-model and reasoning settings. Do not duplicate or
   invent model identifiers elsewhere.
4. Make one spawn attempt per delegated subtask. If it fails, is limited, or
   is unsupported, return that subtask to the parent without retrying or using
   a host-default worker.
5. Keep requested model settings separate from host-confirmed model facts.
   Review every result, integrate deliberately, and run proportionate final
   validation in the parent.

After delegated exploration, the parent may spot-check evidence and investigate
gaps or conflicts, but must not repeat the same broad exploration end to end.
Never fabricate worker identity or report a worker that was not actually
created.

When hook context supplies a compact active policy, follow it. Read
[runtime-policy.md](references/runtime-policy.md) only when reviewing or
diagnosing the policy template, not during an ordinary task turn.
