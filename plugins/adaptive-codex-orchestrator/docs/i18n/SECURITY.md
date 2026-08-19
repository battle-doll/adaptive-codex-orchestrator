# Security overview

**English** · [한국어](SECURITY.ko.md) · [日本語](SECURITY.ja.md) ·
[简体中文](SECURITY.zh-CN.md) · [Русский](SECURITY.ru.md)

This is a concise public-review companion to the detailed, authoritative
[Security policy](../SECURITY.md). Adaptive Codex Orchestrator is an
independent community tool, not an official, affiliated, sponsored, or
endorsed OpenAI product.

## Security posture

The plugin is a local, offline control and policy layer. It does not change the
parent model, reasoning setting, permissions, approvals, sandbox, or global
Codex configuration, and it does not make model-generated code safe by itself.
Users must review `hooks/hooks.json` and `hooks/runtime.py` before trusting
hooks, then review generated changes and validation evidence before use.

Key controls include:

- Deterministic, non-LLM command parsing. Prompt text stays in memory for the
  current event and is never stored, logged, evaluated, or inserted into a
  command.
- Invalid JSON, unknown events, unsupported state, and unavailable storage fail
  closed for plugin functionality while normal Codex work continues.
- Schema-versioned state, atomic replacement, best-effort locking, hashed
  project identity, and writes limited to the host-provided `PLUGIN_DATA`.
- Git discovery with an argument array, `shell=False`, captured output, and a
  short timeout. Prompt text is never part of the command.
- Optional, bounded delegation; nested delegation is disabled by default. The
  parent retains security-sensitive decisions, integration, and final review.

The plugin cannot protect a compromised host, operating-system account, Python
runtime, Git executable, or plugin package. It cannot verify the Ultra setting
or guarantee the correctness, security, or availability of model output.

## Reporting a vulnerability

Do not disclose exploit details, credentials, prompts, proprietary source, or
private paths in a public issue. The designated security-reporting candidate is a
[private GitHub advisory](https://github.com/battle-doll/adaptive-codex-orchestrator/security/advisories/new),
which must be enabled and verified before use. If it is unavailable, first ask
the maintainer for a private channel without sharing sensitive details.

Include the affected version, platform and Codex surface, minimal reproduction,
impact, and whether trusted hooks are required. No response-time commitment is
currently made.

Control commands are recognized in Korean and English only. These translations
do not add Japanese, Simplified Chinese, or Russian command support.
