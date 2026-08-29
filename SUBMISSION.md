# Plugin v0.1.1 Publication and Reviewer Record

**English** · [한국어](plugins/adaptive-codex-orchestrator/docs/i18n/SUBMISSION.ko.md) ·
[日本語](plugins/adaptive-codex-orchestrator/docs/i18n/SUBMISSION.ja.md) ·
[简体中文](plugins/adaptive-codex-orchestrator/docs/i18n/SUBMISSION.zh-CN.md) ·
[Русский](plugins/adaptive-codex-orchestrator/docs/i18n/SUBMISSION.ru.md)

Prepared: **2026-08-29**

Verified on 2026-08-29: v0.1.1 is **Published** in OpenAI Platform at
<https://chatgpt.com/plugins/plugins_6a86354985fc8191b33d2795e2851821>.
Exact-name search returns one result in the public section, and the current-
version detail page opens successfully. The first publication date and the
remote-catalog discoverability field were not independently established.
OpenAI's publication workflow is documented at
<https://developers.openai.com/plugins/deploy/submission>.

Files inside `plugins/adaptive-codex-orchestrator/` retain their pre-publication
status wording because they are part of the deterministic release tree. This
root record supersedes that wording only for current distribution status; the
packaged bytes remain frozen at the validated v0.1.1 SHA-256 below.

## Immutable published v0.1.0 artifact record

- File: `adaptive-codex-orchestrator-0.1.0.zip`
- Files: `88`
- Compressed size: `257,916` bytes
- Uncompressed size: `603,482` bytes
- SHA-256: `62e2332439ed43ba5792c415902c838f9bedc19052bcf6acd21a3f49260b79f1`

Two independent builds were byte-identical. The SHA-256 sidecar, safe archive
inspection, trusted-source byte comparison, and isolated smoke import passed.
This artifact and checksum are historical and must not be rebuilt, replaced,
or confused with the v0.1.1 checksum.

## Published v0.1.1 artifact record

- File: `adaptive-codex-orchestrator-0.1.1.zip`
- Files: `90`
- Compressed size: `271,636` bytes
- Uncompressed size: `649,837` bytes
- SHA-256: `06b1fe2b4b0b3c39ae14e2027447db37659fd205580e5f9e426dc2d03531c38a`

The builder produced two byte-identical builds. The generated
sidecar, safe archive inspection, trusted-source byte comparison, and isolated
smoke import passed. The accountable publisher confirmed completion of review
and the separate Publish action. A trustworthy portal download or digest was
not available for an independent byte comparison with the uploaded artifact,
and no live-host selector-success rate is inferred from publication.

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
The static `evals/discovery-cases.json` set contains 10 direct, 20 indirect,
and 20 negative Korean/English selection cases. Its validator checks counts,
locale balance, and selection labels; no live-host or human semantic run is
claimed.

## Release notes

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

## Completion evidence and limits

The accountable publisher confirmed v0.1.1 submission, approval, and the
separate Publish action. Exact-name directory search and the current-version
detail page were independently rechecked. The exact portal field selections,
attestation text, first publication date, remote-catalog discoverability field,
portal-upload byte identity, post-publication clean installation, and actual
selector success across the 50 discovery prompts were not independently
retained or measured and must not be reconstructed from this record.
