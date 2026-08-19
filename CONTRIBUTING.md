# Contributing

Thank you for improving Adaptive Codex Orchestrator. This is an independent
community project and is not affiliated with or endorsed by OpenAI.

Read the full [contribution guide](plugins/adaptive-codex-orchestrator/CONTRIBUTING.md),
[architecture](plugins/adaptive-codex-orchestrator/docs/ARCHITECTURE.md),
[security policy](SECURITY.md), and [privacy policy](PRIVACY.md) before editing.

Contributions must preserve the core boundaries: the parent owns requirements,
architecture, integration, validation, and the final answer; delegation is
optional and bounded; the plugin does not change models, reasoning, approvals,
sandbox, or permissions; runtime state stays under plugin-owned `PLUGIN_DATA`;
and the control plane makes no external request or prompt/source persistence.

Run the unit tests, policy evaluator, package validator, and deterministic
release builder before proposing a change. Never commit credentials, prompts,
transcripts, proprietary source, generated user patches, private fixtures, or
machine-specific absolute paths.

Security issues must use the [private advisory form](https://github.com/battle-doll/adaptive-codex-orchestrator/security/advisories/new),
not a public issue.
