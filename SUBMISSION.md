# Plugin Submission and Reviewer Notes

**English** · [한국어](plugins/adaptive-codex-orchestrator/docs/i18n/SUBMISSION.ko.md) ·
[日本語](plugins/adaptive-codex-orchestrator/docs/i18n/SUBMISSION.ja.md) ·
[简体中文](plugins/adaptive-codex-orchestrator/docs/i18n/SUBMISSION.zh-CN.md) ·
[Русский](plugins/adaptive-codex-orchestrator/docs/i18n/SUBMISSION.ru.md)

Prepared: **2026-08-19**

This document records the review candidate; it does not claim submission,
approval, publication, affiliation, or endorsement. OpenAI approval and the
developer's later **Publish** action are separate states.

## Candidate artifact

- File: `adaptive-codex-orchestrator-0.1.0.zip`
- Files: `88`
- Compressed size: `257,831` bytes
- Uncompressed size: `603,339` bytes
- SHA-256: `5342258177c1dd115f68e52a1e5596146632ed92251dd4d94a132636d63f7b66`

Two independent builds were byte-identical. The SHA-256 sidecar, safe archive
inspection, trusted-source byte comparison, and isolated smoke import passed.

## Listing

- Package: `adaptive-codex-orchestrator`
- Version: `0.1.0`
- Type: skills-only Codex plugin with trusted local lifecycle hooks
- Display name: `Adaptive Codex Orchestrator`
- Subtitle: `Adaptive task orchestration`
- Category: `Developer Tools`
- Developer and publisher: `battle-doll`
- Website: <https://github.com/battle-doll/adaptive-codex-orchestrator>
- Support: <https://github.com/battle-doll/adaptive-codex-orchestrator/blob/main/SUPPORT.md>
- Privacy: <https://github.com/battle-doll/adaptive-codex-orchestrator/blob/main/PRIVACY.md>
- Terms: <https://github.com/battle-doll/adaptive-codex-orchestrator/blob/main/TERMS.md>
- Requested availability: all countries and regions where OpenAI offers the
  applicable plugin and Codex surfaces.

The package has one skill, no MCP server, no OAuth, no API keys, no external
account, no external network dependency, no telemetry, and no custom app UI.
Therefore no UI screenshots or test credentials are supplied.

## Visual assets

- Directory icon, light and dark slots: `assets/logo.png` (`256×256` PNG)
- Composer icon, light and dark slots: `assets/composer-icon.png` (`48×48` PNG)

The same neutral original asset is intentionally reused for both themes. SVG
sources remain in the package.

## Starter prompts

1. `Use Ultra Orchestration to inspect three independent modules without editing, then summarize the evidence.`
2. `Use Ultra Orchestration for this task only: reproduce the parser bug, make the smallest fix, and run focused tests.`
3. `Show the current Ultra Orchestration scope and profile, and explain whether persistent hooks are available.`

These prompts remain useful without claiming that every ChatGPT surface offers
Codex lifecycle hooks. Persistent scopes are tested only where supported and
trusted; otherwise the explicit skill applies to the current task.

## Reviewer setup

Use the deterministic release ZIP, Python 3.9 or newer, and a writable
host-assigned `PLUGIN_DATA` directory. Review and trust the bundled
`hooks/hooks.json` and hook runtime only for persistent-scope tests. When hooks
are unavailable or untrusted, test the explicit `$adaptive-orchestration`
current-task fallback and do not expect persistence.

Exactly five positive and three negative cases, including fixtures and expected
result shapes, are in
[`evals/reviewer-cases.json`](plugins/adaptive-codex-orchestrator/evals/reviewer-cases.json).
The broader deterministic suite contains 31 policy scenarios.

## Initial release notes

Initial skills-only release of Adaptive Codex Orchestrator. It packages one
adaptive orchestration skill and trusted local lifecycle hooks for one-shot,
session, project, and plugin-global profiles. The control plane is offline,
uses plugin-owned local state, and requires no MCP server, OAuth, credentials,
telemetry, or external network access. When hooks are unavailable or untrusted,
explicit skill use applies only to the current request. Reviewers should use a
writable `PLUGIN_DATA` directory and trust the bundled hooks for persistent-mode
tests.

## Reproducibility

The release builder creates a sorted, timestamp-fixed ZIP with one
`adaptive-codex-orchestrator/` root plus a SHA-256 sidecar. The artifact
validator rejects path traversal, portable-name collisions, symlinks, secret-
like filenames, private home paths, unexpected file modes, oversized members,
and source/archive byte mismatches before its trusted isolated smoke test.
