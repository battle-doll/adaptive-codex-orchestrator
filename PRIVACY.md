# Privacy Policy

**English** · [한국어](plugins/adaptive-codex-orchestrator/docs/i18n/PRIVACY.ko.md) ·
[日本語](plugins/adaptive-codex-orchestrator/docs/i18n/PRIVACY.ja.md) ·
[简体中文](plugins/adaptive-codex-orchestrator/docs/i18n/PRIVACY.zh-CN.md) ·
[Русский](plugins/adaptive-codex-orchestrator/docs/i18n/PRIVACY.ru.md)

Effective date: **2026-08-19**
Publisher: **battle-doll**

## Summary

Adaptive Codex Orchestrator is designed to operate locally and offline. The
plugin makes no external network requests, collects no telemetry, uses no
analytics service, and requires no API key, OAuth grant, or external account.
It has no external data recipient of its own.

This policy describes the plugin implementation, not separate processing by
the Codex host, selected models, operating system, Git, GitHub, or extensions.

## Purpose and data stored

The plugin stores only local preferences and lifecycle facts needed to resolve
the requested orchestration mode. The active file is
`${PLUGIN_DATA}/state-v1.json` and may contain:

- State schema version.
- Plugin-global enabled preference and profile.
- Project enabled/profile preferences keyed by a SHA-256 digest.
- Session enabled/profile overrides, a compatibility-notice flag, bounded
  last-seen data, and one-shot lifecycle identifiers.

Atomic writes may temporarily create a lock and sanitized temporary file.
Readable malformed state may be preserved as a content-addressed recovery
backup inside the same plugin-owned directory. Because another local process
could have altered malformed state, treat such a backup as potentially
sensitive; the plugin neither interprets nor transmits it.

## Data not stored or collected

The plugin does not persist or intentionally collect prompts, transcripts,
source code, generated patches, raw absolute project paths, repository names,
tool or worker conversations, validation logs, credentials, tokens, account
identifiers, telemetry, analytics identifiers, or usage profiles. Prompt text
is parsed only in memory for the current hook event.

## Project identity

Project preferences use `SHA-256(normalized Git root or current directory)`.
The hash reduces casual path disclosure but is a pseudonymous identifier, not
encryption; someone who already knows a candidate path could compare its hash.

## Location, retention, and deletion

State stays in the host-provided plugin-specific `PLUGIN_DATA` directory.
One-shot state is cleared after completion. Session state is cleared on a host
session-end event, with inactive records older than 30 days pruned on a later
session start when immediate cleanup was missed. Project and plugin-global
preferences remain until changed or reset.

To delete plugin data, end affected Codex sessions, obtain the exact
host-assigned plugin-specific `PLUGIN_DATA` path, verify it is not a repository,
home directory, `.codex` root, or shared parent, and remove only that confirmed
plugin-owned directory. Never target a wildcard, unresolved variable, home
directory, or shared data root recursively.

## Changes and contact

Any future feature adding network access, telemetry, credentials, prompt or
source persistence, transcript access, a new identifier, or a new recipient
requires a policy update and security review. Privacy questions may be filed
through [Support](SUPPORT.md); sensitive security matters belong in a
[private advisory](https://github.com/battle-doll/adaptive-codex-orchestrator/security/advisories/new).

The plugin archive contains the detailed offline policy at
[`docs/PRIVACY.md`](plugins/adaptive-codex-orchestrator/docs/PRIVACY.md), and
translations are listed in the
[five-language index](plugins/adaptive-codex-orchestrator/docs/i18n/README.md).
