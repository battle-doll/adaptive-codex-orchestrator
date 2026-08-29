# Adaptive Codex Orchestrator

**English** · [한국어](README.ko.md) · [日本語](README.ja.md) ·
[简体中文](README.zh-CN.md) · [Русский](README.ru.md)

Control when Codex delegates bounded work: choose the task, session, project,
or global scope, select a profile, and keep parent review and safe parallel
execution explicit. Adaptive Codex Orchestrator is for developers who want
delegation controls on demand—not automatic multi-agent routing for every task.

> Publication status, verified 2026-08-29: [v0.1.1 is Published](https://chatgpt.com/plugins/plugins_6a86354985fc8191b33d2795e2851821)
> in OpenAI Platform. Exact-name search returns one result in the public section,
> and the current-version detail page opens successfully. The first publication
> date and remote-catalog discoverability field were not independently established.

## Install or use

- Open the exact [published v0.1.1 plugin page](https://chatgpt.com/plugins/plugins_6a86354985fc8191b33d2795e2851821).
  Exact-name search currently returns one public result.
- Review the local hooks before trust; use the source installation steps below
  for Codex development.
- This branch contains the source intended for published v0.1.1. Packaged files
  retain their pre-publication status wording so the deterministic release tree
  remains byte-identical to SHA-256 `06b1fe2b4b0b3c39ae14e2027447db37659fd205580e5f9e426dc2d03531c38a`;
  this root README is the current distribution-status record. Actual selector
  success across the 50 discovery prompts remains unmeasured.

## Try it

```text
Use orchestration for this task only: inspect three independent modules without editing, then summarize the evidence.
오케스트레이션 상태, 범위, 프로필을 알려줘.
```

## Key boundaries

- Explicit controls only: enable, disable, status, scope, profile, or
  `$adaptive-orchestration`. The product name is not required.
- Do not activate merely because ordinary work could be parallelized or
  delegated. Answer-style, mentor-mode, learning, advice, brainstorming, and
  critique requests are also outside this plugin unless paired with a separate
  explicit orchestration control.
- The parent owns requirements, architecture, integration, validation, and the
  final answer; at most one writer runs concurrently.
- The plugin does not change the selected parent model or reasoning level,
  permissions, approvals, the sandbox, or network access, and stores no
  prompts or source code. Worker model requests follow the bundled policy.

> Independent community project. Adaptive Codex Orchestrator is not
> affiliated with, endorsed by, or an official product of OpenAI.

## What it adds

- Deterministic Korean and English controls for one-shot, session, project,
  and plugin-global scopes.
- Conservative, balanced, and fast profiles with bounded worker and writer
  concurrency.
- A current-task `$adaptive-orchestration <task>` fallback when persistent
  hooks are unavailable or untrusted.
- Local, schema-versioned state under host-provided `PLUGIN_DATA`, with hashed
  project identity and bounded stale-session cleanup.
- Explicit separation between a requested worker model and a model identity
  actually confirmed by the host.

## Safety and privacy boundaries

The plugin does **not** change the selected parent model or reasoning level,
approve tools, alter the sandbox, elevate permissions, modify Codex global
configuration, or silently route every task. Its control-plane code uses only
the Python standard library, makes no external network request, collects no
telemetry, and does not persist prompts, transcripts, source code, or raw
project paths.

Hooks run local code with the permissions already granted to Codex. Review
[`hooks/hooks.json`](plugins/adaptive-codex-orchestrator/hooks/hooks.json) and
[`hooks/runtime.py`](plugins/adaptive-codex-orchestrator/hooks/runtime.py)
before trusting them.

## Install from the public marketplace source

After reviewing the source, add this repository as a Codex plugin marketplace
and install its declared plugin:

```text
codex plugin marketplace add battle-doll/adaptive-codex-orchestrator --ref main
codex plugin add adaptive-codex-orchestrator@adaptive-codex-orchestrator
```

Start a new Codex task after installation or reinstallation so the host can
load the current skill and hook definitions. For a local checkout, replace the
GitHub repository argument with the absolute repository root containing
`.agents/plugins/marketplace.json`.

## Control examples

| Purpose | Korean | English |
| --- | --- | --- |
| Session enable | `솔 울트라 모드 켜줘` | `Turn on Ultra Orchestration for this session.` |
| One-shot enable | `이번 작업만 솔 울트라 모드 켜줘` | `Use Ultra Orchestration for this task only.` |
| Project enable | `이 프로젝트에서는 솔 울트라 모드를 항상 켜줘` | `Enable Ultra Orchestration for this repository.` |
| Disable | `솔 울트라 모드 꺼줘` | `Turn off Ultra Orchestration.` |
| Profile | `빠른 프로필로 전환해` | `Switch to the fast profile.` |
| Status | `오케스트레이션 상태 알려줘` | `Show orchestration status.` |

Control commands are recognized in Korean and English only. The Japanese,
Simplified Chinese, and Russian documentation does not add command-language
support.

## Repository layout

- [`plugins/adaptive-codex-orchestrator`](plugins/adaptive-codex-orchestrator/README.md):
  reviewable plugin root and full technical documentation.
- [`.agents/plugins/marketplace.json`](.agents/plugins/marketplace.json): local
  and GitHub marketplace entry.
- [`.github/workflows/ci.yml`](.github/workflows/ci.yml): cross-platform offline
  validation on Windows, macOS, and Linux.
- [`Final benchmark report`](benchmarks/runs/final-20260819-report/REPORT.html):
  interactive five-language result with the verified metrics and canonical
  report artifact beside it.

## Verify locally

```text
python -m unittest discover -s plugins/adaptive-codex-orchestrator/tests -v
python plugins/adaptive-codex-orchestrator/scripts/evaluate_policies.py
python plugins/adaptive-codex-orchestrator/scripts/validate_package.py --repo-root .
python plugins/adaptive-codex-orchestrator/scripts/build_release.py
```

The release builder emits a deterministic ZIP and SHA-256 sidecar under
`plugins/adaptive-codex-orchestrator/dist/` and validates the archive without
executing untrusted archive code.

## Public documents

- [Support](SUPPORT.md)
- [Security](SECURITY.md)
- [Privacy](PRIVACY.md)
- [Terms](TERMS.md)
- [Submission and reviewer notes](SUBMISSION.md)
- [Five-language document index](plugins/adaptive-codex-orchestrator/docs/i18n/README.md)
- [License](LICENSE)

Publisher and maintainer: [battle-doll](https://github.com/battle-doll).
