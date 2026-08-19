# 지원

[English](SUPPORT.md) · **한국어** · [日本語](SUPPORT.ja.md) ·
[简体中文](SUPPORT.zh-CN.md) · [Русский](SUPPORT.ru.md)

> Adaptive Codex Orchestrator `0.1.0`은 게시 전 공개 검토 후보입니다. 공개
> 지원 위치는 [GitHub Issues](https://github.com/battle-doll/adaptive-codex-orchestrator/issues)로
> 일반 지원 후보로 지정되어 있지만 사용 전에 접근성을 확인해야 하며 응답 시간
> 약속은 없습니다.

이 프로젝트는 독립 커뮤니티 도구이며 OpenAI의 제휴·후원·보증을 받는 공식
제품이 아닙니다. 지원은 최선 노력 방식이며 전문 보안·법률·개인정보·운영
검토를 대체하지 않습니다.

## 도움을 요청하기 전에

[README](README.ko.md), [호환성](../COMPATIBILITY.md),
[보안](../SECURITY.md), [개인정보](../PRIVACY.md),
[검증 기록](../VALIDATION.md)을 확인하고 다음 정보를 준비하세요.

- 플러그인 버전과 운영체제
- Codex 앱 또는 CLI 중 사용 표면
- `hooks/hooks.json`을 검토하고 호스트에서 신뢰했는지 여부
- 영구 훅과 `$adaptive-orchestration <task>` 대안 중 어디에서 발생했는지
- 기대 결과, 실제 결과, 최소 재현과 관련 validation 출력

자격 증명, API 키, 비공개 프롬프트·대화 기록, 독점 소스 코드, 저장소 내용,
계정 식별자 또는 비공개 절대 경로를 올리지 마세요.

## 자주 발생하는 문제

- **모드가 유지되지 않음:** 지원되고 신뢰된 훅과 쓰기 가능한
  `PLUGIN_DATA`가 필요합니다. 훅을 사용할 수 없으면
  `$adaptive-orchestration <task>`를 현재 작업에만 사용하세요.
- **호환 안내가 표시됨:** 플러그인은 부모 모델을 바꾸지 않습니다. 의도한
  부모 모델과 Ultra 설정을 직접 선택하세요. Ultra 검증 성공을 주장하지
  않습니다.
- **Spark가 확인되지 않음:** 호스트가 `gpt-5.3-codex-spark` 가용성이나 모델
  식별자를 제공하지 않을 수 있습니다. 위임된 하위 작업마다 spawn은 한 번만
  시도합니다. 실패·한도·미지원이면 재시도하거나 host-default 모델로 대체하지
  않고 즉시 부모로 되돌립니다.
- **Git 또는 프로젝트 식별 실패:** 정규화한 작업 디렉터리의 SHA-256 해시로
  대체하며 원본 경로는 저장하지 않습니다.
- **상태 손상 또는 쓰기 불가:** 일반 Codex 동작은 계속됩니다. 보존된 손상
  백업은 임의 바이트를 포함할 수 있으므로 민감한 로컬 증거로 취급하세요.

## 안전한 상태 초기화

관련 세션을 끝내고 호스트가 `adaptive-codex-orchestrator`에 할당한 정확한
`PLUGIN_DATA` 경로를 확인합니다. 그 경로가 플러그인 전용이며 소스,
저장소·홈·`.codex` 루트 또는 공유 상위 폴더가 아님을 검증한 뒤, 확인된
전용 폴더나 그 안의 `state-v1.json`만 삭제합니다. 와일드카드, 해석되지
않은 환경 변수나 공유 폴더를 재귀 삭제 대상으로 쓰지 마세요.

## 보안 취약점 신고

공개 이슈에 exploit 세부 정보, 자격 증명, 프롬프트, 독점 소스나 비공개
경로를 공개하지 마세요. 지정된 보안 신고 후보 채널은
[비공개 GitHub advisory](https://github.com/battle-doll/adaptive-codex-orchestrator/security/advisories/new)이며
사용 전에 활성화와 접근 가능 여부를 확인해야 합니다. 사용할 수 없으면 민감한
내용을 보류하고 먼저 maintainer에게 비공개 채널을 요청하세요.

영향 버전, 플랫폼과 Codex 표면, 최소 재현, 보안 영향과 신뢰된 훅 필요
여부를 포함하세요. maintainer가 별도 정책을 게시하기 전에는 응답 시간
보장이 없습니다. 기준 절차는 [보안 원문](../SECURITY.md)입니다.

## 게시 상태

manifest에는 게시자 `battle-doll`과 공개 후보 위치로 지정된
[GitHub 저장소](https://github.com/battle-doll/adaptive-codex-orchestrator),
웹사이트·개인정보·약관 위치가 기록되어 있습니다. GitHub Issues는 일반 지원 후보,
비공개 advisory는 보안 신고 후보 채널입니다. 이 지정은 접근 가능성이나 게시 완료의
증거가 아니므로 사용 전에 확인해야 합니다. 소유자가 [게시 검토](PUBLISHING.ko.md)를 완료하고
모든 주소를 확인해 명시적으로 승인하기 전에는 마켓플레이스 게시·승인 플러그인으로
설명할 수 없습니다.

제어 명령은 한국어와 영어만 인식합니다. 번역된 지원 문서는 일본어·중국어·
러시아어 명령 지원을 추가하지 않습니다.

번역본과 영문 원문이 다르면 [영문 지원 안내](SUPPORT.md),
[Terms](../TERMS.md), 번역하지 않은 [MIT License](../../LICENSE)를
기준으로 합니다.
