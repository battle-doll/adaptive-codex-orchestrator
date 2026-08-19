# Compatibility

## Compatibility statement

Adaptive Codex Orchestrator is Codex-first and intentionally degrades to a
current-task skill when persistent hooks or model metadata are unavailable.
Compatibility claims in this document describe the repository's expected
contract, not a guarantee that every host account, product surface, or model
quota exposes the same features.

The host contracts summarized here were last checked on **2026-08-18**. Before
publication, recheck the current official plugin, hook, subagent, model, and
public-submission documentation and record any difference.

## Supported Codex surfaces

| Surface/capability | Support level | Behavior |
| --- | --- | --- |
| Codex app and CLI loading current plugin packages | Supported plugin surfaces | Loads the manifest, skill, packaged policies, and default hook configuration when supported. |
| Codex app/CLI with trusted hooks | Intended persistent mode | Korean/English one-shot, session, project, and plugin-global controls can use plugin-owned state. |
| Codex without trusted/supported hooks | Degraded | `$adaptive-orchestration <task>` applies policy to the current task only. No persistent activation is claimed. |
| ChatGPT web, desktop, and mobile plugin surfaces | Plugin package surface, not a Codex-hook guarantee | Do not claim that local Codex lifecycle hooks or persistent state run there; use only capabilities actually exposed by that host. |
| Codex IDE extension | Unsupported for plugins in the checked contract | Do not claim plugin or persistent-hook support; use another supported Codex surface. |
| Host with explicit subagent model settings | Intended routing | Parent may request the configured worker and reasoning effort for suitable bounded tasks. |
| Host without explicit model settings | Parent fallback | Do not claim Spark; keep the work in or return it to the parent. |
| Host omitting worker model identity | Generic contract | Separate requested model from `confirmed model: unavailable from host`. |

The plugin never changes the selected parent model, reasoning setting,
sandbox, approval mode, or Codex global configuration on any surface.

## Hook schema and lifecycle

The checked hook event keys are PascalCase: `SessionStart`, `SessionEnd`,
`UserPromptSubmit`, `SubagentStart`, `SubagentStop`, and `Stop`. This plugin
registers the five events other than `SubagentStop`; it does not need a worker-
completion interceptor for its state lifecycle.
`SessionStart.source` can be `startup`, `resume`, `clear`, or `compact`.
Common input includes `session_id`, nullable `transcript_path`, `cwd`,
`hook_event_name`, and the active `model` slug; reasoning effort is not exposed
in hook input. Event-specific input includes prompt/turn, agent, stop, and
session-end fields defined by the current schema.

Model-visible context uses the event-specific output envelope with the matching
event name and `additionalContext`. The registered cleanup-only `Stop` success
emits `{}`. A blocking Stop decision would create a continuation prompt
and is therefore not used. The package uses the current default hook discovery
location rather than an unsupported manifest `hooks` field. If a host renames
or omits an event, only the current documented equivalent may be used and the
mapping must be recorded.

Persistent behavior depends on receiving a stable session identifier and
reliable completion events. `SessionEnd` applies to the main session and is
synchronous/advisory; the checked contract has a one-second default and three-
second maximum timeout. It can occur on archive, deletion,
normal close, or after the task has not been open in any client for an idle
period; switching away or unsubscribing is not an immediate end signal.
Therefore it is not the only cleanup mechanism: a later `SessionStart` prunes
non-current session entries whose `last_seen` is more than 30 days old, and
stale one-shot state is consumed on a later turn when completion was missed. Missing
fields or unsupported event schemas fail safely and must not mutate state. The
user must not be told cleanup was immediate unless the relevant event was
observed.

When active, `SessionStart` (including `source: compact`), a new enable, and an
active profile change deliver the compact policy. Ordinary active turns use the
session's bounded numeric `active_policy_revision` marker to suppress repeated
delivery of the same packaged revision. If that advisory marker cannot be
persisted, the compact policy may recur. Detailed routing, worker-contract, and
model references are loaded once at delegation time only after the compact gate
selects at least one real delegated task.

## Hook trust requirements

Hooks are local executable code and require the trust mechanism supplied by the
host. Users should review `hooks/hooks.json` and the Python runtime before
trusting them. An untrusted hook is skipped; it is not a reason to request more
permissions. The explicit skill remains available, but it must not claim that
session/project/global state was enabled.

Trust status is reported only as a reliable host fact. When the host does not
expose it, status uses `unknown`.

## Parent model and Ultra reasoning detection

When a reliable common `model` field is available, the hook may use it to
decide whether a concise compatibility notice is appropriate. If the field is
missing, the parent is reported as unavailable and compatibility mode remains
honest. The hook does not block a non-Sol parent.

There is no supported claim that the plugin can verify the user's Ultra
reasoning/intelligence selection. Status must always say:

```text
Ultra reasoning verified: no
```

The user remains responsible for manually selecting the intended parent model
and setting.

## Subagent model selection and information

The model policy requests:

```text
model: gpt-5.3-codex-spark
model_reasoning_effort: medium
```

Current Codex custom-agent configuration supports `model` and
`model_reasoning_effort`; the current agent-spawn interface exposes `model` and
`reasoning_effort`. The parent, not the hook, supplies supported spawn fields.
The hook never rewrites a spawn or changes a selected model. The checked local
catalog supports `low`, `medium`, `high`, and `xhigh` for the configured Spark
entry, but release validation must still honor the active host catalog.

Availability of the configured slug is account-, host-, quota-, and time-
dependent. The public display name `GPT-5.3-Codex-Spark` and lowercase API/host
slug `gpt-5.3-codex-spark` are not interchangeable schema fields. Always use
the current official slug in machine-readable policy and document a change
before release.

`SubagentStart` exposes the common active `model` field, but does not separately
identify requested, resolved, and completed models. If it reports the configured
worker, the relevant Spark contract can be injected. If absent, only a generic
bounded-worker contract is safe. A different active model is left unchanged.
Final reporting should say `requested worker model` and `hook-reported active
model`, not imply a stronger completion or billing attestation. A generic
contract for an already-created worker whose identity is unavailable is not
permission to substitute a host-default worker when the explicit model request
cannot be honored.

## Task caps and worker contract compatibility

The profile ceilings are two, four, and six workers for conservative,
balanced, and fast. They are never targets. The effective task cap is the
minimum of the profile ceiling, a lower host cap, an explicit user cap, the
independently useful task count, and the task-specific safety cap. Canonical
task caps are zero for trivial or clear single-file work and unsupported-
completion checks; zero by default, optionally one read-only Explorer, for a
local reproducible bug; zero by default for four small or obvious module-test
pairs, with at most two disjoint read-only Explorers only when substantial
independent evidence makes the expected saving clearly exceed spawn and
integration cost; and at most one read-only Explorer for shared-state,
authentication, authorization, permission, or tenant work. A user cap of zero
always means parent-only.

Every profile permits at most one concurrent writer, and nested delegation is
forbidden without exception. Every worker result must contain exactly these six
top-level fields: `conclusion`, `evidence`, `files_and_lines`,
`tests_or_checks`, `risks`, and `recommended_parent_action`. The parent reviews
every result and may spot-check citations or investigate gaps and conflicts,
but does not repeat the same broad delegated exploration end to end.

## Spark unavailable or rate-limited

- Make one spawn attempt for each delegated subtask.
- On failure, a usage or rate limit, a host cap, or unsupported explicit model
  selection, return that subtask and any affected queued work to the parent.
- Do not retry the spawn and do not substitute a host-default worker.
- Record the parent fallback when material and never fabricate model use.

## ChatGPT limitations

Plugin packaging is available on ChatGPT web, desktop, and mobile as well as
the Codex app and CLI, but the hook contract checked here is the Codex lifecycle
contract. This repository does not claim that a general ChatGPT conversation
executes local Codex hooks, supplies `PLUGIN_DATA`, exposes Codex cleanup, or
supports the same subagent settings. On a surface that can read the skill but
cannot run trusted persistent hooks, only current-task orchestration should be
described as supported. No ChatGPT App, MCP server, OAuth integration, or
remote service is included in this package.

## IDE support

The checked plugin contract does not support the Codex IDE extension. Do not
market plugin installation, persistent hooks, or the fallback skill as an IDE
extension capability. Users should use the Codex app or CLI unless a future
official contract adds IDE plugin support and this document is updated.

## Platform support

| Platform | Intended behavior | Important qualification |
| --- | --- | --- |
| Windows | Standard-library paths and current `commandWindows` hook entries, no Bash assumption | Commands should resolve wrappers from `PLUGIN_ROOT`; POSIX permission bits do not provide the same guarantee and launcher availability must be smoke-tested. |
| macOS | Standard-library paths and POSIX hook command | File permissions and symlinks remain host/filesystem dependent. |
| Linux | Standard-library paths and POSIX hook command | Python launcher and writable `PLUGIN_DATA` must be available. |

Path tests must include Windows- and POSIX-style inputs. Git may be missing or
the directory may not be a repository. Locking, case normalization, symlink
resolution, and user-only permissions are best-effort platform behaviors and
must not be described as identical guarantees.

Hook processes begin with the session working directory, not necessarily the
plugin root. Hook commands and wrappers must resolve packaged files from the
host-provided `PLUGIN_ROOT`. Writable state must resolve from the dedicated
`PLUGIN_DATA` location.

## Known schema and validator limitations

- The current local plugin validator rejects a manifest `hooks` field; default
  `hooks/hooks.json` discovery is used instead.
- The checked plugin package contract does not auto-install `.codex/agents` as
  reusable custom agents. Explorer, Worker, and Tester are skill/policy
  contracts supplied through explicit parent-owned spawn requests.
- The installed general plugin validator does not validate the marketplace,
  full hook schema, starter-prompt count/length, or exact PNG dimensions. The
  repository package validator covers the marketplace, prompt, and PNG checks;
  official upload scanning and manual installation cover the remaining host
  contract.
- The installed validator currently rejects some optional fields accepted by
  the current public manifest contract, including `supportURL` and
  `brandColorDark`. This candidate enters support in the submission form and
  relies on default `hooks/hooks.json` discovery instead of weakening either
  contract or inventing a field.
- Parent model, worker model, trust, compaction source, and lifecycle fields may
  be absent on a particular host. Missing data is reported as unavailable or
  unknown, never inferred.
- Public packaging and submission requirements can change after this review;
  [Publishing](PUBLISHING.md) treats final verification as an owner action.

## Related documents

- [Architecture](ARCHITECTURE.md)
- [Security](SECURITY.md)
- [Testing](TESTING.md)
