# 公開提出記録

[English](SUBMISSION.md) · [한국어](SUBMISSION.ko.md) · **日本語** ·
[简体中文](SUBMISSION.zh-CN.md) · [Русский](SUBMISSION.ru.md)

レビュー日: **2026-08-19**

状態: **ローカルで準備済み、未提出・未承認・未公開**。

これは公開レビュー向け要約です。詳細な owner gate は
[Publishing](../PUBLISHING.md)、実行済みローカル証拠は
[Validation](../VALIDATION.md)を参照してください。本書は tag、push、release、
deploy、marketplace 登録、外部提出を許可しません。

## 提出メタデータ

英語版の[正確な portal listing](SUBMISSION.md#exact-portal-listing-candidate)は
現在の manifest をそのまま反映しています。主要値は次のとおりです。

- package `adaptive-codex-orchestrator`、version `0.1.0`
- display name `Adaptive Codex Orchestrator`
- subtitle `Adaptive task orchestration`
- publisher `battle-doll`、category `Developer Tools`、license `MIT`
- runtime mode `Ultra Orchestration`、requested worker `gpt-5.3-codex-spark`
- color `#7168E8`、`./assets/composer-icon.png` (48×48)、`./assets/logo.png` (256×256)。
  中立な 2 PNG を 4 light/dark upload slots で再利用し、追加 PNG は作らない
- control-command languages: Korean and English only

英語版には正確な long description、8 capabilities、3 starter prompts、提案
release note もあります。提出直前に当時の公式 portal schema と照合します。

## 指定された公開候補先

manifest に記録された publisher は [battle-doll](https://github.com/battle-doll) です。
repository/website は
[GitHub repository](https://github.com/battle-doll/adaptive-codex-orchestrator)、
homepage は [README](https://github.com/battle-doll/adaptive-codex-orchestrator#readme)、
privacy は [PRIVACY.md](https://github.com/battle-doll/adaptive-codex-orchestrator/blob/main/PRIVACY.md)、
terms は [TERMS.md](https://github.com/battle-doll/adaptive-codex-orchestrator/blob/main/TERMS.md)、
public support policy は [SUPPORT.md](https://github.com/battle-doll/adaptive-codex-orchestrator/blob/main/SUPPORT.md)、
一般 support 候補は [GitHub Issues](https://github.com/battle-doll/adaptive-codex-orchestrator/issues)、
機密 security-reporting 候補は
[非公開 GitHub advisory](https://github.com/battle-doll/adaptive-codex-orchestrator/security/advisories/new)として
指定されています。

この指定は到達性、review 済みの内容、公開完了の証拠ではありません。使用前と
提出前に HTTPS、ownership、内容、非公開 advisory の有効化を確認し、機密情報を
Issues に投稿しないでください。

## レビュー証拠と残作業

[Reviewer cases](../../evals/reviewer-cases.json)には、再現可能な setup と expected
behavior を持つ正確に **positive 5 件、negative 3 件**があります。31-scenario
offline policy dataset の代わりではありません。

owner は最新の manifest、hook、skill、model、asset、screenshot、legal link、
portal 要件を再確認し、publisher、URL、`MIT License`、version、2 PNG の 4-slot
reuse、policy、release note を検証します。現在は skills-only でユーザー向け
MCP tool UI がないため product UI screenshot は不要です。全 offline validation
と実際の公開元からの clean install を行い、明示的承認後に当時の公式手順だけで
提出します。ローカル検証は marketplace 承認を意味しません。

制御コマンドとして認識されるのは韓国語と英語だけです。この翻訳は日本語・
簡体字中国語・ロシア語のコマンド対応を追加しません。
