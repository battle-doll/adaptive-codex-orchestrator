# 发布审核清单

[English](../PUBLISHING.md) · [한국어](PUBLISHING.ko.md) ·
[日本語](PUBLISHING.ja.md) · **简体中文** · [Русский](PUBLISHING.ru.md)

本文是[英文 Publishing Checklist](../PUBLISHING.md)的简体中文说明。如果内容
存在差异，以持续维护的英文原文为准。

## 当前状态

Adaptive Codex Orchestrator `0.1.0` 是尚未发布的 public-review candidate。
仓库内容不代表已经提交、批准、部署或被 marketplace 接受。只有在
所有适用 gate 通过后，repository owner 才能明确执行发布操作。

项目是独立社区工具，不得暗示与 OpenAI 存在隶属、赞助、认可关系或属于
OpenAI 官方产品。

## Package 和公开 metadata

- [ ] 使用当前官方/已安装 validator 检查 `.codex-plugin/plugin.json`。
- [ ] 确认 package folder 和 manifest name 都准确为
      `adaptive-codex-orchestrator`。
- [ ] 确认 manifest、`pyproject.toml`、marketplace、`CHANGELOG.md` 的版本
      一致。
- [ ] 最终确认 manifest 中记录的 publisher/developer `battle-doll` 的所有权和
      展示方式。
- [ ] 确认 manifest 指定为公开候选地址的
      [GitHub 仓库](https://github.com/battle-doll/adaptive-codex-orchestrator)、
      homepage、privacy 和 terms URL 可访问且内容已审核。普通支持使用
      [GitHub Issues](https://github.com/battle-doll/adaptive-codex-orchestrator/issues)，
      敏感安全报告使用[私密安全公告](https://github.com/battle-doll/adaptive-codex-orchestrator/security/advisories/new)；
      使用前分别验证可访问性。
- [ ] 确认 `LICENSE` 与 manifest 的 `MIT` metadata 一致。
- [ ] 当前 validator 拒绝 manifest `hooks` 字段，因此保持默认
      `hooks/hooks.json` discovery。
- [ ] 不添加当前不支持的 `supportURL`、`brandColorDark`。
- [ ] 检查 starter prompts 不夸大能力、长度限制或韩语/英语命令支持范围。

## 资产和证据

- [ ] 确认 `assets/icon.svg`、`assets/logo.svg` 为原创，在小尺寸和明暗背景下
      可识别。
- [ ] 确认没有 OpenAI/ChatGPT logo、复制的 Codex artwork、易混淆外观、
      bundled font 或不可用外部 asset。
- [x] 已准备 `assets/logo.png`（256×256）和 `assets/composer-icon.png`（48×48），并
      保留 SVG source。这 2 个中立 PNG 被指定复用于 4 个 light/dark 上传槽。
- [x] 已记录本包仅包含 skills、没有面向用户的 MCP 工具 UI，因此当前审核范围
      不需要产品 UI 截图。提交时仍需确认门户要求是否变化。
- [ ] 重新运行 [Validation](../VALIDATION.md) 和 [Testing](../TESTING.md) 中的
      unit、hook fixture、state、parser、path、policy eval。
- [x] 已准备包含可复现 setup 和 expected result 的
      [5 个正向与 3 个负向 reviewer cases](../../evals/reviewer-cases.json)。
- [ ] 由人工审核 [Security](../SECURITY.md)、[Privacy](../PRIVACY.md) 和
      [Terms](../TERMS.md)。这些文档不是法律意见。

## 手动测试本地 marketplace

先确认 `.agents/plugins/marketplace.json` 的实际 name 是
`adaptive-codex-orchestrator`。以下命令会更改 Codex 状态，必须由 owner
手动执行。

```text
codex plugin marketplace add <absolute-repository-root>
codex plugin list --marketplace adaptive-codex-orchestrator --available --json
codex plugin add adaptive-codex-orchestrator@adaptive-codex-orchestrator
```

在新的 Codex task 中测试 hook trust、disabled behavior、四种 scopes、三种
profiles、status、cleanup、compatibility mode、bounded delegation 和
`$adaptive-orchestration` fallback。不要对默认 personal marketplace 运行
`marketplace add`。

## 正式提交之前

1. 重新核对当时最新的官方 plugin、hook、subagent、model、public-submission
   schema。
2. 从真实 public source 在 clean environment 中安装测试。
3. 核实 publisher claim 以及所有 public URL 的 ownership、HTTPS、redirect
   和内容。
4. 确认没有 secret、private path、prompt、source fixture、local cachebuster
   或缺失 asset。
5. 最终审核 code、docs、security、privacy、terms、brand、compatibility。
6. 仅在 owner 明确授权后，按当时的官方流程提交。

不能仅因 local validation 通过就把清单标记为完成。

## 仅 owner 可完成的事项

- 最终验证 publisher `battle-doll` 及 manifest 指定公开候选 URL 的所有权、
  可访问性和内容。
- 完成适当的 legal/trademark review。
- 在届时门户确认 2 个 PNG 可以复用于 4 个 light/dark 槽；若仍是 skills-only，
  不制作产品 UI 截图。
- 在门户中人工核对已准备的 5 个正向与 3 个负向 reviewer cases。
- 从真实 public source 在支持平台上进行 clean install test。
- 明确批准 tag、push、release、submission。
- 发布后维护 public support 和 private security-reporting channel。

本翻译不更改 [MIT License](../../LICENSE) 的名称、权利或免责声明，也不替代
[英文原文](../PUBLISHING.md)。
