# 支持

[English](SUPPORT.md) · [한국어](SUPPORT.ko.md) ·
[日本語](SUPPORT.ja.md) · **简体中文** · [Русский](SUPPORT.ru.md)

> 2026-08-29 已验证：`0.1.0` 已 Published，远程目录记录为
> `GLOBAL` / `AVAILABLE` / `UNLISTED`。`0.1.1` 是尚未提交的更新候选版本。
> [GitHub Issues](https://github.com/battle-doll/adaptive-codex-orchestrator/issues)
> 提供尽力而为的一般支持，不承诺响应时间。

本项目是独立社区工具，不是 OpenAI 的官方产品，也未获得 OpenAI 的隶属、
赞助或认可。支持按 best effort 提供，不能替代专业 security、legal、privacy
或 production review。

## 请求帮助之前

请先阅读 [README](README.zh-CN.md)、[Compatibility](../COMPATIBILITY.md)、
[Security](../SECURITY.md)、[Privacy](../PRIVACY.md)和
[Validation](../VALIDATION.md)，并准备：

- plugin version 和 operating system
- 使用 Codex app 还是 CLI
- 是否审查并在 host 中信任 `hooks/hooks.json`
- 问题发生在 persistent hooks 还是 `$adaptive-orchestration <task>` fallback
- expected/observed behavior、minimal reproduction 和相关 validation output

不要发布 credential、API key、private prompt/transcript、proprietary source、
repository content、account identifier 或 private absolute path。

## 常见问题

- **模式不能持久化：**需要 supported/trusted hooks 和可写的 `PLUGIN_DATA`。
  hooks 不可用时，仅对当前 task 使用 `$adaptive-orchestration <task>`。
- **出现 compatibility notice：**插件不会更改父模型。请手动选择目标父模型和
  Ultra setting。插件不会声称 Ultra 已验证。
- **Spark 未确认：**host 可能不提供 `gpt-5.3-codex-spark` availability 或
  model identity。每个委派 subtask 只尝试一次 spawn。若失败、达到限制或不受
  支持，不得 retry，也不得替换为 host-default model；应立即交回父模型。
- **Git/project identity 失败：**fallback 为规范化 working directory 的
  SHA-256 digest，不保存原始路径。
- **state 损坏或不可写：**普通 Codex behavior 会继续。保留的损坏 backup
  可能包含任意字节，应视为可能敏感的本地证据。

## 安全重置状态

结束相关 session，取得 host 为 `adaptive-codex-orchestrator` 分配的准确
`PLUGIN_DATA`。确认它是插件专用目录，而不是 source、repository root、home、
`.codex` root 或共享父目录，然后只删除该目录或其中的 `state-v1.json`。
不要把 wildcard、未解析的 environment variable 或共享目录作为递归删除目标。

## 报告安全漏洞

不要在 public issue 中公开 exploit detail、credential、prompt、proprietary
source 或 private path。指定的安全报告候选渠道是
[私密 GitHub 安全公告](https://github.com/battle-doll/adaptive-codex-orchestrator/security/advisories/new)，
但使用前必须确认功能已启用且可以访问。若不可用，请保留敏感细节并先向
maintainer 请求私密渠道。

请提供 affected version、platform/Codex surface、minimal reproduction、impact
以及是否需要 trusted hooks。在 maintainer 发布明确政策前，不承诺响应时间。
权威流程见 [Security 原文](../SECURITY.md)。

## 发布状态

manifest 已记录发布者 `battle-doll`，并将
[GitHub 仓库](https://github.com/battle-doll/adaptive-codex-orchestrator)、
website、privacy 和 terms 指定为公开候选地址。GitHub Issues 是普通支持候选
渠道，私密安全公告是安全报告候选渠道。该指定不证明地址可用或插件已发布，使用
前必须验证。只有 owner 完成
[发布审核](PUBLISHING.zh-CN.md)、验证所有地址并明确授权后，才能将其描述为
已在 marketplace 发布或获得批准。

控制命令仅识别韩语和英语。本文翻译不增加日语、简体中文或俄语命令支持。

如果翻译与英文来源不一致，以[英文 Support](SUPPORT.md)、
[Terms](../TERMS.md)和未翻译的 [MIT License](../../LICENSE)为准。
