# Adaptive Codex Orchestrator

Control when Codex delegates bounded work: choose the task, session, project,
or global scope, select a profile, and keep parent review and safe parallel
execution explicit. This package is for developers who want delegation
controls on demand—not automatic multi-agent routing for every task.

> Publication status, verified 2026-08-29: [v0.1.0 is Published](https://chatgpt.com/plugins/plugins_6a86354985fc8191b33d2795e2851821)
> and remote-catalog `GLOBAL` / `AVAILABLE` / `UNLISTED`. The first publication
> date is unknown. v0.1.1 is an unsubmitted update candidate; see the
> repository [submission notes](../../SUBMISSION.md).

## Install or use

- Open the exact [published v0.1.0 plugin page](https://chatgpt.com/plugins/plugins_6a86354985fc8191b33d2795e2851821).
  `UNLISTED` does not imply directory search or browse placement.
- Review `hooks/hooks.json` and `hooks/runtime.py` before trust, then follow the
  installation instructions below for source-based Codex development.
- This source tree prepares v0.1.1 and is not the published package.

## Try it

```text
Use orchestration for this task only: inspect three independent modules without editing, then summarize the evidence.
오케스트레이션 상태, 범위, 프로필을 알려줘.
```

## Key boundaries

- Explicit controls only: enable, disable, status, scope, profile, or
  `$adaptive-orchestration`; knowing the product name is unnecessary.
- Ordinary parallelizable work and answer-style, mentor-mode, learning, advice,
  brainstorming, or critique requests do not activate this plugin.
- The parent retains requirements, architecture, integration, validation, and
  the final answer, with at most one concurrent writer.
- No change to the selected parent model or reasoning level, permissions,
  approvals, sandbox, or network; no prompt, transcript, source-code, or
  raw-path persistence. Worker model requests follow the bundled policy.

> Independent community project. Adaptive Codex Orchestrator is not affiliated
> with, endorsed by, or an official product of OpenAI.

The latest offline results are recorded in
[Validation](docs/VALIDATION.md).

## English

### Overview

The plugin has two layers:

- A deterministic, standard-library Python control plane parses commands,
  resolves state, protects project identity, and emits hook context.
- The active parent model is the execution plane. It decides whether
  delegation is worthwhile, creates bounded contracts, reviews every result,
  integrates changes, validates the outcome, and answers the user.

See [Architecture](docs/ARCHITECTURE.md) for the state schema, hook lifecycle,
trust boundaries, and delegation sequence.

### Why this plugin exists

Fast delegated workers can reduce latency and parent-context load for narrow,
independent work. They are less suitable for ambiguous requirements, broad
architecture, security-sensitive judgment, or tightly coupled writes. Ultra
Orchestration makes that boundary explicit without replacing the parent with a
fixed workflow engine.

### What it does

- Recognizes deterministic Korean and English enable, disable, status, scope,
  and profile commands.
- Supports one-shot, session, project, and plugin-global preferences.
- Injects a compact active policy only while the mode is active. A numeric
  per-session policy revision suppresses repeated delivery on ordinary turns.
- Prefers bounded, reversible, independently verifiable work for delegation.
- Limits worker and writer concurrency by profile.
- Provides `$adaptive-orchestration <task>` as a current-task fallback.
- Stores project preferences under a one-way project hash, not a raw path.

### What it does not do

- It does not change the selected parent model or reasoning level.
- It does not verify that Ultra reasoning is active.
- It does not rewrite subagent tool calls or silently route models.
- It does not auto-approve tools, change the sandbox, or elevate permissions.
- It does not modify Codex global configuration or a project when mode state is
  toggled.
- It does not guarantee that Spark is available or claim Spark ran without
  host evidence.
- It does not send telemetry, prompts, source code, or state over a network.

### Supported surfaces

This is a Codex-first plugin. The checked plugin packaging surfaces include
ChatGPT web/desktop/mobile and the Codex app/CLI, while the persistent hook
contract used here is specific to the Codex lifecycle. The Codex IDE extension
does not support plugins in the checked contract. Persistent natural-language
controls require a Codex surface that supports this package's events and lets
the user trust its hooks. The explicit skill remains useful when hooks are
unavailable or untrusted. Do not assume that a general ChatGPT conversation or
every Codex host exposes local hooks, session cleanup, parent-model identity,
or subagent-model identity. See
[Compatibility](docs/COMPATIBILITY.md) for the current support contract.

### Required parent-model selection

For the intended experience, manually select Sol with the Ultra reasoning or
intelligence setting before activation. The plugin never changes the selector
and cannot reliably verify the Ultra setting. If a reliable parent identifier
is absent or does not appear to be Sol, the mode remains usable in
compatibility mode and issues at most one notice per session.

### Installation

The public-review source is planned at
`https://github.com/battle-doll/adaptive-codex-orchestrator`. Review
`.codex-plugin/plugin.json`, `hooks/hooks.json`, and `hooks/runtime.py` before
installation. With that marketplace source available, install with:

```text
codex plugin marketplace add battle-doll/adaptive-codex-orchestrator --ref main
codex plugin add adaptive-codex-orchestrator@adaptive-codex-orchestrator
```

Use the current Codex plugin workflow and review the host's hook-trust prompt.

For this repository's configured local marketplace, install with its declared
name:

```text
codex plugin add adaptive-codex-orchestrator@adaptive-codex-orchestrator
```

Start a new Codex task after installation or reinstallation so that the host
can load the current skill and hook definitions.

### Local marketplace installation

The repository marketplace is a non-default local marketplace. If it has not
already been configured, add the repository root (the directory containing
`.agents/plugins/marketplace.json`), then install the plugin using the
marketplace's actual `name` value:

```text
codex plugin marketplace add <absolute-repository-root>
codex plugin add adaptive-codex-orchestrator@adaptive-codex-orchestrator
```

The default personal marketplace at the platform-equivalent of
`~/.agents/plugins/marketplace.json` is discovered implicitly and must not be
added with `codex plugin marketplace add`. Do not hand-edit Codex global
configuration as part of installation.

### Hook review and trust

Hooks execute local code with the permissions already granted to the Codex
host. Review the hook configuration and runtime before trusting them. Trust
does not grant extra permissions: this plugin must not approve tools, alter
the sandbox, or raise privileges. If hooks are skipped, use the explicit
one-shot skill and do not expect persistent natural-language state.

### Natural-language commands

| Purpose | Korean | English |
| --- | --- | --- |
| Session enable | `솔 울트라 모드 켜줘` | `Turn on Ultra Orchestration for this session.` |
| One-shot enable | `이번 작업만 솔 울트라 모드 켜줘` | `Use Ultra Orchestration for this task only.` |
| Project enable | `이 프로젝트에서는 솔 울트라 모드를 항상 켜줘` | `Enable Ultra Orchestration for this repository.` |
| Global enable | `모든 프로젝트에서 기본으로 켜줘` | `Enable Ultra Orchestration globally.` |
| Disable | `솔 울트라 모드 꺼줘` | `Turn off Ultra Orchestration.` |
| Profile | `빠른 프로필로 전환해` | `Switch to the fast profile.` |
| Status | `오케스트레이션 상태 알려줘` | `Show orchestration status.` |

Status has priority over activation-like wording and never changes state.
Explicit negation is a disable. Ambiguous, conflicting, quoted, fenced-code,
or merely incidental examples preserve state. A mixed control command and
coding task takes effect in the same request.

### Scopes

Effective precedence is:

```text
one-shot > session > project > global > disabled
```

- `one-shot` lasts for the current request and is cleared at completion.
- `session` lasts until that session ends; inactive records older than 30 days
  are also removed on a later `SessionStart` when the host missed cleanup.
- `project` persists for the hashed repository or working-directory identity.
- `global` is a plugin-owned default under `PLUGIN_DATA`; it is not Codex
  global configuration.

A generic disable writes a session-level OFF override. It does not erase a
project or global preference.

### Policy delivery

An active `SessionStart` (including `source: compact`), a new enable, or an
active profile change delivers the compact policy. On an ordinary active turn,
the same policy revision is omitted after its numeric `active_policy_revision`
marker has been stored for that session. If the advisory marker cannot be
written, the compact policy may appear again. Detailed routing, worker, and
model references are not injected repeatedly; the parent loads them once only
after choosing at least one real delegated task.

### Profiles

| Profile | Worker ceiling per parent turn | Concurrent writers | Spawn attempts per delegated subtask | Delegated retries |
| --- | ---: | ---: | ---: | ---: |
| `conservative` | 2 | 1 | 1 | 0 |
| `balanced` (default) | 4 | 1 | 1 | 0 |
| `fast` | 6 | 1 | 1 | 0 |

These are ceilings, not worker targets. The effective cap is the minimum of the
profile ceiling, any lower host or explicit user cap, the independently useful
task count, and the task-specific safety cap. Direct execution uses zero
workers for trivial or clear single-file edits and for checking an unsupported
completion claim. A local reproducible bug defaults to zero and may use one
read-only Explorer only when independent evidence materially helps. Four small
or obvious module-test pairs also default to zero; use at most two disjoint
read-only Explorers only when each slice needs substantial independent evidence
and the expected saving clearly exceeds spawn and integration cost. Shared-
state, authentication, authorization, permission, or tenant work may use at
most one read-only Explorer, with the parent as the only writer. Every profile
has a hard limit of one concurrent writer.

### Spark routing behavior

The parent may request `gpt-5.3-codex-spark` with medium reasoning effort for
bounded text work such as file discovery, limited flow tracing, focused failure
analysis, a narrow confirmed change, focused tests, mechanical refactoring, or
targeted validation. Architecture, ambiguous root cause, public API and major
dependency changes, authentication/authorization/cryptography, migrations,
destructive work, complex concurrency, integration, and final validation stay
with the parent.

Delegation is optional. The parent works directly when orchestration overhead
is greater than the expected benefit. Nested delegation is forbidden without
exception. Detailed routing, worker-contract, and model references are loaded
once only after the compact gate selects an actual delegated task. Each
delegated subtask gets one Spark spawn attempt. A missing, unsupported, rate-
limited, or failed request returns that subtask to the parent without retry or
host-default substitution.

The configured model and reasoning effort are requested settings, not proof of
the worker that ran. Any host-reported active model remains a separate,
start-time fact and is not completion or billing attestation. Every worker must
return exactly these six top-level fields and no others: `conclusion`,
`evidence`, `files_and_lines`, `tests_or_checks`, `risks`, and
`recommended_parent_action`. The parent reviews every result, may spot-check
cited evidence and investigate gaps or conflicts, and must not repeat the same
broad delegated exploration end to end.

### One-shot skill fallback

Use the explicit skill when persistent hooks are unavailable or untrusted:

```text
$adaptive-orchestration Analyze this repository's authentication failure,
identify the minimal fix, implement it, and validate it.
```

This applies policy to the current task only. It does not persist state or
claim session, project, or global activation.

### Status output

A status request reports facts equivalent to:

```text
Ultra Orchestration: ON
Effective scope: project
State source: project
Profile: balanced
Configured worker: gpt-5.3-codex-spark
Parent model detected: <model or unavailable>
Ultra reasoning verified: no
Persistent hooks trusted: <yes, no, or unknown>
Compatibility mode: <yes or no>
```

After delegation, summaries list only workers actually created and distinguish
the requested model from a host-confirmed model.

### Security

The hook runtime is local, standard-library code. It uses `shell=False` for
Git discovery, never evaluates prompt text, and contains no approval, sandbox,
or privilege-escalation path. Review the complete threat model in
[Security](docs/SECURITY.md).

### Privacy

The plugin collects no telemetry and makes no external network requests. Its
state contains mode/profile preferences, hashed project keys, session keys,
and lifecycle flags. It does not persist prompts, transcripts, source code,
repository names, or absolute project paths. See [Privacy](docs/PRIVACY.md).

### State reset

Close affected Codex sessions, identify the exact plugin-owned `PLUGIN_DATA`
directory supplied by the host, verify that it is neither the repository nor a
home/configuration root, and delete only that plugin-owned directory (or only
`state-v1.json` if retaining diagnostic backups). Never recursively delete the
parent data directory. The next trusted hook invocation recreates empty state.

### Troubleshooting

- **Mode does not persist:** hooks may be unavailable, untrusted, or unable to
  write `PLUGIN_DATA`; use the explicit skill and inspect the relevant control
  diagnostic.
- **Compatibility notice appears:** manually confirm the intended parent model;
  the plugin does not change it.
- **Spark is not confirmed:** the host may omit worker model identity. Treat the
  worker as generic and keep requested and confirmed models separate.
- **Git is unavailable:** project state falls back to a hash of the normalized
  working directory.
- **State is malformed/read-only:** normal Codex behavior continues; readable
  damaged state is preserved before recovery when storage permits.

### Known limitations

- Ultra reasoning cannot be verified.
- Model slugs and availability are host-controlled and may change.
- Persistent control depends on supported, trusted hooks and reliable lifecycle
  events.
- Some hosts do not expose parent or worker model identity.
- General ChatGPT surfaces do not inherit the Codex hook guarantee, and the
  checked Codex IDE extension contract does not support plugins.
- `SessionEnd` is advisory and may be delayed; stale state also needs bounded
  lifecycle cleanup rather than relying only on immediate session closure.
- File locking and user-only permissions are best-effort and platform-specific.

### Public-submission status

Publisher metadata, public support/privacy/terms destinations, exact PNG assets,
five positive and three negative reviewer cases, and a deterministic release
archive are prepared. This skills-only plugin has no custom UI, so UI
screenshots are not applicable. Submission for OpenAI review is separate from
approval, and approval does not publish the plugin; the developer-controlled
Publish action remains withheld pending hands-on use. See
[Publishing](docs/PUBLISHING.md).

### Non-affiliation disclaimer

OpenAI, ChatGPT, Codex, Sol, and Spark are names associated with their
respective owner. Their appearance here identifies compatible or requested
host capabilities only. Adaptive Codex Orchestrator is independently created
and is not affiliated with or endorsed by OpenAI.

### Project documents

- [Architecture](docs/ARCHITECTURE.md)
- [Security](docs/SECURITY.md)
- [Privacy](docs/PRIVACY.md)
- [Terms](docs/TERMS.md)
- [Compatibility](docs/COMPATIBILITY.md)
- [Testing](docs/TESTING.md)
- [Publishing](docs/PUBLISHING.md)
- [Contributing](CONTRIBUTING.md)
- [Changelog](CHANGELOG.md)
- [MIT License](LICENSE)

## 한국어

### 개요

Adaptive Codex Orchestrator는 Codex 중심의 오프라인 오케스트레이션
하네스입니다. 표준 라이브러리 Python 제어 계층이 한국어·영어 명령,
상태, 프로젝트 식별자, 훅 컨텍스트를 결정론적으로 처리하고, 실제 실행
판단은 사용자가 선택한 부모 모델이 담당합니다. 부모는 요구사항, 설계,
위임 여부, 결과 검토, 통합, 최종 검증과 답변에 계속 책임을 집니다.

상태 스키마와 훅 흐름은 [아키텍처 문서](docs/ARCHITECTURE.md)에 있습니다.

### 이 플러그인이 필요한 이유

빠른 작업자는 범위가 좁고 서로 독립적인 조사·수정에서 지연 시간과 부모
컨텍스트 부담을 줄일 수 있습니다. 반면 모호한 요구사항, 큰 설계,
보안 판단, 겹치는 쓰기 작업에는 적합하지 않습니다. Ultra Orchestration은
고정된 워크플로 엔진을 강제하지 않고 이 경계를 명시합니다.

### 하는 일

- 한국어·영어 활성화, 비활성화, 상태, 범위, 프로필 명령을 결정론적으로
  인식합니다.
- 한 번, 세션, 프로젝트, 플러그인 전체 기본 범위를 지원합니다.
- 모드가 켜진 동안에만 간결한 활성 정책을 주입하며, 세션별 숫자형 정책
  revision으로 일반 턴의 동일 정책 반복 주입을 막습니다.
- 범위가 명확하고 되돌릴 수 있으며 독립 검증 가능한 작업만 위임 후보로
  삼습니다.
- 프로필별 작업자·쓰기 동시 실행 수를 제한합니다.
- 훅이 없거나 신뢰되지 않을 때 `$adaptive-orchestration <task>`를 제공합니다.
- 원본 경로 대신 단방향 프로젝트 해시에 설정을 연결합니다.

### 하지 않는 일

- 부모 모델, 추론 수준, 모델 선택기를 바꾸지 않습니다.
- Ultra 추론이 활성화되었다고 검증하거나 주장하지 않습니다.
- 서브에이전트 호출을 몰래 재작성하거나 모델을 강제 라우팅하지 않습니다.
- 도구를 자동 승인하거나 샌드박스·권한을 변경하지 않습니다.
- 모드 전환만으로 Codex 전체 설정이나 사용자 프로젝트를 수정하지 않습니다.
- 호스트 확인 없이 Spark 사용을 주장하지 않습니다.
- 네트워크로 텔레메트리, 프롬프트, 소스 코드, 상태를 보내지 않습니다.

### 지원 표면

이 패키지는 Codex 우선 플러그인입니다. 확인된 플러그인 패키징 표면은
ChatGPT 웹·데스크톱·모바일과 Codex 앱·CLI이지만, 여기서 사용하는 영구 훅
계약은 Codex 생명주기 전용입니다. 확인된 Codex IDE 확장은 플러그인을
지원하지 않습니다. 영구 자연어 제어에는 현재 이벤트를 지원하고 사용자가
훅을 신뢰한 Codex 표면이 필요합니다. 훅이 없거나 신뢰되지 않으면 명시적
한 번 실행 스킬을 사용할 수 있습니다. 일반 ChatGPT 대화나 모든 Codex
호스트가 로컬 훅·모델 식별자를 제공한다고 가정하지 않습니다. 자세한 내용은
[호환성 문서](docs/COMPATIBILITY.md)를 참고하세요.

### 필요한 부모 모델 선택

의도한 동작을 위해 사용자가 실행 전에 Sol과 Ultra 추론/지능 설정을 직접
선택해야 합니다. 플러그인은 선택기를 변경하지 않으며 Ultra 설정을
신뢰성 있게 검증할 수 없습니다. 부모 식별자가 없거나 Sol로 확인되지
않아도 실행을 차단하지 않고 호환 모드로 동작하며, 안내는 세션당 최대 한
번만 표시합니다.

### 설치

공개 심사용 소스는
`https://github.com/battle-doll/adaptive-codex-orchestrator`에 둘 예정입니다.
설치 전에 `.codex-plugin/plugin.json`, `hooks/hooks.json`, `hooks/runtime.py`를
검토하세요. 공개 소스가 준비되면 다음과 같이 설치할 수 있습니다.

```text
codex plugin marketplace add battle-doll/adaptive-codex-orchestrator --ref main
codex plugin add adaptive-codex-orchestrator@adaptive-codex-orchestrator
```

대상 호스트의 현재 플러그인 설치 절차와 훅 신뢰 안내를 확인해야 합니다.

구성된 로컬 마켓플레이스가 있다면 실제 마켓플레이스 이름으로 설치합니다.

```text
codex plugin add adaptive-codex-orchestrator@adaptive-codex-orchestrator
```

설치 또는 재설치 뒤에는 새 Codex 작업에서 시험해 최신 스킬과 훅 정의가
로드되게 하세요.

### 로컬 마켓플레이스 설치

저장소의 `.agents/plugins/marketplace.json`은 기본 개인 마켓플레이스가
아닌 로컬 마켓플레이스입니다. 아직 등록되지 않았다면 저장소 루트를
등록하고 파일의 실제 `name` 값으로 설치합니다.

```text
codex plugin marketplace add <absolute-repository-root>
codex plugin add adaptive-codex-orchestrator@adaptive-codex-orchestrator
```

플랫폼별 `~/.agents/plugins/marketplace.json` 위치의 기본 개인
마켓플레이스는 자동 발견되므로 `marketplace add`를 실행하지 않습니다.
설치를 위해 Codex 전체 설정을 직접 수정하지 마세요.

### 훅 검토와 신뢰

훅은 Codex 호스트에 이미 부여된 권한으로 로컬 코드를 실행합니다. 신뢰하기
전에 설정과 런타임을 검토하세요. 신뢰해도 추가 권한이 생기지 않으며, 이
플러그인은 도구 승인·샌드박스·권한을 변경해서는 안 됩니다. 훅이 생략되면
명시적 한 번 실행 스킬을 사용하고 영구 자연어 상태를 기대하지 마세요.

### 자연어 명령

위 영문 절의 명령 표에 있는 한국어·영어 표현을 모두 지원 대상으로 합니다.
상태 질문은 활성화처럼 보이는 단어보다 우선하며 상태를 바꾸지 않습니다.
명시적 부정은 비활성화입니다. 상충하거나 모호한 명령, 인용문, 코드 블록,
긴 글 속 우연한 예시는 상태를 바꾸지 않습니다. 제어 명령과 실제 작업이
섞인 요청은 같은 요청에 새 상태를 적용합니다.

### 범위

유효 상태 우선순위는 다음과 같습니다.

```text
one-shot > session > project > global > disabled
```

- `one-shot`: 현재 요청 완료 시 제거됩니다.
- `session`: 현재 세션 종료 시 제거되며, 호스트가 정리를 놓친 경우 30일 넘게
  비활성인 항목은 이후의 안전한 상태 접근에서 제거됩니다.
- `project`: 해시된 저장소 또는 작업 디렉터리 식별자에 영구 저장됩니다.
- `global`: `PLUGIN_DATA` 아래의 플러그인 전용 기본값이며 Codex 전체 설정이
  아닙니다.

범위를 지정하지 않은 비활성화는 세션 OFF 덮어쓰기를 만들며 프로젝트나
전체 기본값을 지우지 않습니다.

### 정책 전달

활성 상태의 `SessionStart`(`source: compact` 포함), 새 활성화, 활성 프로필
변경에서는 간결한 정책을 전달합니다. 일반 활성 턴에서는 해당 세션에 같은
숫자형 `active_policy_revision` marker가 저장된 뒤 동일 revision을 다시
전달하지 않습니다. 이 보조 marker를 저장할 수 없으면 간결한 정책이 다시
나올 수 있습니다. 상세 routing, worker, model reference는 반복 주입하지 않고
부모가 실제 위임 작업을 하나 이상 선택한 뒤 한 번만 읽습니다.

### 프로필

기본값은 `balanced`입니다. 부모 턴당 프로필 상한은 `conservative` 2명,
`balanced` 4명, `fast` 6명이지만 작업자 목표 수가 아닙니다. 실제 상한은
프로필, 더 낮은 호스트·사용자 상한, 독립적으로 유용한 작업 수, 작업별 안전
상한의 최솟값입니다. 사소하거나 명확한 단일 파일 수정 및 근거 없는 완료
주장 검증은 0명입니다. 로컬에서 재현되는 버그도 기본 0명이며 독립 증거가
실질적으로 도움 될 때만 읽기 전용 Explorer 1명을 쓸 수 있습니다. 작고
명확한 독립 모듈-테스트 4쌍도 기본 0명입니다. 각 슬라이스에 상당한 독립
증거가 필요하고 예상 절감이 spawn·통합 비용을 명확히 넘을 때만 서로 분리된
읽기 전용 Explorer 최대 2명을 씁니다. 공유 상태·인증·인가·권한·tenant
작업은 읽기 전용 Explorer 최대 1명이고 부모만 작성합니다. 모든
프로필에서 동시 작성자는 최대 1명이며, 위임할 각 하위 작업의 spawn 시도는
1회, 재시도는 0회입니다.

### Spark 라우팅 동작

부모는 파일 탐색, 제한된 흐름 추적, 집중된 오류 분석, 확인된 작은 수정,
집중 테스트, 기계적 리팩터링, 대상 검증처럼 경계가 명확한 텍스트 작업에
`gpt-5.3-codex-spark`와 중간 추론 수준을 요청할 수 있습니다. 설계,
모호한 원인 판단, 공개 API·주요 의존성, 인증·인가·암호화, 마이그레이션,
파괴적 작업, 복잡한 동시성, 통합과 최종 검증은 부모가 담당합니다.

위임은 선택 사항입니다. 비용이 이득보다 크면 부모가 직접 처리합니다.
중첩 위임은 예외 없이 금지됩니다. 간결한 gate가 실제 위임 작업을 고른 뒤에만
상세 routing, worker-contract, model reference를 한 번 읽습니다. 각 위임
하위 작업은 Spark spawn을 한 번만 시도하며, 시작 실패·미지원·속도 제한이면
재시도나 host-default 대체 없이 부모가 해당 작업을 이어받습니다.

설정된 모델과 추론 수준은 요청값일 뿐 실제 실행 증거가 아닙니다. 호스트가
보고한 활성 모델은 별도의 시작 시점 사실이며 완료 또는 billing 증명이
아닙니다. 작업자 결과는 정확히 `conclusion`, `evidence`, `files_and_lines`,
`tests_or_checks`, `risks`, `recommended_parent_action` 여섯 top-level field만
반환합니다. 부모는 모든 결과를 검토하고 인용 증거와 빈틈·충돌을 표적
확인할 수 있지만, 같은 광범위 탐색을 처음부터 끝까지 중복하지 않습니다.

### 한 번 실행 스킬 대안

훅을 사용할 수 없거나 신뢰하지 않을 때 다음처럼 명시적으로 호출합니다.

```text
$adaptive-orchestration 이 저장소의 인증 실패를 분석하고,
최소 수정으로 해결한 뒤 검증해줘.
```

현재 작업에만 정책을 적용하며 세션·프로젝트·전체 활성화를 저장하거나
성공했다고 주장하지 않습니다.

### 상태 출력

상태 요청은 ON/OFF, 유효 범위, 상태 출처, 프로필, 설정된 작업자, 감지된
부모 모델, `Ultra reasoning verified: no`, 영구 훅 신뢰 상태, 호환 모드를
사실대로 보여 줍니다. 실제로 만든 작업자만 보고하고, 요청한 모델과
호스트가 확인한 모델을 구분합니다.

### 보안

훅 런타임은 로컬 표준 라이브러리 코드입니다. Git 탐색은 `shell=False`를
사용하고 프롬프트를 코드로 평가하지 않으며 도구 승인·샌드박스·권한 상승
경로가 없습니다. 자세한 위협 모델은 [보안 문서](docs/SECURITY.md)에
있습니다.

### 개인정보

외부 네트워크 요청이나 텔레메트리가 없습니다. 상태에는 모드·프로필,
해시된 프로젝트 키, 세션 키, 생명주기 플래그만 들어갑니다. 프롬프트,
대화 기록, 소스 코드, 저장소 이름, 절대 경로는 저장하지 않습니다.
[개인정보 문서](docs/PRIVACY.md)를 참고하세요.

### 상태 초기화

해당 Codex 세션을 닫고 호스트가 제공한 정확한 플러그인 전용
`PLUGIN_DATA` 경로를 확인하세요. 그 경로가 저장소·홈·설정 루트가 아님을
검증한 뒤 해당 플러그인 전용 디렉터리만 삭제합니다. 진단 백업을 남기려면
`state-v1.json`만 삭제할 수 있습니다. 상위 데이터 디렉터리를 재귀적으로
삭제하지 마세요. 다음 신뢰된 훅 실행 시 빈 상태가 다시 만들어집니다.

### 문제 해결

- 상태가 유지되지 않으면 훅 지원·신뢰·`PLUGIN_DATA` 쓰기 가능 여부를
  확인하고 명시적 스킬을 사용하세요.
- 호환 안내가 나오면 의도한 부모 모델을 사용자가 직접 확인하세요.
- Spark가 확인되지 않으면 일반 경계 작업자로 취급하고 요청 모델과 확인
  모델을 구분하세요.
- Git을 사용할 수 없으면 정규화된 현재 작업 디렉터리의 해시를 사용합니다.
- 상태가 손상되거나 읽기 전용이어도 일반 Codex 동작은 계속됩니다.

### 알려진 제한

- Ultra 추론은 검증할 수 없습니다.
- 모델 슬러그와 사용 가능 여부는 호스트가 관리하며 바뀔 수 있습니다.
- 영구 제어는 지원되고 신뢰된 훅과 신뢰성 있는 생명주기 이벤트에 의존합니다.
- 일부 호스트는 부모 또는 작업자 모델 식별자를 제공하지 않습니다.
- 일반 ChatGPT 표면에는 Codex 훅 보장이 적용되지 않으며, 확인된 Codex IDE
  확장은 플러그인을 지원하지 않습니다.
- `SessionEnd`는 advisory 이벤트이며 지연될 수 있으므로 즉시 세션 종료에만
  의존하지 않는 제한된 생명주기 정리가 필요합니다.
- 파일 잠금과 사용자 전용 권한은 플랫폼별 최선 노력입니다.

### 공개 제출 상태

게시자 메타데이터, 공개 지원·개인정보·약관 위치, 정확한 PNG 자산, 심사용
positive 5개와 negative 3개 사례, 결정론적 릴리스 ZIP을 준비했습니다. 이
skills-only 플러그인은 사용자 UI가 없으므로 UI 스크린샷 대상이 아닙니다.
OpenAI 심사 제출과 승인은 별개이며, 승인되어도 자동 게시되지 않습니다.
직접 사용해 보기 전까지 개발자 전용 Publish 작업은 보류합니다.
[게시 준비 문서](docs/PUBLISHING.md)를 참고하세요.

### 비제휴 고지

OpenAI, ChatGPT, Codex, Sol, Spark 명칭은 호환 대상 또는 요청할 수 있는
호스트 기능을 식별하기 위해서만 사용됩니다. Adaptive Codex Orchestrator는
독립적으로 만든 커뮤니티 도구이며 OpenAI와 제휴하거나 보증받은 제품이
아닙니다.

### 프로젝트 문서

영문 절의 프로젝트 문서 목록에서 아키텍처, 보안, 개인정보, 약관, 호환성,
테스트, 게시 준비, 기여, 변경 기록, MIT 라이선스를 확인할 수 있습니다.
