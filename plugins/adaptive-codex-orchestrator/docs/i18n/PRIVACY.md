# Privacy overview

**English** · [한국어](PRIVACY.ko.md) · [日本語](PRIVACY.ja.md) ·
[简体中文](PRIVACY.zh-CN.md) · [Русский](PRIVACY.ru.md)

Effective date: **2026-08-19**

This is a concise public-review companion to the detailed, authoritative
[Privacy policy](../PRIVACY.md).

## Local data behavior

The control plane operates locally and offline. It makes no external network
request, collects no telemetry, uses no analytics, and requires no API key,
OAuth grant, or external account. Separate Codex host, model-provider,
operating-system, Git, and repository-provider behavior is governed by their
own policies.

The active file `${PLUGIN_DATA}/state-v1.json` contains only the schema version;
global, project, session, and one-shot mode/profile preferences; SHA-256 project
keys; session identifiers; lifecycle flags; and bounded last-seen values used
for cleanup. The project hash is a stable pseudonymous identifier, not
encryption. A person who knows a candidate path can recompute it.

The runtime may also create a lock, transient atomic-write files, and a
content-addressed backup of readable corrupt state. A corrupt file modified by
another process may contain arbitrary bytes, so treat its backup as sensitive
local evidence; the plugin never interprets or transmits it.

The plugin does not persist prompts, transcripts, source code, patches, raw
absolute project paths, repository names, credentials, model output, worker
conversations, validation logs, telemetry, or advertising identifiers. Prompt
text is parsed in memory only for the current event.

One-shot state is cleared after request completion. Session state is cleared
when the host reports session end; because that event may be missed, inactive
session entries older than **30 days** are also removed during a later
`SessionStart`. Project and global preferences remain until changed or reset.

## Safe reset

End affected sessions, obtain and resolve the exact host-assigned `PLUGIN_DATA`
directory for `adaptive-codex-orchestrator`, and verify that it is the plugin-
specific data directory—not the plugin source, repository root, home directory,
`.codex` root, or a shared parent. Delete only that confirmed directory, or only
`state-v1.json` to retain recovery material. Never use wildcards, unresolved
environment variables, a home directory, or a shared parent as a recursive
deletion target.

Any future network access, telemetry, credentials, prompt/source persistence,
transcript access, new identifier, or recipient requires an explicit policy
update, security review, user-visible disclosure, versioned state handling, and
any required consent.

Control commands are recognized in Korean and English only. These translations
do not add Japanese, Simplified Chinese, or Russian command support.
