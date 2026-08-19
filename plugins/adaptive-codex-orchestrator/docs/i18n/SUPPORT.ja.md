# サポート

[English](SUPPORT.md) · [한국어](SUPPORT.ko.md) · **日本語** ·
[简体中文](SUPPORT.zh-CN.md) · [Русский](SUPPORT.ru.md)

> Adaptive Codex Orchestrator `0.1.0` は未公開の public-review candidate
> です。public support は [GitHub Issues](https://github.com/battle-doll/adaptive-codex-orchestrator/issues)
> を一般 support の候補先として指定していますが、使用前に到達確認が必要で、response-time commitment
> はありません。

本プロジェクトは独立した community tool であり、OpenAI の提携・後援・
推奨を受ける公式製品ではありません。support は best effort で、専門的な
security、legal、privacy、production review を代替しません。

## 問い合わせ前の確認

[README](README.ja.md)、[Compatibility](../COMPATIBILITY.md)、
[Security](../SECURITY.md)、[Privacy](../PRIVACY.md)、
[Validation](../VALIDATION.md)を確認し、次を用意してください。

- plugin version と operating system
- Codex app または CLI のどちらを使用したか
- `hooks/hooks.json` を review し、host で trust したか
- persistent hooks と `$adaptive-orchestration <task>` fallback のどちらで
  発生したか
- expected/observed behavior、minimal reproduction、関連 validation output

credential、API key、private prompt/transcript、proprietary source、repository
content、account identifier、private absolute path を投稿しないでください。

## よくある問題

- **Mode が保持されない:** supported/trusted hooks と writable
  `PLUGIN_DATA` が必要です。hooks が使えない場合、現在の task だけに
  `$adaptive-orchestration <task>` を使用します。
- **Compatibility notice:** plugin は親モデルを変更しません。意図した親と
  Ultra setting を手動で選択してください。Ultra の検証成功は主張しません。
- **Spark が確認されない:** host は `gpt-5.3-codex-spark` availability または
  model identity を提供しない場合があります。委任した subtask ごとの spawn
  は 1 回だけです。失敗・上限・未対応の場合は retry や host-default model
  への置換を行わず、直ちに親へ戻します。
- **Git/project identity failure:** normalized working directory の SHA-256
  digest に fallback し、生の path は保存しません。
- **State corruption/unwritable:** 通常の Codex behavior は継続します。保存
  された破損 backup は任意 byte を含み得るため、sensitive local evidence と
  して扱います。

## 安全なリセット

関連 session を終了し、host が `adaptive-codex-orchestrator` に割り当てた
正確な `PLUGIN_DATA` を取得します。それが plugin 専用で、source、repository
root、home、`.codex` root、共有 parent ではないと確認してから、その directory
または `state-v1.json` だけを削除します。wildcard、未解決の environment
variable、共有 directory を再帰削除対象にしないでください。

## Security vulnerability

public issue に exploit detail、credential、prompt、proprietary source、private
path を公開しないでください。指定された security-reporting 候補窓口は
[非公開 GitHub advisory](https://github.com/battle-doll/adaptive-codex-orchestrator/security/advisories/new)です。
使用前に有効化と到達性を確認し、利用できなければ sensitive detail を保留して
maintainer に private channel を依頼してください。

affected version、platform/Codex surface、minimal reproduction、impact、trusted
hooks の必要性を含めます。maintainer が方針を公開するまで response-time
guarantee はありません。基準は [Security 原文](../SECURITY.md)です。

## 公開状態

manifest には publisher `battle-doll` と公開候補先として指定された
[GitHub repository](https://github.com/battle-doll/adaptive-codex-orchestrator)、
website、privacy、terms が記録されています。GitHub Issues は一般 support 候補、
非公開 advisory は security-reporting 候補です。この指定は到達可能または公開済みの
証拠ではないため使用前に確認します。owner が [公開レビュー](PUBLISHING.ja.md)を完了し、全 URL
を検証して明示的に承認するまで、marketplace 公開・承認済みと説明できません。

制御コマンドとして認識されるのは韓国語と英語だけです。この翻訳は日本語・
簡体字中国語・ロシア語のコマンド対応を追加しません。

翻訳と英語原文が異なる場合、[英語 Support](SUPPORT.md)、
[Terms](../TERMS.md)、翻訳されていない [MIT License](../../LICENSE) を
基準とします。
