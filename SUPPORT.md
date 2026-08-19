# Support

**English** · [한국어](plugins/adaptive-codex-orchestrator/docs/i18n/SUPPORT.ko.md) ·
[日本語](plugins/adaptive-codex-orchestrator/docs/i18n/SUPPORT.ja.md) ·
[简体中文](plugins/adaptive-codex-orchestrator/docs/i18n/SUPPORT.zh-CN.md) ·
[Русский](plugins/adaptive-codex-orchestrator/docs/i18n/SUPPORT.ru.md)

Effective date: **2026-08-19**

Adaptive Codex Orchestrator is maintained by
[`battle-doll`](https://github.com/battle-doll) as an independent community
project. Support is best effort and has no guaranteed response time.

## General help and bug reports

Use the repository's
[GitHub Issues](https://github.com/battle-doll/adaptive-codex-orchestrator/issues)
for reproducible bugs, compatibility reports, documentation problems, and
feature proposals. Before opening an issue, review the
[plugin README](plugins/adaptive-codex-orchestrator/README.md),
[compatibility notes](plugins/adaptive-codex-orchestrator/docs/COMPATIBILITY.md),
and [validation record](plugins/adaptive-codex-orchestrator/docs/VALIDATION.md).

Include the plugin version, operating system, Codex surface, whether hooks were
reviewed and trusted, a minimal reproduction, expected and observed behavior,
and relevant non-sensitive validation output.

Do not post credentials, API keys, private prompts, transcripts, proprietary
source, repository contents, account identifiers, or private absolute paths.

## Security reports

Do not file public exploit details. Use GitHub's
[private security advisory form](https://github.com/battle-doll/adaptive-codex-orchestrator/security/advisories/new)
and include the affected version, platform, impact, minimal reproduction, and
whether trusted hooks are required. See [Security](SECURITY.md).

## Common checks

- If persistent mode does not work, confirm the Codex surface supports plugins,
  hooks are trusted, and `PLUGIN_DATA` is writable. Otherwise use the explicit
  `$adaptive-orchestration <task>` one-shot fallback.
- If the compatibility notice appears, manually confirm the intended parent
  model and reasoning setting. The plugin cannot change or verify them.
- If the configured worker is unavailable, return the work to the parent; do
  not repeatedly retry or claim a worker model the host did not confirm.

Translated support summaries are listed in the
[five-language document index](plugins/adaptive-codex-orchestrator/docs/i18n/README.md).
