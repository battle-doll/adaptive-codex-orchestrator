# Adaptive Codex Orchestrator

**English** · [한국어](README.ko.md) · [日本語](README.ja.md) ·
[简体中文](README.zh-CN.md) · [Русский](README.ru.md)

> Independent community project. Adaptive Codex Orchestrator is not
> affiliated with, endorsed by, or an official product of OpenAI.

Adaptive Codex Orchestrator is a Codex-focused, offline plugin that adds a
deterministic control plane for optional, bounded task orchestration. It keeps
requirements, architecture, integration, validation, and the final answer
with the selected parent model while allowing narrow independent work to be
delegated when that is genuinely useful.

This repository is the public-review source for version `0.1.0`. A GitHub
release, review submission, approval, and publication are separate states;
none should be inferred from the repository being public.

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
