# Deterministic command language

Read this reference when explaining natural-language controls or extending the
parser tests. The hook parser uses no LLM.

## Intents, scopes, and profiles

- Intents: `enable`, `disable`, `status`, `set_profile`
- Scopes: `one-shot`, `session`, `project`, `global`
- Profiles: `conservative`, `balanced`, `fast`
- Default enable scope: `session`
- Default profile: `balanced`

Enablement precedence is `one-shot > session > project > global > disabled`.
A generic disable creates a session OFF override and never deletes a project or
global preference. A profile command without an explicit scope applies to the
session.

## Examples

| Purpose | Korean | English |
| --- | --- | --- |
| Session enable | `솔 울트라 모드 켜줘` | `Turn on Sol Ultra mode` |
| One-shot enable | `이번 작업만 솔 울트라 모드 켜줘` | `Use orchestration for this task only` |
| Project enable | `이 프로젝트에서는 솔 울트라 모드를 항상 켜줘` | `Enable orchestration for this repository` |
| Global enable | `모든 프로젝트에서 기본으로 켜줘` | `Enable orchestration globally` |
| Disable | `솔 울트라 모드 꺼줘` | `Turn off Ultra Orchestration` |
| Profile | `빠른 프로필로 전환해` | `Switch to the fast profile` |
| Status | `오케스트레이션 상태 알려줘` | `Show orchestration status` |

Profile-use wording is also a profile change, not an activation command:
`솔 울트라 모드를 보수적으로 사용해` and `Use the conservative profile`
set the session profile while preserving the current ON/OFF value.

Recognized anchors include Korean `솔 울트라`, `울트라 오케스트레이션`,
`스파크 오케스트레이션`, and `적응형 오케스트레이션`; English `Sol Ultra`,
`Ultra Orchestration`, `Adaptive Orchestration`, and `Spark Orchestration`;
and the explicit `adaptive-orchestration` skill name. A generic application
`모드`/`mode` or unrelated `프로필 상태`/`profile status` is never enough.

## Safety order

1. Normalize Unicode with NFKC, case-fold, and collapse whitespace.
2. Mask fenced code blocks and quoted examples.
3. Detect status before activation words.
4. Detect explicit negation before ordinary disable/enable.
5. Detect scope and profile conflicts.
6. Decide whether a non-control task remains.

Status never mutates state. Material enable/disable conflicts, multiple scopes,
multiple profiles, unknown profile commands, and inactive referential disables
are ambiguous and preserve state. A long pasted prompt is inspected only at
its command-like edges and requires both a known mode alias and action phrase.
Prompt text is never stored, logged, evaluated, or interpolated into a shell
command.

How-to or deliberative questions are informational rather than control
commands and do not change state. Examples include `How do I enable Ultra
Orchestration?`, `Should I enable Ultra Orchestration?`, and the Korean
equivalent asking how to turn the mode on.

Mixed commands take effect in the same turn:

```text
이번 작업만 솔 울트라 모드를 켜고 결제 실패 원인을 찾아서 수정해줘.
```

The one-shot entry is attached to the current turn and cleared by `Stop`; a
later turn also removes a stale one-shot entry when the host skipped completion
cleanup.

## Task-local worker caps

An instruction such as `Use at most one worker for this task` or
`이번 작업에는 작업자를 최대 한 명만 사용해` is a task-local execution
constraint, not persistent control state. It does not change the active profile
or any stored scope. A zero cap or explicit no-worker instruction keeps the
task in the parent. A positive cap can only lower the profile or host limit;
it never raises either limit.
