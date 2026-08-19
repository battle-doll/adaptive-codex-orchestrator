"""Small adapters for current Codex hook output JSON."""

from __future__ import annotations

import json
from typing import Mapping


CONTEXT_EVENTS = frozenset({"SessionStart", "UserPromptSubmit", "SubagentStart"})


def empty_output() -> dict:
    return {}


def context_output(event: str, context: str) -> dict:
    if event not in CONTEXT_EVENTS:
        raise ValueError("event does not accept hook-specific context")
    if not isinstance(context, str) or not context.strip():
        return {}
    return {
        "hookSpecificOutput": {
            "hookEventName": event,
            "additionalContext": context.strip(),
        }
    }


def is_valid_output(value: object) -> bool:
    if not isinstance(value, Mapping):
        return False
    if not value:
        return True
    specific = value.get("hookSpecificOutput")
    if not isinstance(specific, Mapping):
        return False
    return (
        specific.get("hookEventName") in CONTEXT_EVENTS
        and isinstance(specific.get("additionalContext"), str)
        and bool(specific["additionalContext"].strip())
    )


def encode_output(value: Mapping[str, object]) -> str:
    if not is_valid_output(value):
        raise ValueError("invalid hook output")
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"))


__all__ = ["CONTEXT_EVENTS", "context_output", "empty_output", "encode_output", "is_valid_output"]
