#!/usr/bin/env python3
"""Current Codex command-hook entry point for Adaptive Codex Orchestrator.

The runtime is intentionally offline, standard-library only, and silent except
for one JSON object on stdout.  It never reads transcript files.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
import re
import sys
import time
from typing import Mapping, MutableMapping, Optional, Tuple


HOOK_DIR = Path(__file__).resolve().parent
if str(HOOK_DIR) not in sys.path:
    sys.path.insert(0, str(HOOK_DIR))

from lib.command_parser import ParseResult, parse_command
from lib.hook_output import context_output, encode_output, empty_output
from lib.policy_loader import (
    ACTIVE_POLICY_REVISION,
    PolicyError,
    compact_reminder,
    load_model_policy,
    worker_contract,
)
from lib.project_identity import project_id
from lib.state_store import (
    SESSION_TTL_SECONDS,
    StateStore,
    StateUnavailableError,
    effective_state,
)


MAX_INPUT_BYTES = 256 * 1024
SUPPORTED_EVENTS = frozenset(
    {"SessionStart", "UserPromptSubmit", "SubagentStart", "Stop", "SessionEnd"}
)
_SAFE_ID_RE = re.compile(r"^[A-Za-z0-9._:@-]{1,256}$")
_SAFE_MODEL_RE = re.compile(r"^[A-Za-z0-9._:-]{1,128}$")


def _safe_identifier(value: object) -> Optional[str]:
    if isinstance(value, str) and _SAFE_ID_RE.fullmatch(value):
        return value
    return None


def _safe_model(value: object) -> Optional[str]:
    if isinstance(value, str) and _SAFE_MODEL_RE.fullmatch(value):
        return value.casefold()
    return None


def _looks_like_sol(model: Optional[str]) -> bool:
    if not model:
        return False
    return model == "gpt-5.6" or model == "gpt-5.6-sol" or model.startswith(
        "gpt-5.6-sol-"
    )


def _compatibility(model: Optional[str]) -> Tuple[bool, str]:
    detected = model or "unavailable"
    return (not _looks_like_sol(model), detected)


def _compatibility_notice() -> str:
    return (
        "Ultra Orchestration is active in compatibility mode. The plugin does not "
        "change the parent model. For the intended behavior, select Sol with the "
        "Ultra setting manually. Ultra reasoning cannot be programmatically verified."
    )


def _storage_diagnostic(event: str) -> dict:
    return context_output(
        event,
        "Adaptive Codex Orchestrator could not access plugin-owned state. No persistent "
        "mode change was applied. Normal Codex behavior continues; invoke "
        "`$adaptive-orchestration <task>` for a current-task-only fallback.",
    )


def _status_text(
    effective: Mapping[str, object], model: Optional[str], configured_worker: str
) -> str:
    compatibility, detected = _compatibility(model)
    enabled = "ON" if effective.get("enabled") else "OFF"
    return "\n".join(
        (
            f"Ultra Orchestration: {enabled}",
            f"Effective scope: {effective.get('effective_scope', 'disabled')}",
            f"State source: {effective.get('state_source', 'disabled')}",
            f"Profile: {effective.get('profile', 'balanced')}",
            f"Configured worker: {configured_worker}",
            f"Parent model detected: {detected}",
            "Ultra reasoning verified: no",
            "Persistent hooks trusted: yes",
            f"Compatibility mode: {'yes' if compatibility else 'no'}",
        )
    )


def _event_context(event: str, *parts: str) -> dict:
    content = "\n\n".join(part.strip() for part in parts if part and part.strip())
    return context_output(event, content) if content else empty_output()


def _project(payload: Mapping[str, object]) -> Optional[str]:
    cwd = payload.get("cwd")
    if not isinstance(cwd, str) or not cwd or len(cwd) > 32768:
        return None
    try:
        return project_id(cwd)
    except (OSError, ValueError, UnicodeError):
        return None


def _session_notice_shown(state: Mapping[str, object], session_id: str) -> bool:
    sessions = state.get("sessions")
    if not isinstance(sessions, Mapping):
        return False
    session = sessions.get(session_id)
    return bool(
        isinstance(session, Mapping) and session.get("compatibility_notice_shown") is True
    )


def _active_policy_shown(state: Mapping[str, object], session_id: str) -> bool:
    sessions = state.get("sessions")
    if not isinstance(sessions, Mapping):
        return False
    session = sessions.get(session_id)
    return bool(
        isinstance(session, Mapping)
        and session.get("active_policy_revision") == ACTIVE_POLICY_REVISION
    )


def _mark_active_policy(store: StateStore, session_id: str) -> None:
    try:
        store.mark_active_policy(session_id, ACTIVE_POLICY_REVISION)
    except StateUnavailableError:
        # Context injection remains safe when the advisory de-duplication marker
        # cannot be written. A later turn may receive the compact policy again.
        pass


def _notice_if_needed(
    *,
    store: StateStore,
    state: Mapping[str, object],
    session_id: str,
    model: Optional[str],
) -> str:
    compatibility, _ = _compatibility(model)
    if not compatibility or _session_notice_shown(state, session_id):
        return ""
    try:
        store.mark_compatibility_notice(session_id)
        return _compatibility_notice()
    except StateUnavailableError:
        return (
            _compatibility_notice()
            + " The once-per-session marker could not be saved, so this notice may recur."
        )


def _active_context(
    *,
    plugin_root: Path,
    effective: Mapping[str, object],
    prefix: str = "",
    notice: str = "",
) -> str:
    policy = compact_reminder(plugin_root, str(effective["profile"]))
    return "\n\n".join(value for value in (prefix, notice, policy) if value)


def _handle_session_start(
    payload: Mapping[str, object],
    *,
    store: StateStore,
    state: Mapping[str, object],
    session_id: str,
    project_hash: str,
    plugin_root: Path,
) -> dict:
    effective = effective_state(state, session_id, project_hash)
    if not effective["enabled"]:
        return empty_output()
    model = _safe_model(payload.get("model"))
    notice = _notice_if_needed(
        store=store, state=state, session_id=session_id, model=model
    )
    source = payload.get("source")
    prefix = (
        "Codex context was compacted; restore the active orchestration policy below."
        if source == "compact"
        else ""
    )
    _mark_active_policy(store, session_id)
    return _event_context(
        "SessionStart",
        _active_context(
            plugin_root=plugin_root,
            effective=effective,
            prefix=prefix,
            notice=notice,
        ),
    )


def _apply_control(
    parsed: ParseResult,
    *,
    store: StateStore,
    session_id: str,
    project_hash: str,
    turn_id: Optional[str],
) -> dict:
    if parsed.intent in {"enable", "disable"}:
        return store.set_enabled(
            scope=parsed.scope or "session",
            enabled=parsed.intent == "enable",
            session_id=session_id,
            project_id=project_hash,
            turn_id=turn_id,
            profile=parsed.profile,
        )
    if parsed.intent == "set_profile" and parsed.profile:
        return store.set_profile(
            scope=parsed.scope or "session",
            profile=parsed.profile,
            session_id=session_id,
            project_id=project_hash,
            turn_id=turn_id,
        )
    raise ValueError("not a control intent")


def _handle_user_prompt(
    payload: Mapping[str, object],
    *,
    store: StateStore,
    state: Mapping[str, object],
    session_id: str,
    project_hash: str,
    plugin_root: Path,
) -> dict:
    prompt = payload.get("prompt")
    if not isinstance(prompt, str):
        return empty_output()
    turn_id = _safe_identifier(payload.get("turn_id"))
    model = _safe_model(payload.get("model"))
    configured_worker = str(load_model_policy(plugin_root)["primary_worker"])
    before = effective_state(state, session_id, project_hash)
    parsed = parse_command(prompt, mode_active=bool(before["enabled"]))

    # Status and ambiguous requests are explicitly read-only, including stale
    # one-shot cleanup and compatibility-notice bookkeeping.
    if parsed.intent == "status":
        return _event_context(
            "UserPromptSubmit", _status_text(before, model, configured_worker)
        )
    if parsed.ambiguous:
        return _event_context(
            "UserPromptSubmit",
            "Ultra Orchestration command was ambiguous; no state changed. "
            f"Reason: {parsed.reason}. State the desired scope/profile explicitly.",
        )

    # If Stop was skipped, consume a one-shot before handling a later turn.
    one_shot = state.get("one_shot", {})
    existing = one_shot.get(session_id) if isinstance(one_shot, Mapping) else None
    if isinstance(existing, Mapping) and (
        not turn_id
        or not existing.get("turn_id")
        or existing.get("turn_id") != turn_id
    ):
        state = store.clear_stale_one_shot(session_id, turn_id)
        before = effective_state(state, session_id, project_hash)
        parsed = parse_command(prompt, mode_active=bool(before["enabled"]))
        if parsed.ambiguous:
            # This ambiguity follows an automatic expiry, not a command change.
            return _event_context(
                "UserPromptSubmit",
                "A completed one-shot expired. The new control wording is ambiguous; no "
                f"new preference was applied. Reason: {parsed.reason}.",
            )

    if parsed.intent is None:
        if not before["enabled"]:
            return empty_output()
        notice = _notice_if_needed(
            store=store, state=state, session_id=session_id, model=model
        )
        if _active_policy_shown(state, session_id):
            return _event_context("UserPromptSubmit", notice)
        _mark_active_policy(store, session_id)
        return _event_context(
            "UserPromptSubmit", notice, compact_reminder(plugin_root, str(before["profile"]))
        )

    if parsed.scope == "project" and project_hash == "0" * 64:
        return _event_context(
            "UserPromptSubmit",
            "No project preference was changed because the host did not provide a usable "
            "working directory. Choose a session or one-shot scope instead.",
        )

    updated = _apply_control(
        parsed,
        store=store,
        session_id=session_id,
        project_hash=project_hash,
        turn_id=turn_id,
    )
    after = effective_state(updated, session_id, project_hash)
    action = {
        "enable": "enabled",
        "disable": "disabled",
        "set_profile": "profile updated",
    }[parsed.intent]
    applied = (
        f"Ultra Orchestration command applied: {action}; requested scope "
        f"{parsed.scope or 'session'}."
    )
    status = _status_text(after, model, configured_worker)

    if after["enabled"]:
        notice = _notice_if_needed(
            store=store, state=updated, session_id=session_id, model=model
        )
        # A new enable or active profile change gets the compact policy. A scoped
        # disable that leaves a higher-precedence ON state gets the same summary.
        if parsed.intent in {"enable", "set_profile"}:
            policy = _active_context(
                plugin_root=plugin_root, effective=after, notice=notice
            )
        else:
            policy = "\n\n".join(
                value
                for value in (
                    notice,
                    "The requested OFF preference was saved, but a higher-precedence ON "
                    "override remains effective for this turn. "
                    + compact_reminder(plugin_root, str(after["profile"])),
                )
                if value
            )
        _mark_active_policy(store, session_id)
        return _event_context("UserPromptSubmit", applied, status, policy)

    return _event_context(
        "UserPromptSubmit",
        applied,
        status,
        "Ultra Orchestration is OFF. Do not apply prior orchestration policy to this "
        "request unless the user explicitly invokes the current-task skill.",
    )


def _handle_subagent_start(
    payload: Mapping[str, object],
    *,
    state: Mapping[str, object],
    session_id: str,
    project_hash: str,
    plugin_root: Path,
) -> dict:
    effective = effective_state(state, session_id, project_hash)
    if not effective["enabled"]:
        return empty_output()
    policy = load_model_policy(plugin_root)
    model = _safe_model(payload.get("model"))
    if model and model != policy["primary_worker"].casefold():
        return empty_output()
    return _event_context(
        "SubagentStart",
        worker_contract(plugin_root, confirmed_spark=model == policy["primary_worker"].casefold()),
    )


def _has_stale_sessions(state: Mapping[str, object], session_id: str) -> bool:
    sessions = state.get("sessions", {})
    if not isinstance(sessions, Mapping):
        return False
    now = int(time.time())
    for key, entry in sessions.items():
        if key == session_id or not isinstance(entry, Mapping):
            continue
        last_seen = entry.get("last_seen")
        if isinstance(last_seen, int) and now - last_seen > SESSION_TTL_SECONDS:
            return True
    return False


def handle_event(
    payload: object,
    *,
    environ: Optional[Mapping[str, str]] = None,
    plugin_root: Optional[Path] = None,
) -> dict:
    """Handle one decoded hook event; exposed for offline fixture tests."""

    if not isinstance(payload, Mapping):
        return empty_output()
    if "schema_version" in payload and payload.get("schema_version") != 1:
        return empty_output()
    event = payload.get("hook_event_name")
    if event not in SUPPORTED_EVENTS:
        return empty_output()
    session_id = _safe_identifier(payload.get("session_id"))
    if not session_id:
        return empty_output()

    environ = environ if environ is not None else os.environ
    plugin_root = Path(plugin_root or environ.get("PLUGIN_ROOT") or HOOK_DIR.parent)
    data_value = environ.get("PLUGIN_DATA")
    if not data_value:
        if event == "UserPromptSubmit":
            parsed = parse_command(payload.get("prompt"), mode_active=False)
            if parsed.intent or parsed.ambiguous:
                return _storage_diagnostic("UserPromptSubmit")
        return empty_output()

    project_hash = _project(payload)
    if not project_hash:
        # Session/global operations remain safe. A fixed all-zero hash is never
        # persisted unless a project-scoped command reaches the explicit guard.
        project_hash = "0" * 64
    store = StateStore.from_data_dir(Path(data_value))
    try:
        # Cleanup hooks use one bounded lock acquisition so their three-second
        # host deadline cannot interrupt a second state-lock wait.
        if event == "Stop":
            store.clear_one_shot(session_id)
            return empty_output()
        if event == "SessionEnd":
            store.clear_session(session_id)
            return empty_output()
        state = store.read()
        if event == "SessionStart":
            sessions = state.get("sessions", {})
            if isinstance(sessions, Mapping) and session_id in sessions:
                state = store.touch_session(session_id)
            if _has_stale_sessions(state, session_id):
                state = store.prune_stale_sessions(keep_session=session_id)
            return _handle_session_start(
                payload,
                store=store,
                state=state,
                session_id=session_id,
                project_hash=project_hash,
                plugin_root=plugin_root,
            )
        if event == "UserPromptSubmit":
            return _handle_user_prompt(
                payload,
                store=store,
                state=state,
                session_id=session_id,
                project_hash=project_hash,
                plugin_root=plugin_root,
            )
        if event == "SubagentStart":
            return _handle_subagent_start(
                payload,
                state=state,
                session_id=session_id,
                project_hash=project_hash,
                plugin_root=plugin_root,
            )
    except (StateUnavailableError, PolicyError, OSError, ValueError, TypeError):
        if event == "UserPromptSubmit":
            parsed = parse_command(payload.get("prompt"), mode_active=False)
            if parsed.intent or parsed.ambiguous:
                return _storage_diagnostic("UserPromptSubmit")
        return empty_output()
    return empty_output()


def _read_stdin() -> object:
    raw = sys.stdin.buffer.read(MAX_INPUT_BYTES + 1)
    if len(raw) > MAX_INPUT_BYTES:
        return None
    try:
        return json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        return None


def main() -> int:
    try:
        result = handle_event(_read_stdin())
        sys.stdout.write(encode_output(result))
        sys.stdout.write("\n")
        return 0
    except Exception:
        # Hooks must never break ordinary Codex work. Avoid stderr/stdout details
        # that might expose host paths or event contents.
        sys.stdout.write("{}\n")
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
