# Adaptive Codex Orchestrator

[English](../../README.md) · **한국어** · [日本語](README.ja.md) ·
[简体中文](README.zh-CN.md) · [Русский](README.ru.md)

Codex가 제한된 작업을 언제 위임할지 직접 제어하세요. 작업·세션·프로젝트·전역
범위와 프로필을 고르고, 부모 검토와 안전한 병렬 실행을 명시적으로 유지할 수
있습니다. 모든 작업을 자동 다중 에이전트로 돌리는 도구가 아니라, 필요할 때만
위임 제어를 쓰고 싶은 개발자를 위한 플러그인입니다.

> 게시 상태(2026-08-29 확인): [v0.1.0은 Published](https://chatgpt.com/plugins/plugins_6a86354985fc8191b33d2795e2851821)이며
> 원격 카탈로그는 `GLOBAL` / `AVAILABLE` / `UNLISTED`입니다. 최초 게시 날짜는
> 확인되지 않았습니다. v0.1.1은 아직 제출하지 않은 업데이트 후보입니다.

## 설치 또는 사용

- 정확한 [게시된 v0.1.0 플러그인 페이지](https://chatgpt.com/plugins/plugins_6a86354985fc8191b33d2795e2851821)를
  여세요. `UNLISTED`은 디렉터리 검색·탐색 노출을 뜻하지 않습니다.
- `hooks/hooks.json`과 `hooks/runtime.py`를 검토한 뒤 아래 소스 설치 절차를
  따르세요.
- 이 패키지 소스는 v0.1.1 후보이며 현재 게시된 패키지가 아닙니다.

## 바로 해보기

```text
이번 작업만 울트라 오케스트레이션을 켜고 세 모듈을 수정 없이 조사해 증거를 요약해줘.
오케스트레이션 상태, 범위, 프로필을 알려줘.
```

## 핵심 경계

- 활성화·비활성화·상태·범위·프로필 또는 `$adaptive-orchestration` 같은 명시적
  제어만 대상이며 제품명을 알 필요는 없습니다.
- 일반 병렬화 가능 작업, 답변 방식, 멘토 모드, 학습, 조언, 브레인스토밍,
  비평 요청은 활성화하지 않습니다.
- 요구사항·설계·통합·검증·최종 답변은 부모가 책임지며 동시 작성자는 최대
  한 명입니다.
- 모델·추론·권한·승인·샌드박스·네트워크를 바꾸지 않고 프롬프트·대화·소스·
  원본 경로를 저장하지 않습니다.

> 독립 커뮤니티 프로젝트입니다. Adaptive Codex Orchestrator는 OpenAI와
> 제휴하거나 OpenAI가 후원·보증하는 공식 제품이 아닙니다.

## 하는 일과 하지 않는 일

하는 일:

- 한 번, 세션, 프로젝트, 플러그인 전체 기본 범위의 활성화 상태를
  `${PLUGIN_DATA}/state-v1.json`에 저장합니다.
- 범위가 명확하고 되돌릴 수 있으며 독립 검증 가능한 작업만 위임 후보로
  삼습니다.
- 기본 `balanced` 프로필에서 부모 턴당 작업자 최대 4명, 동시 작성자 1명을
  허용합니다.
- 활성 세션에는 간결한 정책을 전달하고 숫자형
  `active_policy_revision`으로 일반 턴의 같은 revision 반복을 막습니다.
- 원본 프로젝트 경로 대신 정규화된 루트의 SHA-256 해시를 저장합니다.
- 훅을 사용할 수 없을 때 `$adaptive-orchestration <task>` 한 번 실행 대안을
  제공합니다.

하지 않는 일:

- 부모 모델, 추론 수준, 모델 선택기, 권한, 샌드박스 또는 Codex 전체 설정을
  변경하지 않습니다.
- Ultra 추론이 활성화되었다고 검증하거나 주장하지 않습니다.
- 모드가 켜졌다는 이유만으로 작업자를 만들지 않습니다.
- 호스트 확인 없이 `gpt-5.3-codex-spark`가 실제 사용되었다고 주장하지
  않습니다.
- API 키, OAuth, 외부 계정, 텔레메트리 또는 제어 계층의 네트워크 요청을
  요구하지 않습니다.
- 프롬프트, 대화 기록, 소스 코드 또는 원본 절대 프로젝트 경로를 저장하지
  않습니다.

## 지원 표면과 필요한 선택

확인된 대상은 Codex 앱과 CLI입니다. 신뢰된 훅이 있으면 영구 자연어 상태를
사용할 수 있습니다. 일반 ChatGPT 대화가 로컬 Codex 훅, `PLUGIN_DATA`, 동일한
정리 이벤트나 서브에이전트 설정을 제공한다고 가정하지 않습니다. 확인된
계약에서는 Codex IDE 확장의 플러그인 사용을 지원하지 않습니다.

의도한 동작을 위해 사용자가 Sol과 Ultra 추론/지능 설정을 직접 선택해야
합니다. 플러그인은 이를 대신 선택하거나 Ultra 설정을 신뢰성 있게 확인할
수 없습니다. 자세한 내용은 [호환성 문서](../COMPATIBILITY.md)를 참고하세요.

## 로컬 설치

현재 manifest에는 게시자 `battle-doll`과 공개 후보 위치로 지정된
[GitHub 저장소](https://github.com/battle-doll/adaptive-codex-orchestrator),
홈페이지·개인정보·약관 URL이 기록되어 있습니다. 이 지정은 게시 완료를 뜻하지
않으며 사용 또는 제출 전에 각 주소의 접근성과 검토된 내용을 확인해야 합니다. 설치 전에
`.codex-plugin/plugin.json`, `hooks/hooks.json`, `hooks/runtime.py`를 검토하고
훅을 신뢰할지 결정하세요.

저장소 소유자가 실제 `.agents/plugins/marketplace.json` 값을 확인한 뒤 다음
명령을 수동으로 실행합니다. 이 작업은 Codex 상태를 변경하므로 자동으로
수행하지 않습니다.

```text
codex plugin marketplace add <absolute-repository-root>
codex plugin list --marketplace adaptive-codex-orchestrator --available --json
codex plugin add adaptive-codex-orchestrator@adaptive-codex-orchestrator
```

설치 또는 재설치 뒤에는 새 Codex 작업에서 시험하세요. 기본 개인
마켓플레이스는 자동 발견되므로 해당 경로에 `marketplace add`를 실행하지
않습니다.

## 자연어 제어

현재 결정론적 명령 언어는 **한국어와 영어만** 지원합니다. 이 번역 문서가
다른 명령 언어 지원을 의미하지는 않습니다.

| 목적 | 한국어 | 영어 |
| --- | --- | --- |
| 세션 활성화 | `솔 울트라 모드 켜줘` | `Turn on Ultra Orchestration for this session.` |
| 이번 작업만 | `이번 작업만 솔 울트라 모드 켜줘` | `Use Ultra Orchestration for this task only.` |
| 프로젝트 | `이 프로젝트에서는 솔 울트라 모드를 항상 켜줘` | `Enable Ultra Orchestration for this repository.` |
| 전체 기본값 | `모든 프로젝트에서 기본으로 켜줘` | `Enable Ultra Orchestration globally.` |
| 비활성화 | `솔 울트라 모드 꺼줘` | `Turn off Ultra Orchestration.` |
| 프로필 | `빠른 프로필로 전환해` | `Switch to the fast profile.` |
| 상태 | `오케스트레이션 상태 알려줘` | `Show orchestration status.` |

상태 질문은 상태를 바꾸지 않습니다. 명시적 부정, 상충하는 범위·프로필,
인용문, 코드 블록이나 긴 글 속 우연한 예시는 안전하게 처리됩니다. 제어
명령과 실제 작업이 섞인 요청은 같은 턴에 적용됩니다.

## 범위와 프로필

상태 우선순위는 다음과 같습니다.

```text
one-shot > session > project > global > disabled
```

범위 없는 일반 비활성화는 세션 OFF 덮어쓰기를 만들며 프로젝트나 전체
기본값을 지우지 않습니다.

| 프로필 | 부모 턴당 작업자 상한 | 동시 작성자 | 하위 작업당 spawn 시도 | 위임 재시도 |
| --- | ---: | ---: | ---: | ---: |
| `conservative` | 2 | 1 | 1 | 0 |
| `balanced` | 4 | 1 | 1 | 0 |
| `fast` | 6 | 1 | 1 | 0 |

프로필 값은 목표가 아니라 상한입니다. 실제 상한은 프로필, 더 낮은 호스트·
사용자 상한, 독립적으로 유용한 작업 수, 작업별 안전 상한의 최솟값입니다.
사소하거나 명확한 단일 파일 수정과 근거 없는 완료 검증은 0명입니다. 로컬
재현 버그도 기본 0명이고 독립 증거가 실질적으로 도움 될 때만 읽기 전용
Explorer 1명을 쓸 수 있습니다. 작고 명확한 독립 모듈-테스트 4쌍도 기본
0명입니다. 각 슬라이스에 상당한 독립 증거가 필요하고 예상 절감이 spawn·통합
비용을 명확히 넘을 때만 분리된 읽기 전용 Explorer 최대 2명을 씁니다. 공유
상태·인증·인가·권한·tenant 작업은 읽기 전용 Explorer 최대 1명이며 부모만
작성합니다. 모든 프로필의 동시 작성자 상한은 1명입니다.

## 위임 정책

파일·심볼 탐색, 제한된 호출 경로 추적, 집중된 실패 분석, 확인된 작은 수정,
집중 테스트와 기계적 변경처럼 경계가 명확한 텍스트 작업만 빠른 작업자
후보입니다. 설계, 모호한 원인 판단, 인증·인가·암호화, 데이터 마이그레이션,
파괴적 작업, 공개 API·주요 의존성, 복잡한 동시성, 통합과 최종 검증 판단은
부모가 담당합니다.

중첩 위임은 예외 없이 금지됩니다. 간결한 gate가 실제 위임 작업을 고른
뒤에만 상세 routing, worker-contract, model reference를 한 번 읽습니다. 각
하위 작업은 Spark spawn을 한 번만 시도하며 실패·제한·명시적 모델 미지원이면
재시도나 host-default 대체 없이 부모가 이어받습니다. 요청 모델과 추론 수준은
호스트가 확인한 활성 모델과 구분하며, 시작 시점 모델 보고는 완료나 billing
증명이 아닙니다.

모든 작업자는 정확히 `conclusion`, `evidence`, `files_and_lines`,
`tests_or_checks`, `risks`, `recommended_parent_action` 여섯 top-level field만
반환합니다. 부모는 결과를 검토하고 인용 증거·빈틈·충돌을 표적 확인하지만,
같은 광범위 탐색을 처음부터 끝까지 중복하지 않습니다. 실제로 생성된
작업자만 보고합니다.

## 보안, 개인정보와 상태 삭제

제어 계층은 로컬 표준 라이브러리 코드이며 외부 네트워크 요청을 하지
않습니다. 상태에는 모드·프로필, 해시된 프로젝트 키, 세션 키와 수명주기
플래그만 저장됩니다. 프롬프트는 현재 이벤트에서 메모리로만 처리하며
로그나 상태에 기록하지 않습니다.

전체 상태를 지우려면 먼저 관련 세션을 끝내고, 호스트가
`adaptive-codex-orchestrator`에 할당한 정확한 `PLUGIN_DATA` 경로를 확인한
뒤, 그 경로가 플러그인 전용이며 저장소·홈·`.codex` 루트·공유 상위 폴더가
아님을 검증하세요. 확인된 전용 폴더 또는 그 안의 `state-v1.json`만
삭제합니다. 와일드카드나 확인되지 않은 환경 변수로 재귀 삭제하지 마세요.

- [보안 원문](../SECURITY.md)
- [개인정보 원문](../PRIVACY.md)
- [이용 조건 원문](../TERMS.md)
- [지원 안내](SUPPORT.ko.md)

## 검증 및 게시 상태

[2026-08-19 로컬 검증 기록](../VALIDATION.md)은 Windows/Python 3.12.10에서
108개 테스트(실패 0, 의도적 skip 1), 31개 정책 평가, 1,969개 패키지
assertion 통과를 기록합니다. GitHub Actions는 Windows·macOS·Linux와 Python
3.9·3.12로 설정됐지만, 이 로컬 기록에서는 원격 CI를 실행하지 않았습니다.

게시자 `battle-doll`, manifest에 지정된 공개 후보 URL과 PNG 2개가 기록되어
있습니다. 중립적인
`assets/logo.png`와 `assets/composer-icon.png`를 포털의 light/dark 네 업로드
슬롯에 각각 재사용하도록 지정했습니다. 이 패키지는 skills-only이며 사용자 대상 MCP
도구 UI가 없어 현재 검토 범위에서는 제품 UI 스크린샷이 필요하지 않습니다.
양성 5개·음성 3개의 [검토 사례](../../evals/reviewer-cases.json)도 준비되었습니다.
게시 전에는 각 URL의 접근성과 내용, 법률·상표 검토, 깨끗한 공개 원본 설치와 당시 포털
요건 재확인이 남아 있습니다. 자세한 내용은 [제출 기록](SUBMISSION.ko.md)과
[게시 검토](PUBLISHING.ko.md)를 참고하세요.

소스는 [MIT License](../../LICENSE)로 제공됩니다. 번역본은 편의를 위한
자료이며 영문 유지 문서, [Terms](../TERMS.md)와 번역하지 않은 `MIT License`
내용을 대체하지 않습니다.
