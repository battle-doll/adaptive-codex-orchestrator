# Plugin Submission and Reviewer Notes

**English** · [한국어](plugins/adaptive-codex-orchestrator/docs/i18n/SUBMISSION.ko.md) ·
[日本語](plugins/adaptive-codex-orchestrator/docs/i18n/SUBMISSION.ja.md) ·
[简体中文](plugins/adaptive-codex-orchestrator/docs/i18n/SUBMISSION.zh-CN.md) ·
[Русский](plugins/adaptive-codex-orchestrator/docs/i18n/SUBMISSION.ru.md)

Prepared: **2026-08-29**

Verified on 2026-08-29: v0.1.0 is **Published** in OpenAI Platform. The remote
catalog records `GLOBAL` / `AVAILABLE` with discoverability `UNLISTED` at
<https://chatgpt.com/plugins/plugins_6a86354985fc8191b33d2795e2851821>.
The first publication date is unknown. `UNLISTED` is not a claim of directory
search or browse placement. OpenAI's publication workflow is documented at
<https://developers.openai.com/plugins/deploy/submission>.

Version v0.1.1 is an **unsubmitted update candidate**. This document does not
claim submission, approval, publication, LISTED discoverability, affiliation,
endorsement, or improved performance for that update.

## Immutable published v0.1.0 artifact record

- File: `adaptive-codex-orchestrator-0.1.0.zip`
- Files: `88`
- Compressed size: `257,916` bytes
- Uncompressed size: `603,482` bytes
- SHA-256: `62e2332439ed43ba5792c415902c838f9bedc19052bcf6acd21a3f49260b79f1`

Two independent builds were byte-identical. The SHA-256 sidecar, safe archive
inspection, trusted-source byte comparison, and isolated smoke import passed.
This artifact and checksum are historical and must not be rebuilt, replaced,
or reused as the v0.1.1 candidate checksum.

## v0.1.1 listing metadata

- Package: `adaptive-codex-orchestrator`
- Version: `0.1.1`
- Type: skills-only Codex plugin with trusted local lifecycle hooks
- Display name: `Adaptive Codex Orchestrator`
- Subtitle: `Explicit bounded orchestration`
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

1. `Use orchestration for this task only: inspect three independent modules without editing, then summarize the evidence.`
2. `이번 작업만 울트라 오케스트레이션을 켜고 파서 버그를 재현한 뒤 최소 수정과 집중 테스트를 해줘.`
3. `Show orchestration status, scope, and profile, and say whether persistent hooks are available.`

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

## Update notes draft

Discovery-focused patch update. It clarifies that explicit Korean or English
orchestration controls—not merely parallelizable work—select the plugin, makes
scope/profile/status examples visible, and adds a 50-case Korean/English
discovery golden set. It does not change the runtime parser, hook behavior,
state schema, delegation policy, permissions, privacy, network behavior, or
deterministic packaging contract. When hooks are unavailable or untrusted,
explicit skill use still applies only to the current request.

## Reproducibility

The release builder creates a sorted, timestamp-fixed ZIP with one
`adaptive-codex-orchestrator/` root plus a SHA-256 sidecar. The artifact
validator rejects path traversal, portable-name collisions, symlinks, secret-
like filenames, private home paths, unexpected file modes, oversized members,
and source/archive byte mismatches before its trusted isolated smoke test.
