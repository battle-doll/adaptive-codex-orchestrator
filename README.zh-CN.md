# Adaptive Codex Orchestrator

[English](README.md) · [한국어](README.ko.md) ·
[日本語](README.ja.md) · **简体中文** · [Русский](README.ru.md)

> Adaptive Codex Orchestrator 是独立的社区项目。它与 OpenAI 无隶属、赞助
> 或认可关系，也不是 OpenAI 的官方产品。

Adaptive Codex Orchestrator 是面向 Codex 的本地、离线编排工具。确定性的
Python 控制平面负责可选运行模式 **Ultra Orchestration** 的韩语/英语命令、
状态、项目标识和 hook 上下文。用户选择的父模型仍负责理解需求、架构、是否
委派、审查结果、集成、最终验证和最终答复。

当前 `0.1.0` 是公开审核候选版本。GitHub 源码公开、提交 OpenAI 审核、
获得批准以及开发者执行 Publish 是彼此独立的状态；仓库公开并不表示后续
状态已经完成。

## 能做什么，以及明确不做什么

- 在 `${PLUGIN_DATA}/state-v1.json` 中保存 one-shot、session、project 和插件
  全局默认状态。
- 只把边界清楚、可逆且可独立验证的工作视为委派候选。
- 默认 `balanced` profile 每个父模型回合最多 4 个 worker，同时最多 1 个
  writer。
- 只持久化规范化项目根目录的 SHA-256 hash，不保存原始路径。
- 在 hooks 不可用或不受信任时，提供仅对当前任务生效的
  `$adaptive-orchestration <task>`。

插件不会更改父模型、reasoning level、model selector、权限、sandbox 或 Codex
全局配置；不会声称已验证 Ultra reasoning；不会仅因模式开启就创建 worker；
不会在 host 未确认时声称实际使用了 `gpt-5.3-codex-spark`。控制平面不需要 API
key、OAuth、外部账号、telemetry 或网络请求，也不保存 prompt、transcript、
source code 或原始绝对项目路径。

## 支持范围

已核对的目标是 Codex app 和 CLI。持久化自然语言状态需要 host 支持并由用户
信任的 hooks。不能假设普通 ChatGPT 会话会执行本地 Codex hooks、提供
`PLUGIN_DATA`、相同的清理事件或 subagent 设置。已核对的契约不支持在 Codex
IDE extension 中使用插件。

为获得预期体验，用户需要手动选择 Sol 和 Ultra reasoning/intelligence
设置。插件不会代替用户选择，也无法可靠验证 Ultra 设置。详见
[Compatibility](plugins/adaptive-codex-orchestrator/docs/COMPATIBILITY.md)。

## 本地安装

manifest 已记录发布者 `battle-doll`，并将
[GitHub 仓库](https://github.com/battle-doll/adaptive-codex-orchestrator)以及
homepage、privacy、terms URL 指定为公开候选地址。这不表示已经发布；使用或
提交前必须验证所有地址可访问且内容经过审核。安装前请审查 `.codex-plugin/plugin.json`、
`hooks/hooks.json` 和 `hooks/runtime.py`，并决定是否信任 hooks。

repository owner 核对 `.agents/plugins/marketplace.json` 的实际值后，手动执行
以下命令。这些命令会更改 Codex 状态。

```text
codex plugin marketplace add <absolute-repository-root>
codex plugin list --marketplace adaptive-codex-orchestrator --available --json
codex plugin add adaptive-codex-orchestrator@adaptive-codex-orchestrator
```

安装或重装后，请在新的 Codex task 中测试。默认 personal marketplace 会被
自动发现，不应对该路径运行 `marketplace add`。

## 控制命令

当前确定性命令识别**仅支持韩语和英语**。中文文档不代表支持中文控制命令。
可以使用以下英语命令：

```text
Turn on Ultra Orchestration for this session.
Use Ultra Orchestration for this task only.
Enable Ultra Orchestration for this repository.
Enable Ultra Orchestration globally.
Switch to the fast profile.
Show orchestration status.
Turn off Ultra Orchestration.
```

status 查询不会修改状态。明确否定、冲突的 scope/profile、引用内容、代码块
以及长文本中偶然出现的示例会按安全规则处理。控制命令和实际任务可以在同一
回合生效。

状态优先级：

```text
one-shot > session > project > global > disabled
```

未指定 scope 的一般关闭操作会写入 session OFF override，而不会删除 project
或 global preference。

| Profile | 每个父模型回合的 worker | 并发 writer | 委派重试 |
| --- | ---: | ---: | ---: |
| `conservative` | 2 | 1 | 0；仅在明确可恢复时为 1 |
| `balanced` | 4 | 1 | 1 |
| `fast` | 6 | 通常 1；完全隔离时才可为 2 | 1 |

更低的 host limit 优先。`fast` 的两个 writer 例外仅适用于文件所有权完全
分离、不同 worktree 或经父模型验证的 production/test 隔离。

## 委派策略

文件和 symbol 定位、有限 call path 跟踪、聚焦的失败分析、已确认的小改动、
focused tests 和机械性修改等边界明确的文本任务适合快速 worker。架构、模糊
根因、authentication/authorization/cryptography、数据库迁移、破坏性操作、
public API、主要依赖、复杂并发、集成和最终验证判断必须由父模型负责。

默认禁止 nested delegation。每个 worker 都必须收到包含 scope、允许文件、
禁止行为、证据和验证要求的有界契约。父模型审查每个结果，并且只报告实际
创建的 worker。

## 安全、隐私和状态重置

控制平面是本地 standard-library code，不发出外部网络请求。state 仅包含
mode/profile、hash 后的 project key、session key 和 lifecycle flag。prompt
只在当前 event 的内存中解析，不会写入日志或 state。

重置时先结束相关 session，取得 host 为 `adaptive-codex-orchestrator` 分配的
准确 `PLUGIN_DATA` 路径。确认它是插件专用目录，而不是 plugin source、
repository root、home、`.codex` root 或共享父目录，然后只删除该专用目录或
其中的 `state-v1.json`。不要使用 wildcard 或未解析的环境变量执行递归删除。

- [Security 原文](SECURITY.md)
- [Privacy 原文](PRIVACY.md)
- [Terms 原文](TERMS.md)
- [简体中文支持](plugins/adaptive-codex-orchestrator/docs/i18n/SUPPORT.zh-CN.md)

## 验证和发布状态

[2026-08-19 本地验证记录](plugins/adaptive-codex-orchestrator/docs/VALIDATION.md)记载：Windows / Python 3.12.10
下运行 108 个 tests（0 failure，1 个有意 skip）、31 个 policy evals 和 1,969
个 package assertions，全部 PASS。GitHub Actions 配置了 Windows、macOS、
Linux 以及 Python 3.9、3.12，但本地记录没有执行远程 CI。

发布者 `battle-doll`、manifest 指定的公开候选 URL 和 2 个 PNG 已记录。中立的
`assets/logo.png` 与 `assets/composer-icon.png` 被指定分别复用于门户的 4 个
light/dark 上传槽。本包仅包含 skills，没有面向用户的 MCP 工具 UI，因此在当前
审核范围内不需要产品 UI 截图。包含 5 个正向和 3 个负向的
[审核案例](plugins/adaptive-codex-orchestrator/evals/reviewer-cases.json)也已准备好。发布前仍需确认各 URL 的
可访问性与内容、完成法律/商标审核、从真实公开来源执行干净安装，并重新核对届时门户要求。
详见[提交记录](plugins/adaptive-codex-orchestrator/docs/i18n/SUBMISSION.zh-CN.md)和[发布审核](plugins/adaptive-codex-orchestrator/docs/i18n/PUBLISHING.zh-CN.md)。

源码按 [MIT License](LICENSE) 提供。本翻译仅供参考，不替代维护中的
英文文档、[Terms](TERMS.md)或未翻译的 `MIT License` 正文。
