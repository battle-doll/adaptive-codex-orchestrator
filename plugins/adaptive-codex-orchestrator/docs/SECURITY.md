# Security

## Security posture

Adaptive Codex Orchestrator is a local, offline control and policy layer. Its
security objective is to preserve normal Codex permission boundaries while
adding deterministic mode state and bounded delegation guidance. It does not
make delegated code safe by itself. The parent and user must review generated
changes before relying on them.

This is an independent community project and is not affiliated with or
endorsed by OpenAI.

## Threat model

The design considers:

- Prompt text that resembles a control command accidentally or maliciously
  changing persistent state.
- Commands embedded in quoted examples, fenced code, long pasted text, or
  conflicting instructions.
- Malformed, stale, concurrently written, or future-version state.
- Path disclosure through project preferences, logs, errors, or backup files.
- Shell injection through prompt text, paths, Git discovery, or hook commands.
- A hook receiving malformed or unsupported JSON.
- A worker expanding scope, writing overlapping files, delegating recursively,
  or claiming validation without evidence.
- A host omitting or misreporting parent or worker model identity.
- Untrusted plugin code receiving the same local access as the Codex process.

The model does not attempt to protect a machine from a malicious or already
compromised Codex host, Python interpreter, operating system account, Git
binary, or plugin package. It also cannot guarantee the correctness or safety
of model-generated code.

## Trust boundaries

1. **User and host:** the user selects the parent model, reasoning setting,
   sandbox, and approval policy. The plugin does not change them.
2. **Host and hook:** trusted hooks receive event JSON and may read/write only
   plugin-owned state. Review `hooks/hooks.json` and `hooks/runtime.py` before
   granting trust.
3. **Control and execution planes:** deterministic code decides only control
   facts and context. The parent model owns architectural and product judgment.
4. **Parent and workers:** every worker gets a bounded contract. The parent
   reviews evidence and validation before integration.
5. **Plugin state and project:** the state key is a SHA-256 digest of a
   normalized root. The raw project path and source are not persisted.

See [Architecture](ARCHITECTURE.md) for the detailed lifecycle.

## Hook risks and controls

- Disabled ordinary requests emit no orchestration policy.
- Invalid JSON, unknown events, unsupported schema, and unavailable state fail
  closed for plugin functionality while preserving normal Codex behavior.
- Hooks do not preprocess or rewrite tool/subagent calls, auto-approve tools,
  alter permissions, elevate the sandbox, or request another model turn.
- A compatibility notice is rate-limited to once per session.
- Active hooks deliver a compact policy. A bounded numeric
  `active_policy_revision` session marker suppresses repeated delivery of the
  same revision on ordinary active turns; it contains no prompt or task text.
- One-shot and session cleanup is scoped to the current session; project and
  global preferences and other sessions are preserved.
- Hook trust is an explicit user/host decision. If hooks are not trusted, the
  one-shot skill is the supported fallback.

## Prompt command parsing risks and controls

The parser is deterministic and uses no LLM. It normalizes Unicode with NFKC,
case-folds, normalizes whitespace, masks fenced code, and attempts to exclude
quoted examples before classifying intent. Status and explicit negation take
priority over activation. Conflicting scopes, profiles, or enable/disable
instructions preserve state and return an ambiguity fact.

Prompt text exists in memory only for the current event. It must never be
stored, logged, evaluated, or interpolated into a command. A long prompt needs
both a recognized mode alias and an action phrase at a command-like boundary.

## State corruption and concurrency

State is schema-versioned and deterministically serialized under
`PLUGIN_DATA`. Writes use a same-directory temporary file followed by
`os.replace` and a best-effort cross-platform lock. Readable malformed or
unsupported state is preserved before clean recovery when storage permits.
Failure to read or write state must not block ordinary Codex work.

Recovery backups preserve raw prior bytes. Although this runtime never writes
prompts or source into state, another process with write access could have put
arbitrary content in a corrupt file. Treat corrupt backups as potentially
sensitive local evidence; they are never interpreted or transmitted.

Locks and user-only permissions are platform-specific best efforts, not a
cross-platform security boundary. Do not share one writable `PLUGIN_DATA`
directory between mutually untrusted operating-system users.

## Path and shell safety

Project-root discovery invokes Git with an argument array, `shell=False`,
captured output, and a short timeout. Missing Git, a timeout, and a non-Git
directory fall back to the normalized current directory. Prompt text is never
part of this command. Only a SHA-256 digest of the normalized root is retained.

Hook commands must use the current host schema and platform-appropriate Python
launcher. They must not assume Bash on Windows or concatenate user-controlled
text into a shell command.

## Permission boundaries

The plugin requires no API key, OAuth grant, external account, network access,
or additional sandbox permission. It contains no path for changing
`~/.codex/config.toml`, the model selector, reasoning level, tool approvals, or
the sandbox. A mode toggle writes only to the plugin's `PLUGIN_DATA` location.

## Delegation safety

- Delegation is optional and limited to bounded, reversible, independently
  verifiable work when it provides a material benefit.
- Profile ceilings are two, four, and six workers for conservative, balanced,
  and fast, but task-aware safety caps reduce actual use to zero, one, or two
  where applicable. Trivial or clear single-file work and unsupported-
  completion checks use zero. A local reproducible bug defaults to zero and may
  use one read-only Explorer only for materially useful independent evidence.
  Four small or obvious module-test pairs also default to zero. At most two
  disjoint read-only Explorers are used only when substantial independent
  evidence makes the expected saving clearly exceed spawn and integration
  cost. Shared-state, authentication, authorization, permission, and tenant
  work may use at most one read-only Explorer and keeps the parent as the only
  writer.
- Every profile permits at most one concurrent writer. There is no disjoint-
  file or fast-profile exception.
- Nested delegation is forbidden without exception.
- Detailed routing, worker-contract, and model references are loaded once only
  after the compact gate selects a real delegated task.
- Each delegated subtask gets one Spark spawn attempt. Failure, a limit, or
  unsupported explicit model selection returns it to the parent without retry
  or host-default substitution.
- Requested model settings stay separate from host-confirmed facts; a start-
  time model report is not completion or billing attestation.
- Every worker returns exactly `conclusion`, `evidence`, `files_and_lines`,
  `tests_or_checks`, `risks`, and `recommended_parent_action`, with no other
  top-level fields. Missing concrete evidence or exact validation is incomplete.
- Architecture, authentication, authorization, cryptography, destructive/data-
  loss-sensitive decisions, major public API/dependency changes, integration,
  and final validation judgment remain with the parent.
- The parent may spot-check cited evidence and investigate gaps or conflicts,
  but must not repeat the same broad delegated exploration end to end.

## Unsupported and residual-risk scenarios

- The plugin cannot verify the host's Ultra reasoning setting.
- A missing model identifier prevents model-specific enforcement or reporting.
- A host without reliable completion/session-end events may delay cleanup; a
  later event must remove stale one-shot state where supported.
- Untrusted or unsupported hooks cannot provide persistent natural-language
  control.
- A compromised dependency-free Python runtime, Git executable, host, or
  plugin directory is outside this control plane's protection.
- Model output and delegated edits can still contain security defects and need
  human review appropriate to their impact.

## Reporting a vulnerability

Do not include exploit details, credentials, prompts, proprietary source code,
or private paths in a public issue. Until the repository owner publishes a
dedicated security contact, report privately through the repository host's
private security-advisory feature or the support channel designated in the
release metadata. If neither exists, withhold sensitive details and ask the
maintainer for a private channel first.

Include the affected version, platform and Codex surface, minimal reproduction,
security impact, and whether the issue requires trusted hooks. The maintainer
should acknowledge, triage, coordinate remediation and disclosure, and credit
the reporter when requested and appropriate. No response-time guarantee is
made before a maintainer publishes one.
