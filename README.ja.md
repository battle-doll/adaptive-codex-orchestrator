# Adaptive Codex Orchestrator

[English](README.md) · [한국어](README.ko.md) · **日本語** ·
[简体中文](README.zh-CN.md) · [Русский](README.ru.md)

> Adaptive Codex Orchestrator は独立したコミュニティプロジェクトです。
> OpenAI と提携しておらず、OpenAI が後援・推奨する公式製品でもありません。

Adaptive Codex Orchestrator は、Codex 向けのローカルかつオフラインの
オーケストレーションハーネスです。決定論的な Python 制御プレーンが、
任意の実行モード **Ultra Orchestration** の韓国語・英語コマンド、状態、
プロジェクト識別子、フックコンテキストを処理します。要件、設計、委任の
判断、結果のレビュー、統合、最終検証、ユーザーへの回答は、ユーザーが
選択した親モデルが引き続き担当します。

現在の `0.1.0` は公開レビュー候補です。GitHub でのソース公開、OpenAI
へのレビュー提出、承認、開発者による Publish は別々の状態であり、
リポジトリの公開だけで後続の状態まで完了したことにはなりません。

## 主な機能と境界

- 1 回限り、セッション、プロジェクト、プラグイン全体の既定値を
  `${PLUGIN_DATA}/state-v1.json` に保存します。
- 範囲が限定され、可逆で、独立して検証可能な作業だけを委任候補にします。
- 既定の `balanced` プロファイルでは、親ターンあたり最大 4 worker、同時
  writer は 1 です。
- 生のプロジェクトパスではなく、正規化したルートの SHA-256 ハッシュを
  保存します。
- 信頼済みフックを利用できない場合、現在のタスクだけに
  `$adaptive-orchestration <task>` を適用できます。

このプラグインは親モデル、推論レベル、モデルセレクター、権限、sandbox、
Codex のグローバル設定を変更しません。Ultra 推論が有効だと検証せず、
ホストの確認なしに `gpt-5.3-codex-spark` が使用されたとも主張しません。
API key、OAuth、外部アカウント、telemetry、制御プレーンのネットワーク
アクセスは不要です。prompt、transcript、source code、生の絶対パスは
保存しません。

## 対応範囲

確認済みの対象は Codex app と CLI です。永続的な自然言語状態には、対応し
信頼された hooks が必要です。通常の ChatGPT 会話がローカル Codex hooks、
`PLUGIN_DATA`、同一の cleanup event や subagent 設定を提供するとは
みなしません。確認済みの契約では Codex IDE extension の plugin 利用は
サポートされません。

想定どおりに使うには、ユーザーが Sol と Ultra reasoning/intelligence 設定を
手動で選択します。プラグインはこれらを変更せず、Ultra 設定を確実に検証
できません。詳細は [Compatibility](plugins/adaptive-codex-orchestrator/docs/COMPATIBILITY.md) を参照してください。

## ローカルインストール

manifest には publisher `battle-doll` と公開候補先として指定された
[GitHub repository](https://github.com/battle-doll/adaptive-codex-orchestrator)、
homepage・privacy・terms URL が記録されています。この指定は公開済みという
意味ではなく、使用または提出前に全 URL の到達性と内容を確認する必要があります。
インストール前に
`.codex-plugin/plugin.json`、`hooks/hooks.json`、`hooks/runtime.py` を確認し、
hooks を信頼するか判断してください。

repository owner が `.agents/plugins/marketplace.json` の実値を確認した後、
次を手動で実行します。これらは Codex の状態を変更します。

```text
codex plugin marketplace add <absolute-repository-root>
codex plugin list --marketplace adaptive-codex-orchestrator --available --json
codex plugin add adaptive-codex-orchestrator@adaptive-codex-orchestrator
```

インストールまたは再インストール後は新しい Codex task でテストします。
既定の personal marketplace は自動検出されるため、そのパスに
`marketplace add` を実行しません。

## 制御コマンド

現在、決定論的なコマンド認識が対応するのは **韓国語と英語のみ**です。
日本語版ドキュメントは日本語コマンド対応を意味しません。例えば次の英語
コマンドを使用できます。

```text
Turn on Ultra Orchestration for this session.
Use Ultra Orchestration for this task only.
Enable Ultra Orchestration for this repository.
Enable Ultra Orchestration globally.
Switch to the fast profile.
Show orchestration status.
Turn off Ultra Orchestration.
```

status 質問は状態を変更しません。明示的な否定、競合する scope/profile、
引用、code block、長い文章中の偶発的な例は安全側に処理されます。制御
コマンドと実作業を組み合わせた request は同じターンで適用されます。

状態の優先順位:

```text
one-shot > session > project > global > disabled
```

scope のない通常の無効化は session OFF override を作成し、project/global
設定を削除しません。

| Profile | Worker/parent turn | Concurrent writers | Delegated retry |
| --- | ---: | ---: | ---: |
| `conservative` | 2 | 1 | 0、明確に回復可能な場合のみ 1 |
| `balanced` | 4 | 1 | 1 |
| `fast` | 6 | 通常 1、完全に分離された場合のみ 2 | 1 |

より低い host limit が優先されます。`fast` の writer 2 件は、ファイル所有が
完全に分離、別 worktree、または検証済みの production/test 分離の場合だけ
許可されます。

## 委任ポリシー

ファイル・symbol 探索、限定的な call path 追跡、狭い failure 分析、確認済み
の小さな修正、focused test、機械的変更のような境界の明確な text task が
高速 worker の候補です。architecture、曖昧な root-cause、認証・認可・
暗号、database migration、破壊的操作、public API、主要 dependency、複雑な
concurrency、統合、最終検証判断は親が担当します。

Nested delegation は既定で禁止されます。各 worker には scope、許可 file、
禁止行為、必要な証拠と validation を含む契約を渡します。親はすべての結果
をレビューし、実際に作成した worker だけを報告します。

## Security、Privacy、リセット

制御プレーンはローカルの standard-library code で、外部ネットワーク要求を
行いません。state には mode/profile、ハッシュ化した project key、session
key、lifecycle flag だけが保存されます。prompt は現在 event のメモリ内で
処理され、log や state には書き込まれません。

リセット時は関連 session を終了し、host が
`adaptive-codex-orchestrator` に割り当てた正確な `PLUGIN_DATA` を確認します。
plugin source、repository root、home、`.codex` root、共有 parent ではないこと
を確認してから、その plugin 専用 directory または `state-v1.json` だけを
削除します。wildcard や未解決の環境変数で再帰削除しないでください。

- [Security 原文](SECURITY.md)
- [Privacy 原文](PRIVACY.md)
- [Terms 原文](TERMS.md)
- [日本語サポート](plugins/adaptive-codex-orchestrator/docs/i18n/SUPPORT.ja.md)

## 検証と公開状態

[2026-08-19 のローカル検証記録](plugins/adaptive-codex-orchestrator/docs/VALIDATION.md)では、Windows / Python
3.12.10 で 108 tests（failure 0、意図的 skip 1）、31 policy evals、1,969
package assertions が PASS しています。GitHub Actions は Windows・macOS・
Linux と Python 3.9・3.12 用に設定されていますが、このローカル記録では
remote CI は実行していません。

publisher `battle-doll`、manifest 指定の公開候補 URL、2 個の PNG が記録されて
います。中立な
`assets/logo.png` と `assets/composer-icon.png` を portal の light/dark 4 upload
slots で再利用するものとして指定しています。本 package は skills-only でユーザー向け MCP tool
UI がないため、現在の review scope では product UI screenshot は不要です。
positive 5 件・negative 3 件の [reviewer cases](plugins/adaptive-codex-orchestrator/evals/reviewer-cases.json)も
準備済みです。公開前には各 URL の到達性と内容、legal/trademark review、実際の公開元
からの clean install、当時の portal requirement 再確認が必要です。詳細は
[Submission](plugins/adaptive-codex-orchestrator/docs/i18n/SUBMISSION.ja.md)と[公開レビュー](plugins/adaptive-codex-orchestrator/docs/i18n/PUBLISHING.ja.md)を参照してください。

source は [MIT License](LICENSE) で提供されます。この翻訳は参考情報で
あり、維持されている英語文書、[Terms](TERMS.md)、翻訳されていない
`MIT License` の内容を置き換えません。
