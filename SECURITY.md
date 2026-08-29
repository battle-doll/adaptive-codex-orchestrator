# Security Policy

**English** · [한국어](plugins/adaptive-codex-orchestrator/docs/i18n/SECURITY.ko.md) ·
[日本語](plugins/adaptive-codex-orchestrator/docs/i18n/SECURITY.ja.md) ·
[简体中文](plugins/adaptive-codex-orchestrator/docs/i18n/SECURITY.zh-CN.md) ·
[Русский](plugins/adaptive-codex-orchestrator/docs/i18n/SECURITY.ru.md)

## Supported version

Security fixes are provided for the latest published version. Version `0.1.0`
is the current supported published release; version `0.1.1` is an unsubmitted
update candidate.

## Reporting a vulnerability

Please use GitHub's
[private security advisory form](https://github.com/battle-doll/adaptive-codex-orchestrator/security/advisories/new).
Do not publish exploit details, credentials, prompts, proprietary source, or
private paths in an issue. Include the affected version, platform and Codex
surface, minimal reproduction, impact, and whether trusted hooks are required.
Support is best effort and no response-time commitment is made.

## Security posture

Adaptive Codex Orchestrator is a local, offline control and policy layer. It
does not change the parent model, reasoning setting, permissions, approvals,
sandbox, or Codex global configuration, and it does not make model-generated
code safe by itself.

Key controls include deterministic command parsing; no prompt, transcript, or
source persistence; schema-versioned plugin-owned state; atomic replacement;
best-effort locking and user-only permissions; hashed project identity; Git
discovery with an argument array, `shell=False`, captured output, and a short
timeout; and bounded optional delegation with parent-owned integration and
final review.

Invalid JSON, unknown events, unsupported state, and unavailable storage fail
closed for plugin functionality while ordinary Codex work continues. Hooks do
not approve tools, elevate privileges, or interpolate prompt text into shell
commands.

The plugin cannot protect a compromised host, operating-system account, Python
runtime, Git executable, or plugin package. It cannot verify the Ultra setting
or guarantee the correctness, security, availability, or model identity of
generated work.

Review the full [security and threat model](plugins/adaptive-codex-orchestrator/docs/SECURITY.md)
and [`hooks/runtime.py`](plugins/adaptive-codex-orchestrator/hooks/runtime.py)
before trusting hooks. Translations are listed in the
[five-language index](plugins/adaptive-codex-orchestrator/docs/i18n/README.md).
