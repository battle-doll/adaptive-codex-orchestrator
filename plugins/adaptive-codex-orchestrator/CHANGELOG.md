# Changelog

All notable changes to Adaptive Codex Orchestrator will be documented here.
The project uses semantic versioning for public releases.

## [Unreleased]

No changes yet.

## [0.1.0] - 2026-08-19

### Added

- Initial two-layer architecture for deterministic local control and parent-led
  execution.
- Offline hook runtime for command parsing, atomic versioned state, hashed
  project identity, lifecycle cleanup, compatibility notices, and compact
  context injection on Windows, macOS, and Linux.
- Korean and English command-language policy for one-shot, session, project,
  and plugin-global scopes.
- Conservative, balanced, and fast delegation profiles with bounded writer and
  retry behavior.
- Central model policy for requesting `gpt-5.3-codex-spark` while keeping
  requested and host-confirmed model identity separate.
- Explorer, Worker, Tester, and generic bounded-worker contracts.
- Original neutral SVG assets, exact 256×256 and 48×48 submission PNGs, a local
  marketplace entry, 31 policy eval scenarios, cross-platform CI, and offline
  package validation.
- Architecture, security, privacy, terms, compatibility, testing, publishing,
  contribution, and five-language public documentation in English, Korean,
  Japanese, Simplified Chinese, and Russian.
- Exactly five positive and three negative reviewer cases with reproducible
  fixtures and expected result shapes.
- A deterministic one-root ZIP builder, SHA-256 sidecar, safe untrusted-archive
  validation, trusted-source comparison, and isolated smoke import.
- MIT license and Python project metadata for the offline standard-library
  control plane.

### Security

- Defined no-network, no-telemetry, no-prompt/source persistence, safe
  subprocess, plugin-owned state, and no-permission-elevation invariants.
- Restricted Korean and English controls to orchestration-specific anchors so
  ordinary application modes and unrelated profile-status requests cannot
  mutate or query orchestration state.
- Added missing-turn one-shot expiry and bounded single-lock cleanup behavior
  for skipped completion hooks and state-lock contention.

### Changed

- Added task-aware worker caps: zero for trivial/direct verification, at most
  one read-only Explorer for local bugs and shared-state/security boundaries,
  and at most two disjoint read-only Explorers for structural mapping, while
  small or obvious four-module maps now default to parent-only to avoid measured
  spawn and integration regressions.
- Replaced eager full-policy injection with a compact active policy, numeric
  per-session revision de-duplication, and delegation-time reference loading.
- Limited every profile to one concurrent writer, one spawn attempt per
  delegated subtask, and parent fallback without host-default substitution.
- Standardized worker results on six evidence-focused fields and made parent
  review use targeted spot checks instead of repeating delegated exploration.

### Notes

- GitHub source availability, OpenAI submission, approval, and the later
  developer-controlled Publish action are separate states. Publication is
  intentionally withheld pending hands-on use and a separate owner decision.
