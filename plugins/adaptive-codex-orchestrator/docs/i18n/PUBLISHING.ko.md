# 게시 검토 체크리스트

[English](../PUBLISHING.md) · **한국어** · [日本語](PUBLISHING.ja.md) ·
[简体中文](PUBLISHING.zh-CN.md) · [Русский](PUBLISHING.ru.md)

이 문서는 [영문 게시 체크리스트](../PUBLISHING.md)의 한국어 안내본입니다.
차이가 있으면 유지 관리되는 영문 원문을 기준으로 합니다.

## 현재 상태

2026-08-29 확인 결과 `0.1.0`은 OpenAI Platform에 Published 상태이고 원격
카탈로그는 `GLOBAL` / `AVAILABLE`, discoverability `UNLISTED`로 기록합니다:
<https://chatgpt.com/plugins/plugins_6a86354985fc8191b33d2795e2851821>.
최초 게시 날짜는 확인되지 않았습니다. `0.1.1`은 아직 제출하지 않은 업데이트
후보이며, 저장소의 어떤 내용도 해당 업데이트의 제출·승인·게시·LISTED 상태를
의미하지 않습니다.

이 프로젝트는 독립 커뮤니티 도구이며 OpenAI의 제휴·후원·보증·공식 제품인
것처럼 표시하면 안 됩니다.

## 패키지와 공개 메타데이터

- [ ] 현재 공식/설치된 validator로 `.codex-plugin/plugin.json`을 검사합니다.
- [ ] 패키지 폴더와 manifest 이름이 정확히
      `adaptive-codex-orchestrator`인지 확인합니다.
- [ ] manifest, `pyproject.toml`, 마켓플레이스와 `CHANGELOG.md`의 버전이
      일치하는지 확인합니다.
- [ ] manifest에 기록된 게시자·개발자 `battle-doll`의 소유권과 표시를 최종
      확인합니다.
- [ ] manifest에 공개 후보 위치로 지정된
      [GitHub 저장소](https://github.com/battle-doll/adaptive-codex-orchestrator),
      홈페이지·개인정보·약관 주소가 실제로 열리고 검토된 내용인지 확인합니다.
      일반 지원은 [GitHub Issues](https://github.com/battle-doll/adaptive-codex-orchestrator/issues),
      민감한 보안 신고는 [비공개 advisory](https://github.com/battle-doll/adaptive-codex-orchestrator/security/advisories/new)로
      구분하며 사용 전에 접근성을 확인합니다.
- [ ] `LICENSE`와 manifest의 `MIT` 메타데이터가 일치하는지 확인합니다.
- [ ] 현재 validator가 manifest `hooks` 필드를 거부하므로 기본
      `hooks/hooks.json` 탐색을 유지합니다.
- [ ] 지원되지 않는 `supportURL`, `brandColorDark`를 추가하지 않습니다.
- [ ] starter prompt가 실제 기능, 길이 제한과 한국어·영어 명령 지원 범위를
      과장하지 않는지 확인합니다.

## 자산과 증거

- [ ] `assets/icon.svg`, `assets/logo.svg`가 독창적이고 작은 크기에서도
      읽히는지 확인합니다.
- [ ] OpenAI/ChatGPT 로고, 복제된 Codex 아트워크, 혼동 가능한 외형, 번들
      폰트나 외부 누락 자산이 없는지 확인합니다.
- [x] `assets/logo.png`(256×256)와 `assets/composer-icon.png`(48×48)를 준비하고 SVG
      원본을 보존했습니다. 두 중립 PNG는 light/dark 네 업로드 슬롯에 재사용하도록
      지정했습니다.
- [x] 이 패키지는 skills-only이고 사용자 대상 MCP 도구 UI가 없어 현재 검토
      범위에서 제품 UI 스크린샷이 필요하지 않음을 기록했습니다. 제출 시점의
      포털 요구가 달라졌는지는 다시 확인합니다.
- [ ] [검증 기록](../VALIDATION.md)과 [테스트 절차](../TESTING.md)의 단위,
      훅 fixture, 상태, 파서, 경로, 정책 평가를 다시 실행합니다.
- [x] 재현 설정과 기대 결과를 포함한 [양성 5개·음성 3개 검토 사례](../../evals/reviewer-cases.json)를
      준비했습니다.
- [ ] [보안](../SECURITY.md), [개인정보](../PRIVACY.md),
      [이용 조건](../TERMS.md)을 사람이 검토합니다. 문서는 법률 자문이
      아닙니다.

## 로컬 마켓플레이스 수동 시험

실제 `.agents/plugins/marketplace.json` 이름이
`adaptive-codex-orchestrator`인지 먼저 확인합니다. 다음 명령은 Codex
상태를 변경하므로 소유자가 수동으로 실행합니다.

```text
codex plugin marketplace add <absolute-repository-root>
codex plugin list --marketplace adaptive-codex-orchestrator --available --json
codex plugin add adaptive-codex-orchestrator@adaptive-codex-orchestrator
```

새 Codex 작업에서 훅 신뢰, 비활성 상태, 네 범위, 세 프로필, 상태 표시,
정리, 호환 모드, 제한된 위임과 `$adaptive-orchestration` 대안을 시험합니다.
기본 개인 마켓플레이스에는 `marketplace add`를 실행하지 않습니다.

## 제출 직전

1. 최신 공식 plugin·hook·subagent·model·공개 제출 스키마를 다시 확인합니다.
2. 실제 공개 배포 원본을 깨끗한 환경에 설치해 시험합니다.
3. 게시자 주장과 모든 공개 URL의 소유권·HTTPS·redirect·내용을 확인합니다.
4. 비밀, 비공개 경로, 프롬프트, source fixture, 로컬 cachebuster와 누락
   자산이 없는지 확인합니다.
5. 코드, 문서, 보안, 개인정보, 약관, 브랜드와 호환성을 최종 검토합니다.
6. 소유자의 명시적 승인 후 당시의 공식 절차로만 제출합니다.

로컬 validation 통과만으로 이 체크리스트를 완료 처리하지 않습니다.

## 소유자만 수행할 남은 작업

- 게시자 `battle-doll`과 manifest 지정 공개 후보 URL의 소유권·접근성·내용을
  최종 검증합니다.
- 적절한 법률·상표 검토를 받습니다.
- 두 PNG를 네 light/dark 슬롯에 재사용할 수 있는지 당시 포털에서 확인합니다.
  skills-only 상태가 바뀌지 않았다면 제품 UI 스크린샷은 만들지 않습니다.
- 준비된 양성 5개·음성 3개 검토 사례를 포털에서 사람이 확인합니다.
- 실제 공개 원본에서 지원 플랫폼의 설치를 시험합니다.
- tag, push, release, submission을 명시적으로 승인합니다.
- 게시 뒤 공개 지원 및 비공개 보안 신고 채널을 유지합니다.

번역본은 [MIT License](../../LICENSE) 이름과 권리·면책 내용을 변경하지
않으며 [영문 원문](../PUBLISHING.md)을 대체하지 않습니다.
