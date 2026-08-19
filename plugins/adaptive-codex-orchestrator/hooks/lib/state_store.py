"""Versioned plugin-owned state with atomic writes and best-effort locking."""

from __future__ import annotations

from contextlib import contextmanager
import copy
import hashlib
import json
import os
from pathlib import Path
import stat
import tempfile
import time
from typing import Callable, Dict, Iterator, Mapping, MutableMapping, Optional


SCHEMA_VERSION = 1
PROFILES = frozenset({"conservative", "balanced", "fast"})
SESSION_TTL_SECONDS = 30 * 24 * 60 * 60
# Leave enough headroom for a short burst of durable, fsync-backed updates on
# slower hosts while keeping lock failures bounded and fail-safe.
STATE_LOCK_TIMEOUT_SECONDS = 2.0


class StateUnavailableError(RuntimeError):
    """Raised when plugin-owned state cannot be read or written safely."""


class StateValidationError(ValueError):
    """Raised for an unsupported state schema."""


def default_state() -> dict:
    return {
        "schema_version": SCHEMA_VERSION,
        "global": {
            "enabled": False,
            "profile": "balanced",
            "configured": False,
        },
        "projects": {},
        "sessions": {},
        "one_shot": {},
    }


def _optional_entry(value: object, *, session: bool = False, one_shot: bool = False) -> dict:
    if not isinstance(value, Mapping):
        return {}
    result: dict = {}
    if isinstance(value.get("enabled"), bool):
        result["enabled"] = value["enabled"]
    if value.get("profile") in PROFILES:
        result["profile"] = value["profile"]
    if session:
        result["compatibility_notice_shown"] = bool(
            value.get("compatibility_notice_shown", False)
        )
        touched = value.get("last_seen")
        if isinstance(touched, int) and touched >= 0:
            result["last_seen"] = touched
        policy_revision = value.get("active_policy_revision")
        if isinstance(policy_revision, int) and 0 < policy_revision <= 1000:
            result["active_policy_revision"] = policy_revision
    if one_shot:
        turn_id = value.get("turn_id")
        if isinstance(turn_id, str) and 0 < len(turn_id) <= 256:
            result["turn_id"] = turn_id
    return result


def migrate_state(value: object) -> dict:
    """Migrate supported historical shapes and reject future versions."""

    if not isinstance(value, Mapping):
        raise StateValidationError("state root must be an object")
    version = value.get("schema_version", 0)
    if version == 0:
        # Pre-release state used a boolean top-level enabled value.
        migrated = default_state()
        if isinstance(value.get("enabled"), bool):
            migrated["global"]["enabled"] = value["enabled"]
            migrated["global"]["configured"] = True
        if value.get("profile") in PROFILES:
            migrated["global"]["profile"] = value["profile"]
            migrated["global"]["configured"] = True
        return migrated
    if version != SCHEMA_VERSION:
        raise StateValidationError(f"unsupported state schema: {version!r}")
    return dict(value)


def sanitize_state(value: object) -> dict:
    value = migrate_state(value)
    result = default_state()

    global_value = value.get("global")
    if isinstance(global_value, Mapping):
        if isinstance(global_value.get("enabled"), bool):
            result["global"]["enabled"] = global_value["enabled"]
        if global_value.get("profile") in PROFILES:
            result["global"]["profile"] = global_value["profile"]
        configured = global_value.get("configured")
        if isinstance(configured, bool):
            result["global"]["configured"] = configured
        elif "enabled" in global_value or "profile" in global_value:
            # Preserve the semantics of v1 pre-marker state.
            result["global"]["configured"] = True

    projects = value.get("projects")
    if isinstance(projects, Mapping):
        for key, entry in projects.items():
            if isinstance(key, str) and len(key) == 64 and all(
                character in "0123456789abcdef" for character in key
            ):
                cleaned = _optional_entry(entry)
                if cleaned:
                    result["projects"][key] = cleaned

    sessions = value.get("sessions")
    if isinstance(sessions, Mapping):
        for key, entry in sessions.items():
            if isinstance(key, str) and 0 < len(key) <= 256:
                cleaned = _optional_entry(entry, session=True)
                if cleaned:
                    result["sessions"][key] = cleaned

    one_shot = value.get("one_shot")
    if isinstance(one_shot, Mapping):
        for key, entry in one_shot.items():
            if isinstance(key, str) and 0 < len(key) <= 256:
                cleaned = _optional_entry(entry, one_shot=True)
                if cleaned:
                    result["one_shot"][key] = cleaned
    return result


def effective_state(state: Mapping[str, object], session_id: str, project_id: str) -> dict:
    """Resolve independent enabled/profile values by documented precedence."""

    clean = sanitize_state(state)
    layers = (
        ("one-shot", clean["one_shot"].get(session_id, {})),
        ("session", clean["sessions"].get(session_id, {})),
        ("project", clean["projects"].get(project_id, {})),
        (
            "global",
            clean["global"] if clean["global"].get("configured") else {},
        ),
    )
    enabled = False
    enabled_source = "disabled"
    profile = "balanced"
    profile_source = "default"
    for name, layer in layers:
        if "enabled" in layer:
            enabled = layer["enabled"]
            enabled_source = name
            break
    for name, layer in layers:
        if "profile" in layer:
            profile = layer["profile"]
            profile_source = name
            break
    return {
        "enabled": enabled,
        "profile": profile,
        "effective_scope": enabled_source,
        "state_source": enabled_source,
        "profile_source": profile_source,
    }


class _CrossPlatformLock:
    def __init__(
        self, path: Path, timeout: float = STATE_LOCK_TIMEOUT_SECONDS
    ) -> None:
        self.path = path
        self.timeout = timeout
        self.handle = None

    def __enter__(self) -> "_CrossPlatformLock":
        try:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            self.handle = self.path.open("a+b")
            deadline = time.monotonic() + self.timeout
            while True:
                try:
                    if os.name == "nt":
                        import msvcrt

                        self.handle.seek(0)
                        msvcrt.locking(self.handle.fileno(), msvcrt.LK_NBLCK, 1)
                    else:
                        import fcntl

                        fcntl.flock(self.handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
                    # Windows byte-range locks work on an empty file. Initialize
                    # the sentinel only after acquiring the lock so concurrent
                    # first-open callers never write through another lock.
                    self.handle.seek(0, os.SEEK_END)
                    if self.handle.tell() == 0:
                        self.handle.write(b"\0")
                        self.handle.flush()
                    return self
                except (BlockingIOError, OSError):
                    if time.monotonic() >= deadline:
                        raise StateUnavailableError("timed out waiting for state lock")
                    time.sleep(0.02)
        except StateUnavailableError:
            self._close()
            raise
        except OSError as exc:
            self._close()
            raise StateUnavailableError("plugin state lock is unavailable") from exc

    def _close(self) -> None:
        if self.handle is not None:
            self.handle.close()
            self.handle = None

    def __exit__(self, exc_type, exc, traceback) -> None:
        if self.handle is None:
            return
        try:
            if os.name == "nt":
                import msvcrt

                self.handle.seek(0)
                msvcrt.locking(self.handle.fileno(), msvcrt.LK_UNLCK, 1)
            else:
                import fcntl

                fcntl.flock(self.handle.fileno(), fcntl.LOCK_UN)
        finally:
            self._close()


class StateStore:
    """Read and mutate `${PLUGIN_DATA}/state-v1.json` safely."""

    def __init__(self, path: Path) -> None:
        self.path = Path(path)
        self.lock_path = self.path.with_name(self.path.name + ".lock")

    @classmethod
    def from_data_dir(cls, data_dir: Path) -> "StateStore":
        return cls(Path(data_dir) / "state-v1.json")

    def _backup(self, raw: bytes) -> None:
        digest = hashlib.sha256(raw).hexdigest()[:16]
        target = self.path.with_name(f"state-v1.corrupt-{digest}.json")
        if target.exists():
            return
        try:
            target.write_bytes(raw)
            self._restrict(target)
        except OSError as exc:
            raise StateUnavailableError("could not preserve malformed state") from exc

    def _read_unlocked(self) -> dict:
        if not self.path.exists():
            return default_state()
        try:
            raw = self.path.read_bytes()
        except OSError as exc:
            raise StateUnavailableError("plugin state is unreadable") from exc
        try:
            parsed = json.loads(raw.decode("utf-8"))
            return sanitize_state(parsed)
        except (UnicodeDecodeError, json.JSONDecodeError, StateValidationError, TypeError, ValueError):
            self._backup(raw)
            return default_state()

    @staticmethod
    def _restrict(path: Path) -> None:
        if os.name != "nt":
            try:
                path.chmod(stat.S_IRUSR | stat.S_IWUSR)
            except OSError:
                pass

    def _write_unlocked(self, state: object) -> None:
        clean = sanitize_state(state)
        serialized = (json.dumps(clean, ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode(
            "utf-8"
        )
        try:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            descriptor, name = tempfile.mkstemp(
                prefix=".state-v1-", suffix=".tmp", dir=str(self.path.parent)
            )
            temporary = Path(name)
            try:
                with os.fdopen(descriptor, "wb") as handle:
                    handle.write(serialized)
                    handle.flush()
                    os.fsync(handle.fileno())
                self._restrict(temporary)
                os.replace(temporary, self.path)
                self._restrict(self.path)
            finally:
                try:
                    temporary.unlink(missing_ok=True)
                except OSError:
                    pass
        except OSError as exc:
            raise StateUnavailableError("plugin state is not writable") from exc

    def read(self) -> dict:
        with _CrossPlatformLock(self.lock_path):
            return copy.deepcopy(self._read_unlocked())

    def update(self, mutate: Callable[[MutableMapping[str, object]], None]) -> dict:
        with _CrossPlatformLock(self.lock_path):
            state = self._read_unlocked()
            mutate(state)
            clean = sanitize_state(state)
            self._write_unlocked(clean)
            return copy.deepcopy(clean)

    def set_enabled(
        self,
        *,
        scope: str,
        enabled: bool,
        session_id: str,
        project_id: str,
        turn_id: Optional[str] = None,
        profile: Optional[str] = None,
    ) -> dict:
        if scope not in {"one-shot", "session", "project", "global"}:
            raise ValueError("invalid scope")
        if profile is not None and profile not in PROFILES:
            raise ValueError("invalid profile")

        def mutate(state: MutableMapping[str, object]) -> None:
            if scope == "global":
                entry = state["global"]
                entry["configured"] = True
            elif scope == "project":
                entry = state["projects"].setdefault(project_id, {})
            elif scope == "session":
                entry = state["sessions"].setdefault(
                    session_id, {"compatibility_notice_shown": False}
                )
                entry["last_seen"] = int(time.time())
            else:
                entry = state["one_shot"].setdefault(session_id, {})
                if turn_id:
                    entry["turn_id"] = turn_id
            entry["enabled"] = bool(enabled)
            if profile is not None:
                entry["profile"] = profile

        return self.update(mutate)

    def set_profile(
        self,
        *,
        scope: str,
        profile: str,
        session_id: str,
        project_id: str,
        turn_id: Optional[str] = None,
    ) -> dict:
        if scope not in {"one-shot", "session", "project", "global"}:
            raise ValueError("invalid scope")
        if profile not in PROFILES:
            raise ValueError("invalid profile")

        def mutate(state: MutableMapping[str, object]) -> None:
            if scope == "global":
                entry = state["global"]
                entry["configured"] = True
            elif scope == "project":
                entry = state["projects"].setdefault(project_id, {})
            elif scope == "one-shot":
                entry = state["one_shot"].setdefault(session_id, {})
                if turn_id:
                    entry["turn_id"] = turn_id
            else:
                entry = state["sessions"].setdefault(
                    session_id, {"compatibility_notice_shown": False}
                )
                entry["last_seen"] = int(time.time())
            entry["profile"] = profile

        return self.update(mutate)

    def mark_compatibility_notice(self, session_id: str) -> dict:
        def mutate(state: MutableMapping[str, object]) -> None:
            entry = state["sessions"].setdefault(
                session_id, {"compatibility_notice_shown": False}
            )
            entry["compatibility_notice_shown"] = True
            entry["last_seen"] = int(time.time())

        return self.update(mutate)

    def mark_active_policy(self, session_id: str, revision: int) -> dict:
        if not isinstance(revision, int) or not 0 < revision <= 1000:
            raise ValueError("invalid active policy revision")

        def mutate(state: MutableMapping[str, object]) -> None:
            entry = state["sessions"].setdefault(
                session_id, {"compatibility_notice_shown": False}
            )
            entry["active_policy_revision"] = revision
            entry["last_seen"] = int(time.time())

        return self.update(mutate)

    def touch_session(self, session_id: str) -> dict:
        def mutate(state: MutableMapping[str, object]) -> None:
            entry = state["sessions"].get(session_id)
            if isinstance(entry, MutableMapping):
                entry["last_seen"] = int(time.time())

        return self.update(mutate)

    def clear_one_shot(self, session_id: str) -> dict:
        with _CrossPlatformLock(self.lock_path):
            state = self._read_unlocked()
            if session_id not in state["one_shot"]:
                return copy.deepcopy(state)
            state["one_shot"].pop(session_id, None)
            clean = sanitize_state(state)
            self._write_unlocked(clean)
            return copy.deepcopy(clean)

    def clear_stale_one_shot(
        self, session_id: str, turn_id: Optional[str]
    ) -> dict:
        def mutate(state: MutableMapping[str, object]) -> None:
            entry = state["one_shot"].get(session_id)
            stored_turn = entry.get("turn_id") if isinstance(entry, Mapping) else None
            if entry and (not turn_id or not stored_turn or stored_turn != turn_id):
                state["one_shot"].pop(session_id, None)

        return self.update(mutate)

    def clear_session(self, session_id: str) -> dict:
        with _CrossPlatformLock(self.lock_path):
            state = self._read_unlocked()
            present = session_id in state["sessions"] or session_id in state["one_shot"]
            if not present:
                return copy.deepcopy(state)
            state["sessions"].pop(session_id, None)
            state["one_shot"].pop(session_id, None)
            clean = sanitize_state(state)
            self._write_unlocked(clean)
            return copy.deepcopy(clean)

    def prune_stale_sessions(
        self,
        *,
        now: Optional[int] = None,
        max_age_seconds: int = SESSION_TTL_SECONDS,
        keep_session: Optional[str] = None,
    ) -> dict:
        """Remove bounded stale session/one-shot entries as lifecycle backup."""

        timestamp = int(time.time()) if now is None else int(now)

        def mutate(state: MutableMapping[str, object]) -> None:
            stale = []
            for key, entry in state["sessions"].items():
                if key == keep_session or not isinstance(entry, Mapping):
                    continue
                last_seen = entry.get("last_seen")
                if isinstance(last_seen, int) and timestamp - last_seen > max_age_seconds:
                    stale.append(key)
            for key in stale:
                state["sessions"].pop(key, None)
                state["one_shot"].pop(key, None)

        return self.update(mutate)


__all__ = [
    "PROFILES",
    "SCHEMA_VERSION",
    "SESSION_TTL_SECONDS",
    "STATE_LOCK_TIMEOUT_SECONDS",
    "StateStore",
    "StateUnavailableError",
    "StateValidationError",
    "default_state",
    "effective_state",
    "migrate_state",
    "sanitize_state",
]
