# 公开提交记录

[English](SUBMISSION.md) · [한국어](SUBMISSION.ko.md) · [日本語](SUBMISSION.ja.md) ·
**简体中文** · [Русский](SUBMISSION.ru.md)

审核日期：**2026-08-29**

状态：**v0.1.0 已 Published，远程目录为 `GLOBAL` / `AVAILABLE` /
`UNLISTED`；v0.1.1 是尚未提交的更新候选版本**。

准确的 v0.1.0 页面为
<https://chatgpt.com/plugins/plugins_6a86354985fc8191b33d2795e2851821>。
首次发布日期未知，不声称具有 LISTED 状态。

本文是公开审核摘要。详细的所有者门槛见[发布清单](../PUBLISHING.md)，已执行的
本地证据见[验证记录](../VALIDATION.md)。本文不授权 tag、push、release、部署、
marketplace 注册或外部提交。

## 提交元数据

英文版的[准确门户列表值](SUBMISSION.md#exact-portal-listing-candidate)逐项反映当前
manifest。关键值如下：

- 包 `adaptive-codex-orchestrator`，版本 `0.1.1`
- 显示名称 `Adaptive Codex Orchestrator`
- 副标题 `Explicit bounded orchestration`
- 发布者 `battle-doll`，类别 `Developer Tools`，许可证 `MIT`
- 运行模式 `Ultra Orchestration`，请求工作器 `gpt-5.3-codex-spark`
- 颜色 `#7168E8`，`./assets/composer-icon.png`（48×48），`./assets/logo.png`（256×256）。
  2 个中立 PNG 复用于 4 个 light/dark 上传槽，不创建额外 PNG
- 控制命令语言：仅韩语和英语

英文版还包含准确的 long description、8 项 capability、3 条 starter prompt 和
拟定 release note。提交前必须与当时的官方门户架构重新核对。

## 指定的公开候选地址

manifest 记录的发布者为 [battle-doll](https://github.com/battle-doll)。
repository/website 候选地址为
[GitHub 仓库](https://github.com/battle-doll/adaptive-codex-orchestrator)，
homepage 为 [README](https://github.com/battle-doll/adaptive-codex-orchestrator#readme)，
privacy 为 [PRIVACY.md](https://github.com/battle-doll/adaptive-codex-orchestrator/blob/main/PRIVACY.md)，
terms 为 [TERMS.md](https://github.com/battle-doll/adaptive-codex-orchestrator/blob/main/TERMS.md)，
公开支持政策为 [SUPPORT.md](https://github.com/battle-doll/adaptive-codex-orchestrator/blob/main/SUPPORT.md)，
普通支持候选渠道为 [GitHub Issues](https://github.com/battle-doll/adaptive-codex-orchestrator/issues)，
敏感安全报告候选渠道为
[私密 GitHub 安全公告](https://github.com/battle-doll/adaptive-codex-orchestrator/security/advisories/new)。

该指定不证明地址可访问、内容已审核或已经发布。使用前和提交前必须验证 HTTPS、
所有权、内容和私密安全公告功能是否启用，且不得在 Issues 中发送敏感信息。

## 审核证据与剩余门槛

[审核案例](../../evals/reviewer-cases.json)准确包含 **5 个正向和 3 个负向案例**，
并带有可复现设置与预期行为。它们不能替代包含 31 个场景的离线政策数据集。

所有者必须重新核对最新 manifest、hook、skill、model、asset、screenshot、法律
链接和门户要求，并验证发布者、URL、`MIT License`、版本、2 个 PNG 的 4 槽复用、
政策和 release note。当前仅包含 skills，没有面向用户的 MCP 工具 UI，因此不需
产品 UI 截图。还需运行完整离线验证，从真实公开来源执行干净安装，并在明确批准后
仅通过当时的官方流程提交。本地验证不等于 marketplace 批准。

控制命令仅识别韩语和英语。本文翻译不增加日语、简体中文或俄语命令支持。
