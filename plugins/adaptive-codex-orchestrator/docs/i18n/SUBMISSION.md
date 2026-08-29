# Public submission record

**English** · [한국어](SUBMISSION.ko.md) · [日本語](SUBMISSION.ja.md) ·
[简体中文](SUBMISSION.zh-CN.md) · [Русский](SUBMISSION.ru.md)

Review date: **2026-08-29**

Status: **v0.1.0 Published and remote-catalog `GLOBAL` / `AVAILABLE` /
`UNLISTED`; v0.1.1 is an unsubmitted update candidate**.

Exact v0.1.0 plugin page:
<https://chatgpt.com/plugins/plugins_6a86354985fc8191b33d2795e2851821>.
The first publication date is unknown. No LISTED status is claimed.

This is a concise public-review record. The detailed owner gates remain in
[Publishing](../PUBLISHING.md), and the latest locally executed evidence is in
[Validation](../VALIDATION.md). Nothing in this document authorizes a tag,
push, release, deployment, marketplace registration, or external submission.

## Exact portal listing candidate

These values mirror the current package manifest and must be rechecked against
the then-current official portal schema immediately before submission.

| Field | Manifest-recorded candidate value |
| --- | --- |
| Package | `adaptive-codex-orchestrator` |
| Version | `0.1.1` |
| Type | `Skills-only Codex plugin with trusted local lifecycle hooks` |
| Display name | `Adaptive Codex Orchestrator` |
| Subtitle / short description | `Explicit bounded orchestration` |
| Package description | `Control when Codex delegates bounded tasks, with explicit scope, profiles, and safe parallel execution.` |
| Developer / publisher | `battle-doll` |
| Category | `Developer Tools` |
| License | `MIT` (`MIT License`) |
| Runtime mode | `Ultra Orchestration` |
| Requested worker | `gpt-5.3-codex-spark` |
| Command languages | Korean and English only |
| Brand color | `#7168E8` |
| Composer icon | `./assets/composer-icon.png` |
| Logo | `./assets/logo.png` |
| Website | `https://github.com/battle-doll/adaptive-codex-orchestrator` |
| Support policy | `https://github.com/battle-doll/adaptive-codex-orchestrator/blob/main/SUPPORT.md` |
| Privacy policy | `https://github.com/battle-doll/adaptive-codex-orchestrator/blob/main/PRIVACY.md` |
| Terms | `https://github.com/battle-doll/adaptive-codex-orchestrator/blob/main/TERMS.md` |
| Requested availability | All countries and regions where OpenAI offers the applicable plugin and Codex surfaces |

The two neutral PNGs are ready: `assets/logo.png` at 256×256 and
`assets/composer-icon.png` at 48×48. They are designated for reuse across the
portal's four light/dark logo and composer-icon upload slots. No additional PNG
is implied. This is a skills-only package with no user-facing MCP tool UI, so a
product UI screenshot is not required for the current review scope; recheck the
portal rule at submission time.

Exact long description:

> Use Adaptive Codex Orchestrator when the user explicitly enables, disables,
> scopes, profiles, or queries orchestration in Korean or English. The parent
> keeps requirements, architecture, integration, validation, and the final
> answer while bounded, independently verifiable work may be delegated. It
> does not activate merely because parallel work could help, does not change
> the selected parent model or reasoning level, permissions, sandbox settings,
> or network access, and does not store prompts or source code. Worker model
> requests follow the bundled policy.

Exact capabilities:

1. `Adaptive task orchestration`
2. `Parent-owned judgment and review`
3. `Bounded worker delegation`
4. `Controlled parallel reads and writes`
5. `Korean and English mode controls`
6. `One-shot, session, project, and global scopes`
7. `Local offline state`
8. `Codex lifecycle hooks`

Exact starter prompts:

```text
Use orchestration for this task only: inspect three independent modules without editing, then summarize the evidence.
이번 작업만 울트라 오케스트레이션을 켜고 파서 버그를 재현한 뒤 최소 수정과 집중 테스트를 해줘.
Show orchestration status, scope, and profile, and say whether persistent hooks are available.
```

Proposed release note (copy exactly if still accurate at submission):

> Discovery-focused patch update. It clarifies that explicit Korean or English
> orchestration controls—not merely parallelizable work—select the plugin and
> adds a 50-case Korean/English discovery golden set. It does not change the
> runtime parser, hook behavior, state schema, delegation policy, permissions,
> privacy, network behavior, or deterministic packaging contract.

## Designated candidate destinations

The manifest-recorded publisher is [battle-doll](https://github.com/battle-doll).
The following GitHub locations are designated candidate destinations. A
designation is not proof of accessibility, reviewed content, or publication;
verify every destination over HTTPS before use and again before submission.

- Repository and website:
  [github.com/battle-doll/adaptive-codex-orchestrator](https://github.com/battle-doll/adaptive-codex-orchestrator)
- Homepage:
  [repository README](https://github.com/battle-doll/adaptive-codex-orchestrator#readme)
- Privacy:
  [PRIVACY.md](https://github.com/battle-doll/adaptive-codex-orchestrator/blob/main/PRIVACY.md)
- Terms:
  [TERMS.md](https://github.com/battle-doll/adaptive-codex-orchestrator/blob/main/TERMS.md)
- General support:
  [GitHub Issues](https://github.com/battle-doll/adaptive-codex-orchestrator/issues)
- Public support policy:
  [SUPPORT.md](https://github.com/battle-doll/adaptive-codex-orchestrator/blob/main/SUPPORT.md)
- Sensitive security reports:
  [private GitHub advisory](https://github.com/battle-doll/adaptive-codex-orchestrator/security/advisories/new)

GitHub Issues is the designated general-support candidate. Do not send sensitive
reports there. The private GitHub advisory is the designated security-reporting
candidate and must be enabled and verified before use.

The package has one skill, no MCP server, no OAuth, no API key, no external
account, no external network dependency, no telemetry, and no custom app UI.
Consequently, the current skills-only review supplies neither UI screenshots
nor test credentials.

## Reviewer evidence and remaining gates

The portal-ready [reviewer cases](../../evals/reviewer-cases.json) contain
exactly **five positive and three negative cases**, including reproducible
setup, expected behavior, result shape, and a safety rationale for every
negative case. They complement, rather than replace, the 31-scenario offline
policy dataset.

The static `evals/discovery-cases.json` golden set adds exactly **10 direct,
20 indirect, and 20 negative** Korean/English selection cases. Its validator
checks count, locale balance, and expected-selection labels; it is not a claim
of live-host execution or human semantic scoring.

Before submission, the owner must:

- Recheck current manifest, hook, skill, model, asset, screenshot, legal-link,
  and portal requirements. Current validation intentionally omits a manifest
  `hooks` field and uses default `hooks/hooks.json` discovery; do not add
  unsupported `supportURL` or `brandColorDark` fields.
- Verify `battle-doll`, all public URLs, `MIT License`, version, the two PNG
  assets and their four-slot reuse, skills-only status, privacy/security/terms
  text, and the release note. Do not invent a product UI screenshot while no
  user-facing MCP tool UI exists.
- Run the full offline validation and a clean install from the actual public
  source; local validation does not equal marketplace approval.
- Review the five positive and three negative reviewer cases manually, then
  submit only through the current official process with explicit owner approval.

Control commands are recognized in Korean and English only. Localized public
documentation does not add Japanese, Simplified Chinese, or Russian command
support.
