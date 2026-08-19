# 公開レビュー用チェックリスト

[English](../PUBLISHING.md) · [한국어](PUBLISHING.ko.md) · **日本語** ·
[简体中文](PUBLISHING.zh-CN.md) · [Русский](PUBLISHING.ru.md)

これは [英語版 Publishing Checklist](../PUBLISHING.md) の日本語案内です。
差異がある場合、維持されている英語原文を基準とします。

## 現在の状態

Adaptive Codex Orchestrator `0.1.0` は未公開の public-review candidate です。
この repository の内容は、提出、承認、deploy、marketplace acceptance
を意味しません。公開は、すべての該当 gate を通過した後に repository
owner が明示的に実行する操作です。

本プロジェクトは独立した community tool であり、OpenAI の提携・後援・
推奨・公式製品であるかのように表示してはいけません。

## Package と public metadata

- [ ] 現在の公式またはインストール済み validator で
      `.codex-plugin/plugin.json` を検証する。
- [ ] package folder と manifest name が正確に
      `adaptive-codex-orchestrator` であることを確認する。
- [ ] manifest、`pyproject.toml`、marketplace、`CHANGELOG.md` の version を
      一致させる。
- [ ] manifest に記録された publisher/developer `battle-doll` の ownership と
      表示を最終確認する。
- [ ] manifest が公開候補先として指定する
      [GitHub repository](https://github.com/battle-doll/adaptive-codex-orchestrator)、
      homepage、privacy、terms URL の到達性と内容を確認する。一般 support は
      [GitHub Issues](https://github.com/battle-doll/adaptive-codex-orchestrator/issues)、
      機密 security report は[非公開 advisory](https://github.com/battle-doll/adaptive-codex-orchestrator/security/advisories/new)と
      区別し、使用前に到達性を確認する。
- [ ] `LICENSE` と manifest の `MIT` metadata が一致することを確認する。
- [ ] 現 validator は manifest `hooks` field を拒否するため、既定の
      `hooks/hooks.json` discovery を維持する。
- [ ] 未対応の `supportURL`、`brandColorDark` を追加しない。
- [ ] starter prompt が機能、長さ、韓国語・英語のみの command support を
      誇張していないことを確認する。

## Assets と evidence

- [ ] `assets/icon.svg` と `assets/logo.svg` の独自性、小サイズでの可読性、
      light/dark contrast を確認する。
- [ ] OpenAI/ChatGPT logo、複製した Codex artwork、混同を招く外観、bundled
      font、取得不能な外部 asset がないことを確認する。
- [x] `assets/logo.png` (256×256) と `assets/composer-icon.png` (48×48) を用意し SVG
      source を保持した。中立な 2 PNG は 4 light/dark upload slots で再利用する
      ものとして指定した。
- [x] package は skills-only でユーザー向け MCP tool UI がなく、現在の review
      scope では product UI screenshot が不要であることを記録した。提出時に
      portal requirement が変わっていないか再確認する。
- [ ] [Validation](../VALIDATION.md) と [Testing](../TESTING.md) の unit、hook
      fixture、state、parser、path、policy eval を再実行する。
- [x] 再現 setup と expected result を含む
      [positive 5 件・negative 3 件の reviewer cases](../../evals/reviewer-cases.json)を
      準備した。
- [ ] [Security](../SECURITY.md)、[Privacy](../PRIVACY.md)、
      [Terms](../TERMS.md) を人が review する。文書は法律相談ではない。

## Local marketplace の手動テスト

実際の `.agents/plugins/marketplace.json` name が
`adaptive-codex-orchestrator` であることを確認します。次の command は
Codex state を変更するため owner が手動で実行します。

```text
codex plugin marketplace add <absolute-repository-root>
codex plugin list --marketplace adaptive-codex-orchestrator --available --json
codex plugin add adaptive-codex-orchestrator@adaptive-codex-orchestrator
```

新しい Codex task で hook trust、disabled behavior、4 scopes、3 profiles、
status、cleanup、compatibility mode、bounded delegation、
`$adaptive-orchestration` fallback をテストします。既定の personal
marketplace に `marketplace add` を実行しません。

## Submission 直前

1. 最新の公式 plugin、hook、subagent、model、public-submission schema を
   再確認する。
2. 実際の public source を clean environment にインストールして試験する。
3. publisher claim と全 public URL の ownership、HTTPS、redirect、内容を
   確認する。
4. secret、private path、prompt、source fixture、local cachebuster、欠落 asset
   がないことを確認する。
5. code、docs、security、privacy、terms、brand、compatibility を最終 review
   する。
6. owner の明示的承認後、その時点の公式手続だけで提出する。

local validation の PASS だけで checklist を完了扱いにしません。

## Owner-only actions

- publisher `battle-doll` と manifest 指定の公開候補 URL の ownership、到達性、内容を
  最終検証する。
- 必要な legal/trademark review を受ける。
- 2 PNG の 4 light/dark slots での再利用を当時の portal で確認する。skills-only
  のままなら product UI screenshot は作成しない。
- prepared positive 5 / negative 3 reviewer cases を portal で人が確認する。
- 実際の public source から対応 platform へ clean install する。
- tag、push、release、submission を明示的に承認する。
- 公開後の public support と private security-reporting channel を維持する。

この翻訳は [MIT License](../../LICENSE) の名称、権利、免責を変更せず、
[英語原文](../PUBLISHING.md)を置き換えません。
