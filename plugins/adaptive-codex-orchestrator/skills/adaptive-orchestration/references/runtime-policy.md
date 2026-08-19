# Ultra Orchestration runtime policy

Ultra Orchestration is active for this request.

Active profile: `{{PROFILE}}`
Profile worker cap: `{{MAX_WORKERS}}`
Requested worker setting: `{{PRIMARY_WORKER}}` at `{{REASONING_EFFORT}}`

The parent owns the objective, requirements, decomposition, integration, final
validation, and final answer. This policy changes no parent model, reasoning
level, permissions, sandbox, or global Codex configuration. Ultra reasoning
and worker-model identity are not verified unless the host provides reliable
facts for those exact properties.

Apply this compact gate without loading detailed references:

1. Delegate only a clear, bounded, independently useful, independently
   verifiable slice when its material benefit exceeds orchestration overhead.
2. Effective task worker cap = minimum of the profile cap, any lower host cap,
   the explicit user cap, and the independently useful task count.
3. A user cap of zero or an explicit no-worker request means parent-only.
   Never raise an explicit user cap.
4. Permit at most one concurrent writer. Nested delegation is forbidden.
5. If no worker is selected, record a concise internal no-worker reason and
   continue directly without user-facing orchestration ceremony.

Task overrides: trivial, typo, clear single-file, and unsupported-completion
verification tasks use zero workers. A local reproducible bug defaults to zero
and may use one read-only evidence Explorer only when materially useful. Four
independent modules default to zero workers when the modules and paired tests
are small or obvious; use at most two disjoint read-only Explorers only when
each slice requires substantial independent evidence and the expected saving
clearly exceeds spawn and integration cost. Shared-state, common-fixture,
authentication, permission, and tenant-boundary work uses at most one read-only
Explorer, with all writing and final security validation in the parent.

Only when the gate selects an actual delegated task, read `routing-policy.md`,
`worker-contracts.md`, and `model-policy.json`. Use one spawn attempt per
subtask. On failure, limit, or unsupported explicit model selection, return
that subtask to the parent without retry or host-default substitution. Keep the
requested model separate from any host-confirmed model fact.

Review every result. The parent may spot-check evidence and investigate gaps or
conflicts, but must not repeat delegated broad exploration end to end. Never
report a worker that was not actually created.
