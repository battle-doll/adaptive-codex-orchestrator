# Changelog

All notable changes to Adaptive Codex Orchestrator are recorded in the
[plugin changelog](plugins/adaptive-codex-orchestrator/CHANGELOG.md).

## [0.1.1] - Unreleased

- Reframed manifest, skill, and agent metadata around explicit Korean and
  English orchestration controls rather than tasks that merely look
  parallelizable.
- Added clear non-goals for ordinary work, answer-style controls, mentor mode,
  learning, advice, brainstorming, and critique without changing the runtime
  parser, delegation policy, permissions, privacy, networking, or
  determinism.
- Reworked the five-language README openings around the user problem, target
  audience, install/use path, starter commands, and key boundaries.
- Added a validated discovery golden set with 10 direct, 20 indirect, and 20
  negative Korean/English cases, including Premilume/no-plugin boundaries.
- Synchronized v0.1.1 update-candidate version surfaces while preserving the
  immutable v0.1.0 artifact and checksum.

Verified on 2026-08-29: v0.1.0 is Published in OpenAI Platform; the remote
catalog records `GLOBAL` / `AVAILABLE` and discoverability `UNLISTED` at
<https://chatgpt.com/plugins/plugins_6a86354985fc8191b33d2795e2851821>.
v0.1.1 is an unsubmitted update candidate. No LISTED status, review outcome,
publication, or performance improvement is claimed.

## [0.1.0] - 2026-08-19

- Initial deterministic local orchestration control plane and parent-led
  execution policy.
- Korean and English control commands with one-shot, session, project, and
  plugin-global scopes and three bounded delegation profiles.
- Offline trusted hooks, hashed project identity, atomic versioned state,
  compatibility reporting, lifecycle cleanup, and explicit skill fallback.
- Cross-platform tests, 31 policy scenarios, five positive plus three negative
  reviewer cases, public policies, and five-language documentation.
- Exact submission PNGs and deterministic ZIP/SHA-256 release tooling.

The statements above record the source-release state on 2026-08-19. Later
publication status is recorded in the v0.1.1 section without changing the
historical v0.1.0 artifact.
