# Architecture

Adaptive Codex Orchestrator is a two-layer, offline orchestration harness. The
control plane is deterministic Python. The execution plane remains the active
parent model and the host's native subagent interface.

## Design invariants

1. The parent owns requirements, architecture, delegation judgment,
   integration, validation, and the final answer.
2. A mode toggle changes only plugin-owned state under `PLUGIN_DATA`.
3. The plugin never changes the selected parent model, reasoning effort,
   sandbox, approval mode, or global Codex configuration.
4. Delegation is optional. Only bounded, reversible, independently verifiable
   work should be offered to a fast worker.
5. Requested worker settings and host-confirmed model facts remain separate; a
   start-time model report is not completion or billing attestation.
6. Prompt and transcript contents are neither logged nor persisted.

## Control plane

The hook entry point, `hooks/runtime.py`, reads one current Codex hook event as
JSON from standard input and emits one JSON object on standard output. Its
standard-library modules have narrow responsibilities:

| Module | Responsibility |
| --- | --- |
| `command_parser.py` | NFKC normalization and deterministic Korean/English control-intent parsing |
| `state_store.py` | Versioned state, precedence, locking, recovery, and atomic writes |
| `project_identity.py` | Safe Git-root discovery and one-way SHA-256 project identity |
| `policy_loader.py` | Load and validate packaged policies without network access |
| `hook_output.py` | Produce event-specific current Codex hook output shapes |

The parser receives prompt text in memory only. Its result contains intent,
scope, profile, confidence, ambiguity, and a remaining-task flag; the original
prompt never enters state or logs.

## State schema and precedence

State is stored at `${PLUGIN_DATA}/state-v1.json`:

```json
{
  "schema_version": 1,
  "global": {
    "enabled": false,
    "profile": "balanced",
    "configured": false
  },
  "projects": {"<sha256>": {"enabled": true, "profile": "balanced"}},
  "sessions": {
    "<session-id>": {
      "enabled": false,
      "profile": "balanced",
      "compatibility_notice_shown": false,
      "active_policy_revision": 3,
      "last_seen": 1787000000
    }
  },
  "one_shot": {
    "<session-id>": {"enabled": true, "profile": "fast", "turn_id": "<turn-id>"}
  }
}
```

`enabled` and `profile` are independently optional on project, session, and
one-shot entries. This lets a session profile override a project profile
without implicitly changing whether the project is enabled.

Enablement precedence is:

```text
one-shot > session > project > global > disabled
```

Profile precedence follows the same order, independently of enablement. A
generic disable writes a session-level `enabled: false` override; it never
deletes project or global preferences. A project or global disable writes an
explicit OFF preference at that scope.

`global.configured` distinguishes the untouched default from an explicit
global OFF preference. `active_policy_revision` is a bounded numeric marker
used only to suppress repeat delivery of the same compact policy in a session;
it contains no prompt or task content. `last_seen` is a coarse lifecycle
timestamp, not user content. On a later `SessionStart`, session records older
than 30 days are removed unless they belong to the current session; this is a
bounded backup for the advisory `SessionEnd` event.

Writes occur under a best-effort cross-platform lock, use a temporary file plus
`os.replace`, and are deterministically serialized. Malformed or unsupported
readable state is preserved as a content-addressed backup before a clean state
is used. User-only file permissions are applied on POSIX systems where the API
is meaningful.

## Project identity

The runtime invokes `git rev-parse --show-toplevel` with an argument array,
`shell=False`, captured output, and a short timeout. If Git is missing, times
out, or the directory is not a repository, the current working directory is
used. Separators and platform case rules are normalized, then only this value
is retained:

```text
SHA-256(normalized root)
```

No absolute path or repository name is written to state.

## Hook lifecycle

```mermaid
sequenceDiagram
    participant H as Codex host
    participant C as Control plane
    participant S as PLUGIN_DATA state
    participant P as Parent model
    participant W as Delegated worker

    H->>C: SessionStart(startup/resume/clear/compact)
    C->>S: Read effective state
    C-->>P: Compact policy only when active
    H->>C: UserPromptSubmit(prompt)
    C->>C: Parse in memory
    C->>S: Apply only unambiguous control change
    C-->>P: Revised compact policy, status, notice, or no context
    P->>P: Apply compact gate; select zero or more bounded tasks
    P->>P: Load detailed references once only if delegation was selected
    P->>W: Bounded contract + explicit supported model settings
    H->>C: SubagentStart
    C-->>W: Model-confirmed or generic bounded-worker context
    W-->>P: Exact six-field evidence and validation result
    P->>P: Review, spot-check, integrate, and validate
    H->>C: Stop
    C->>S: Clear one-shot state
    H->>C: SessionEnd
    C->>S: Clear this session and one-shot only
```

### `SessionStart`

- Disabled: emit no model-visible context.
- Enabled: inject the compact active policy, effective profile, and configured
  worker, then store the numeric session policy revision.
- `source: compact`: restore the compact active policy after compaction.
- If the host model is missing or not recognized as Sol, add one compatibility
  notice per session. Ultra reasoning is never claimed as verified.

### `UserPromptSubmit`

- Status takes precedence and never mutates state.
- Unambiguous controls update state and affect the same turn.
- Newly enabled mode and active profile changes deliver the compact policy and
  update the session revision marker.
- An ordinary active turn receives the compact policy only when its stored
  `active_policy_revision` differs from the packaged revision. Matching
  revisions suppress repeated policy delivery; inactive turns receive no
  context. If the advisory marker cannot be written, a later turn may receive
  the compact policy again.
- Ambiguity preserves state and adds only a concise diagnostic.

### `SubagentStart`

The current hook schema supplies `agent_id`, `agent_type`, and the common
`model` field. A confirmed configured worker receives the relevant contract.
If `model` is absent, a generic bounded-worker contract is used and the plugin
must not claim Spark ran. This handles an already-created worker with missing
identity; it does not authorize a host-default fallback when explicit model
selection is unsupported. A confirmed different model is left unchanged. The
hook never rewrites a spawn call or changes permissions.

### `Stop` and `SessionEnd`

`Stop` clears one-shot state and emits an empty JSON object; it never requests
another model turn. `SessionEnd` clears only that session and its one-shot
entry. Project/global state and other sessions remain intact.

## Execution plane

The execution plane is policy, not a workflow engine. The parent applies the
compact gate before loading detailed references. It evaluates clarity, benefit,
boundaries, verifiability, write overlap, and overhead. Zero workers is the
default for trivial or clear single-file edits, unsupported-completion checks,
and local reproducible bugs; the last category may use one read-only Explorer
only when independent evidence materially helps. Four small or obvious module-
test pairs also default to zero. At most two disjoint read-only Explorers are
used only when each slice needs substantial independent evidence and the
expected saving clearly exceeds spawn and integration cost. Shared-state,
authentication, authorization, permission, and tenant work may use at most one
read-only Explorer and keeps all writes in the parent.

Only after at least one real delegated task survives that gate does the parent
load `routing-policy.md`, `worker-contracts.md`, and `model-policy.json` once.
It creates a task contract with role, objective, scope, allowed areas,
forbidden actions, required evidence, validation, and return format. Every
worker result has exactly six top-level fields: `conclusion`, `evidence`,
`files_and_lines`, `tests_or_checks`, `risks`, and
`recommended_parent_action`.

The model policy is defined once in
`skills/adaptive-orchestration/references/model-policy.json`. Current Codex
subagent configuration supports explicit `model` and
`model_reasoning_effort`; the policy requests those fields when the host makes
them available. Each delegated subtask receives one Spark spawn attempt. A
failed, limited, or unsupported explicit request returns to the parent without
retry or host-default substitution. The request remains distinct from any
host-reported active model, which is only a start-time fact.

## Parallelism and conflict prevention

| Profile | Worker ceiling per parent turn | Concurrent writers | Spawn attempts per delegated subtask | Delegated retries |
| --- | ---: | ---: | ---: | ---: |
| conservative | 2 | 1 | 1 | 0 |
| balanced | 4 | 1 | 1 | 0 |
| fast | 6 | 1 | 1 | 0 |

Profile values are ceilings, not targets. The effective task cap is the minimum
of the profile ceiling, any lower host or explicit user cap, the independently
useful task count, and the applicable zero/one/two task-specific safety cap.
Parallel reads are preferred. At most one worker may write concurrently in
every profile; sensitive task categories keep the parent as the only writer.
Nested delegation is forbidden without exception, so all decomposition remains
with the parent.

The parent reviews every result and may spot-check cited evidence or investigate
gaps and conflicts. It must not repeat the same broad delegated exploration end
to end; verification is targeted and integration remains parent-owned.

## Skill fallback

`$adaptive-orchestration <task>` is a current-task-only fallback. It applies the
same compact gate and loads detailed model, routing, and worker policies only if
the gate selects delegation. It does not write persistent state or claim that
session/project/global activation succeeded. This keeps the core workflow
usable on surfaces where plugin hooks are unavailable or untrusted.

## Failure behavior and trust boundaries

- Missing or read-only `PLUGIN_DATA`: ordinary Codex behavior continues;
  relevant control requests receive a concise diagnostic.
- Missing Git: hash the normalized current directory.
- Invalid input/event/schema: emit safe empty JSON and do not mutate state.
- Missing worker model identity: use generic worker language and report the
  requested/confirmed distinction.
- Untrusted hooks: the host skips them; the explicit skill remains usable.
- The runtime has no network code, telemetry, credential handling, transcript
  reads, tool approval path, or sandbox mutation path.

## Verified host contracts

This architecture was checked on 2026-08-18 against the official
[Codex hooks](https://developers.openai.com/codex/hooks),
[subagents](https://developers.openai.com/codex/subagents), and
[plugin packaging](https://developers.openai.com/plugins/build/plugins)
documentation. The default `hooks/hooks.json` discovery path is used so the
manifest does not need a redundant `hooks` field.
