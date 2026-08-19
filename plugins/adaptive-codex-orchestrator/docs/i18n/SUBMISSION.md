# Public submission record

**English** · [한국어](SUBMISSION.ko.md) · [日本語](SUBMISSION.ja.md) ·
[简体中文](SUBMISSION.zh-CN.md) · [Русский](SUBMISSION.ru.md)

Review date: **2026-08-19**

Status: **prepared locally; not yet submitted/approved/published**.

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
| Version | `0.1.0` |
| Type | `Skills-only Codex plugin with trusted local lifecycle hooks` |
| Display name | `Adaptive Codex Orchestrator` |
| Subtitle / short description | `Adaptive task orchestration` |
| Package description | `Local, deterministic orchestration policies for adaptive Codex development workflows.` |
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

> Apply deterministic, local orchestration policy to Codex development tasks
> while the selected parent model keeps requirements, architecture, review,
> integration, validation, and the final answer. Use Korean or English controls
> for one-shot, session, project, or global scope, choose conservative,
> balanced, or fast profiles, and delegate only bounded, independently
> verifiable work. The plugin never changes the parent model or reasoning level,
> requests gpt-5.3-codex-spark only when useful, stores no prompts or source
> code, and sends no telemetry.

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
Use Ultra Orchestration to inspect three independent modules without editing, then summarize the evidence.
Use Ultra Orchestration for this task only: reproduce the parser bug, make the smallest fix, and run focused tests.
Show the current Ultra Orchestration scope and profile, and explain whether persistent hooks are available.
```

Proposed release note (copy exactly if still accurate at submission):

> Initial skills-only release of Adaptive Codex Orchestrator. It packages one
> adaptive orchestration skill and trusted local lifecycle hooks for one-shot,
> session, project, and plugin-global profiles. The control plane is offline,
> uses plugin-owned local state, and requires no MCP server, OAuth, credentials,
> telemetry, or external network access. When hooks are unavailable or untrusted,
> explicit skill use applies only to the current request. Reviewers should use a
> writable `PLUGIN_DATA` directory and trust the bundled hooks for persistent-mode
> tests.

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
