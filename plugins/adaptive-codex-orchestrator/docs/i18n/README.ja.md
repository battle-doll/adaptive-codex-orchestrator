# Adaptive Codex Orchestrator

[English](../../README.md) · [한국어](README.ko.md) · **日本語** ·
[简体中文](README.zh-CN.md) · [Русский](README.ru.md)

Codex が限定された作業をいつ委任するかを明示的に制御できます。タスク、
セッション、プロジェクト、グローバルのスコープとプロファイルを選び、親の
レビューと安全な並列実行を維持します。すべての作業を自動でマルチエージェント
化するものではなく、必要なときだけ委任を制御したい開発者向けです。

> 公開状況（2026-08-29 確認）: [v0.1.0 は Published](https://chatgpt.com/plugins/plugins_6a86354985fc8191b33d2795e2851821)、
> リモートカタログでは `GLOBAL` / `AVAILABLE` / `UNLISTED` です。初回公開日は
> 不明です。v0.1.1 は未提出の更新候補です。

## インストールまたは使用

- 正確な[公開済み v0.1.0 プラグインページ](https://chatgpt.com/plugins/plugins_6a86354985fc8191b33d2795e2851821)を
  開きます。`UNLISTED` はディレクトリ検索・閲覧面への掲載を意味しません。
- `hooks/hooks.json` と `hooks/runtime.py` を確認し、下の source installation
  手順に従います。
- この package source は v0.1.1 候補で、現在公開済みの package ではありません。

## 試す

```text
Use orchestration for this task only: inspect three independent modules without editing, then summarize the evidence.
Show orchestration status, scope, and profile.
```

## 主要な境界

- enable、disable、status、scope、profile、または `$adaptive-orchestration`
  という明示的制御だけが対象で、製品名は不要です。
- 通常の並列化可能な作業、回答スタイル、メンターモード、学習、助言、
  ブレインストーミング、批評は起動しません。
- 要件、設計、統合、検証、最終回答は親が所有し、同時 writer は最大 1 です。
- 選択済みの親 model、reasoning level、権限、承認、sandbox、network を変更
  せず、prompt、会話、source、raw path を保存しません。worker model の
  request は bundled policy に従います。

> Adaptive Codex Orchestrator は独立したコミュニティプロジェクトです。
> OpenAI と提携しておらず、OpenAI が後援・推奨する公式製品でもありません。

## 主な機能と境界

- 1 回限り、セッション、プロジェクト、プラグイン全体の既定値を
  `${PLUGIN_DATA}/state-v1.json` に保存します。
- 範囲が限定され、可逆で、独立して検証可能な作業だけを委任候補にします。
- 既定の `balanced` プロファイルでは、親ターンあたり最大 4 worker、同時
  writer は 1 です。
- 有効な session には compact policy を渡し、数値の
  `active_policy_revision` により通常ターンで同じ revision の反復を抑止します。
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
できません。詳細は [Compatibility](../COMPATIBILITY.md) を参照してください。

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

| Profile | Worker ceiling/parent turn | Concurrent writers | Spawn attempts/subtask | Delegated retry |
| --- | ---: | ---: | ---: | ---: |
| `conservative` | 2 | 1 | 1 | 0 |
| `balanced` | 4 | 1 | 1 | 0 |
| `fast` | 6 | 1 | 1 | 0 |

Profile 値は目標ではなく上限です。実効上限は profile、より低い host/user
上限、独立して有用な task 数、task 固有の safety cap の最小値です。単純または
明確な single-file edit と根拠のない完了報告の確認は 0 worker です。ローカルで
再現可能な bug も既定は 0 で、独立証拠が実質的に役立つ場合だけ read-only
Explorer を最大 1 使用できます。小さく明確な 4 組の独立 module-test も既定は
0 です。各 slice に相当量の独立証拠が必要で、予想される節約が spawn と統合の
コストを明確に上回る場合だけ、分離した read-only Explorer を最大 2 使用します。
shared-state、authentication、authorization、permission、tenant の作業は
read-only Explorer を最大 1 とし、親だけが書き込みます。すべての profile で
concurrent writer は最大 1 です。

## 委任ポリシー

ファイル・symbol 探索、限定的な call path 追跡、狭い failure 分析、確認済み
の小さな修正、focused test、機械的変更のような境界の明確な text task が
高速 worker の候補です。architecture、曖昧な root-cause、認証・認可・
暗号、database migration、破壊的操作、public API、主要 dependency、複雑な
concurrency、統合、最終検証判断は親が担当します。

Nested delegation は例外なく禁止されます。Compact gate が実際の委任 task
を選んだ後に限り、詳細な routing、worker-contract、model reference を 1 回
読み込みます。各 subtask は Spark spawn を 1 回だけ試み、失敗、limit、明示
model 非対応なら retry や host-default 置換なしで親へ戻します。Requested model
と reasoning は host-confirmed active model と区別し、開始時の model report は
completion や billing の証明ではありません。

各 worker は `conclusion`、`evidence`、`files_and_lines`、`tests_or_checks`、
`risks`、`recommended_parent_action` の正確な 6 top-level fields だけを返します。
親は全結果をレビューし、引用証拠、gap、conflict を spot-check できますが、同じ
広範な探索を最初から最後まで繰り返しません。実際に作成した worker だけを
報告します。

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

- [Security 原文](../SECURITY.md)
- [Privacy 原文](../PRIVACY.md)
- [Terms 原文](../TERMS.md)
- [日本語サポート](SUPPORT.ja.md)

## 検証と公開状態

[2026-08-29 のローカル検証記録](../VALIDATION.md)では、Windows / Python
3.12.10 で 112 tests（failure 0、意図的 skip 1）、31 policy evals、2,447
package assertions が PASS しています。GitHub Actions は Windows・macOS・
Linux と Python 3.9・3.12 用に設定されていますが、このローカル記録では
remote CI は実行していません。

publisher `battle-doll`、manifest 指定の公開候補 URL、2 個の PNG が記録されて
います。中立な
`assets/logo.png` と `assets/composer-icon.png` を portal の light/dark 4 upload
slots で再利用するものとして指定しています。本 package は skills-only でユーザー向け MCP tool
UI がないため、現在の review scope では product UI screenshot は不要です。
positive 5 件・negative 3 件の [reviewer cases](../../evals/reviewer-cases.json)も
準備済みです。公開前には各 URL の到達性と内容、legal/trademark review、実際の公開元
からの clean install、当時の portal requirement 再確認が必要です。詳細は
[Submission](SUBMISSION.ja.md)と[公開レビュー](PUBLISHING.ja.md)を参照してください。

source は [MIT License](../../LICENSE) で提供されます。この翻訳は参考情報で
あり、維持されている英語文書、[Terms](../TERMS.md)、翻訳されていない
`MIT License` の内容を置き換えません。
