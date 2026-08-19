# 공개 제출 기록

[English](SUBMISSION.md) · **한국어** · [日本語](SUBMISSION.ja.md) ·
[简体中文](SUBMISSION.zh-CN.md) · [Русский](SUBMISSION.ru.md)

검토일: **2026-08-19**

상태: **로컬 준비 완료; 아직 제출·승인·게시되지 않음**.

이 문서는 공개 검토용 요약입니다. 상세 소유자 절차는
[게시 체크리스트](../PUBLISHING.md), 실행된 로컬 증거는
[검증 기록](../VALIDATION.md)에 있습니다. 이 문서는 tag, push, release, 배포,
마켓플레이스 등록 또는 외부 제출을 승인하지 않습니다.

## 제출 메타데이터

영문 [정확한 포털 목록 값](SUBMISSION.md#exact-portal-listing-candidate)은 현재
manifest를 그대로 반영합니다. 핵심 값은 다음과 같습니다.

- 패키지 `adaptive-codex-orchestrator`, 버전 `0.1.0`
- 표시 이름 `Adaptive Codex Orchestrator`
- 부제 `Adaptive task orchestration`
- 게시자 `battle-doll`, 범주 `Developer Tools`, 라이선스 `MIT`
- 실행 모드 `Ultra Orchestration`, 요청 작업자 `gpt-5.3-codex-spark`
- 색상 `#7168E8`, `./assets/composer-icon.png`(48×48), `./assets/logo.png`(256×256).
  중립 PNG 2개를 light/dark 네 업로드 슬롯에 재사용하며 추가 PNG를 뜻하지 않습니다.
- 제어 명령 언어: 한국어와 영어만

영문 원문에는 정확한 long description, 8개 capability, 3개 starter prompt와
제안 release note가 포함되어 있습니다. 제출 직전에 당시 공식 포털 스키마와
대조해야 합니다.

## 지정된 공개 후보 위치

manifest에 기록된 게시자는 [battle-doll](https://github.com/battle-doll)입니다.
저장소·웹사이트는
[GitHub 저장소](https://github.com/battle-doll/adaptive-codex-orchestrator),
홈페이지는 [README](https://github.com/battle-doll/adaptive-codex-orchestrator#readme),
개인정보는 [PRIVACY.md](https://github.com/battle-doll/adaptive-codex-orchestrator/blob/main/PRIVACY.md),
약관은 [TERMS.md](https://github.com/battle-doll/adaptive-codex-orchestrator/blob/main/TERMS.md),
공개 지원 정책은 [SUPPORT.md](https://github.com/battle-doll/adaptive-codex-orchestrator/blob/main/SUPPORT.md),
일반 지원 후보는 [GitHub Issues](https://github.com/battle-doll/adaptive-codex-orchestrator/issues),
민감한 보안 신고 후보는
[비공개 GitHub advisory](https://github.com/battle-doll/adaptive-codex-orchestrator/security/advisories/new)로
지정되어 있습니다.

이 지정은 접근 가능성·검토된 내용·게시 완료의 증거가 아닙니다. 사용 전과 제출
전에 HTTPS 응답, 소유권, 내용과 비공개 advisory 활성화를 확인해야 하며 민감한
내용을 Issues에 올리면 안 됩니다.

## 검토 증거와 남은 절차

[검토 사례](../../evals/reviewer-cases.json)는 재현 가능한 설정과 기대 동작을 가진
정확히 **양성 5개와 음성 3개** 사례입니다. 이는 31개 오프라인 정책 평가를
대체하지 않습니다.

소유자는 최신 manifest·hook·skill·model·asset·screenshot·법률 링크·포털
요건을 재확인하고, 게시자·URL·`MIT License`·버전·PNG 2개의 네 슬롯 재사용·
정책·release note를 검증해야 합니다. 현재는 skills-only이고 사용자 대상 MCP
도구 UI가 없으므로 제품 UI 스크린샷을 만들 필요가 없습니다. 전체 오프라인 검증과
실제 공개 원본의 깨끗한 설치를 수행하고, 명시적으로 승인한 뒤 당시 공식 절차로만
제출해야 합니다. 로컬 검증 통과는 마켓플레이스 승인이 아닙니다.

제어 명령은 한국어와 영어만 인식합니다. 번역 문서는 일본어·중국어·러시아어
명령 지원을 추가하지 않습니다.
