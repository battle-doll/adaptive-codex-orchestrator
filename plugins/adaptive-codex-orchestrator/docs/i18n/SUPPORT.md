# Support

**English** · [한국어](SUPPORT.ko.md) · [日本語](SUPPORT.ja.md) ·
[简体中文](SUPPORT.zh-CN.md) · [Русский](SUPPORT.ru.md)

> Verified 2026-08-29: `0.1.0` is Published and remote-catalog
> `GLOBAL` / `AVAILABLE` / `UNLISTED`. Version `0.1.1` is an unsubmitted update
> candidate. [GitHub Issues](https://github.com/battle-doll/adaptive-codex-orchestrator/issues)
> provides best-effort general support with no response-time commitment.

Adaptive Codex Orchestrator is an independent, community-created developer
tool. It is not affiliated with, sponsored by, endorsed by, or an official
product of OpenAI. Support is best effort and does not replace professional
security, legal, privacy, or production review.

## Before requesting help

Review the current [README](../../README.md),
[Compatibility](../COMPATIBILITY.md), [Security](../SECURITY.md),
[Privacy](../PRIVACY.md), and [Validation](../VALIDATION.md). Confirm:

- Plugin version and operating system.
- Codex surface: app or CLI. The checked contract does not support plugin use
  in the Codex IDE extension.
- Whether `hooks/hooks.json` was reviewed and trusted by the host.
- Whether the failure occurs with persistent hooks or only with the explicit
  `$adaptive-orchestration <task>` fallback.
- Exact expected and observed behavior, minimal reproduction, and relevant
  validation command output.

Do not post credentials, API keys, private prompts, transcripts, proprietary
source code, repository contents, account identifiers, or private absolute
paths. Redact local values while keeping the reproduction useful.

## Common issues

### Mode does not persist

Persistent one-shot, session, project, and plugin-global controls require a
Codex surface with supported, trusted hooks and writable `PLUGIN_DATA`. When
hooks are unavailable or untrusted, use:

```text
$adaptive-orchestration <task>
```

That fallback applies to the current task only and must not be described as a
persistent activation.

### Compatibility notice appears

The plugin does not select or change the parent model. Manually select the
intended parent model and Ultra setting. A missing or non-Sol host model report
does not block execution, and the plugin never claims that Ultra reasoning was
verified.

### Spark is unavailable or not confirmed

The configured worker is `gpt-5.3-codex-spark`, but the host controls model
availability and reporting. Make at most one spawn attempt per delegated
subtask. On failure, a limit, or unsupported selection, do not retry or
substitute the host-default model; return the work to the parent. Requested and
host-reported models must remain separate facts.

### Git or project identity is unavailable

If Git is missing, times out, or the directory is not a repository, project
identity falls back to a SHA-256 digest of the normalized working directory.
Raw project paths are not persisted.

### State is malformed or unwritable

Ordinary Codex behavior continues without active plugin state. Readable damaged
state may be preserved as a local recovery backup when storage permits. The
backup can contain arbitrary bytes from the damaged state file and should be
treated as potentially sensitive local evidence; it is never interpreted or
transmitted by the plugin.

## Safe state reset

1. End affected Codex sessions.
2. Obtain the exact host-assigned `PLUGIN_DATA` directory for
   `adaptive-codex-orchestrator`.
3. Resolve and inspect it. Confirm it is the plugin-specific data directory,
   not the plugin source, repository root, home directory, `.codex` root, or a
   shared parent.
4. Delete only that confirmed plugin-owned directory, or only `state-v1.json`
   if recovery material should remain.

Never use a wildcard, unresolved environment variable, home directory, or
shared plugin-data parent as a recursive deletion target. See
[Privacy](../PRIVACY.md) for the complete retention and deletion contract.

## Security reports

Do not disclose exploit details, credentials, prompts, proprietary source, or
private paths in a public issue. The designated security-reporting candidate is a
[private GitHub advisory](https://github.com/battle-doll/adaptive-codex-orchestrator/security/advisories/new),
which must be enabled and verified before use. If it is unavailable, withhold
sensitive details and first ask the maintainer for a private channel.

Include the affected version, platform and Codex surface, minimal reproduction,
impact, and whether trusted hooks are required. No acknowledgement or response-
time guarantee is made until the maintainer publishes one. The authoritative
process is in [Security](../SECURITY.md).

## Publication status

The manifest records publisher `battle-doll` and designates the
[GitHub repository](https://github.com/battle-doll/adaptive-codex-orchestrator),
website, privacy, and terms locations as candidate public destinations. GitHub
Issues is the designated general-support candidate; private advisories are the
designated security-reporting candidate. These designations are not proof of
accessibility or publication and must be verified before use. The owner must
complete [Publishing](../PUBLISHING.md), verify every destination, and authorize
submission explicitly before presenting the plugin as marketplace-published or
approved.

Control commands are recognized in Korean and English only. Localized support
documentation does not add Japanese, Simplified Chinese, or Russian command
support.

Translations are informational. If this page conflicts with the maintained
English documentation, the English source, [Terms](../TERMS.md), and the
untranslated [MIT License](../../LICENSE) control.
