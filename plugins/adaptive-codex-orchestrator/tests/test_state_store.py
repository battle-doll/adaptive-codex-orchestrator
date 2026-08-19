"""Offline tests for plugin-owned state, precedence, recovery, and locking."""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
import json
import os
from pathlib import Path
import stat
import sys
import tempfile
import threading
import unittest
from unittest import mock


HOOKS_DIR = Path(__file__).resolve().parents[1] / "hooks"
sys.path.insert(0, str(HOOKS_DIR))

from lib.project_identity import project_id
from lib import state_store as state_store_module
from lib.state_store import (
    SCHEMA_VERSION,
    SESSION_TTL_SECONDS,
    StateStore,
    StateUnavailableError,
    StateValidationError,
    default_state,
    effective_state,
    migrate_state,
    sanitize_state,
)


PROJECT_A = "a" * 64
PROJECT_B = "b" * 64
SESSION_A = "session-a"
SESSION_B = "session-b"


class StateStoreTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.data_dir = Path(self.temp.name) / "plugin-data"
        self.store = StateStore.from_data_dir(self.data_dir)

    def test_default_state_is_disabled_and_balanced(self) -> None:
        state = self.store.read()
        self.assertEqual(default_state(), state)
        resolved = effective_state(state, SESSION_A, PROJECT_A)
        self.assertFalse(resolved["enabled"])
        self.assertEqual("balanced", resolved["profile"])
        self.assertEqual("disabled", resolved["effective_scope"])
        self.assertEqual("default", resolved["profile_source"])

    def test_precedence_one_shot_session_project_global(self) -> None:
        self.store.set_enabled(
            scope="global",
            enabled=True,
            session_id=SESSION_A,
            project_id=PROJECT_A,
            profile="balanced",
        )
        self.store.set_enabled(
            scope="project",
            enabled=False,
            session_id=SESSION_A,
            project_id=PROJECT_A,
            profile="fast",
        )
        self.store.set_enabled(
            scope="session",
            enabled=True,
            session_id=SESSION_A,
            project_id=PROJECT_A,
            profile="conservative",
        )
        state = self.store.set_enabled(
            scope="one-shot",
            enabled=False,
            session_id=SESSION_A,
            project_id=PROJECT_A,
            turn_id="turn-a",
            profile="balanced",
        )

        resolved = effective_state(state, SESSION_A, PROJECT_A)
        self.assertFalse(resolved["enabled"])
        self.assertEqual("one-shot", resolved["state_source"])
        self.assertEqual("balanced", resolved["profile"])
        self.assertEqual("one-shot", resolved["profile_source"])

        state = self.store.clear_one_shot(SESSION_A)
        resolved = effective_state(state, SESSION_A, PROJECT_A)
        self.assertTrue(resolved["enabled"])
        self.assertEqual("session", resolved["state_source"])
        self.assertEqual("conservative", resolved["profile"])

    def test_enabled_and_profile_values_resolve_independently(self) -> None:
        self.store.set_enabled(
            scope="global",
            enabled=True,
            session_id=SESSION_A,
            project_id=PROJECT_A,
            profile="balanced",
        )
        state = self.store.set_profile(
            scope="project",
            profile="fast",
            session_id=SESSION_A,
            project_id=PROJECT_A,
        )
        resolved = effective_state(state, SESSION_A, PROJECT_A)
        self.assertTrue(resolved["enabled"])
        self.assertEqual("global", resolved["state_source"])
        self.assertEqual("fast", resolved["profile"])
        self.assertEqual("project", resolved["profile_source"])

    def test_session_and_project_state_are_independent(self) -> None:
        self.store.set_enabled(
            scope="project",
            enabled=True,
            session_id=SESSION_A,
            project_id=PROJECT_A,
        )
        self.store.set_enabled(
            scope="project",
            enabled=False,
            session_id=SESSION_A,
            project_id=PROJECT_B,
        )
        self.store.set_enabled(
            scope="session",
            enabled=False,
            session_id=SESSION_A,
            project_id=PROJECT_A,
        )
        state = self.store.set_enabled(
            scope="session",
            enabled=True,
            session_id=SESSION_B,
            project_id=PROJECT_A,
        )

        self.assertFalse(effective_state(state, SESSION_A, PROJECT_A)["enabled"])
        self.assertTrue(effective_state(state, SESSION_B, PROJECT_A)["enabled"])
        self.assertFalse(effective_state(state, "session-c", PROJECT_B)["enabled"])
        self.assertTrue(effective_state(state, "session-c", PROJECT_A)["enabled"])

    def test_one_shot_records_turn_and_restores_previous_state(self) -> None:
        self.store.set_enabled(
            scope="session",
            enabled=False,
            session_id=SESSION_A,
            project_id=PROJECT_A,
        )
        state = self.store.set_enabled(
            scope="one-shot",
            enabled=True,
            session_id=SESSION_A,
            project_id=PROJECT_A,
            turn_id="turn-1",
            profile="fast",
        )
        self.assertEqual("turn-1", state["one_shot"][SESSION_A]["turn_id"])
        self.assertTrue(effective_state(state, SESSION_A, PROJECT_A)["enabled"])

        state = self.store.clear_one_shot(SESSION_A)
        self.assertFalse(effective_state(state, SESSION_A, PROJECT_A)["enabled"])
        self.assertNotIn(SESSION_A, state["one_shot"])

    def test_stale_one_shot_only_clears_on_different_turn(self) -> None:
        self.store.set_enabled(
            scope="one-shot",
            enabled=True,
            session_id=SESSION_A,
            project_id=PROJECT_A,
            turn_id="turn-1",
        )
        state = self.store.clear_stale_one_shot(SESSION_A, "turn-1")
        self.assertIn(SESSION_A, state["one_shot"])
        state = self.store.clear_stale_one_shot(SESSION_A, "turn-2")
        self.assertNotIn(SESSION_A, state["one_shot"])

    def test_stale_one_shot_clears_when_either_turn_id_is_unavailable(self) -> None:
        self.store.set_enabled(
            scope="one-shot",
            enabled=True,
            session_id=SESSION_A,
            project_id=PROJECT_A,
            turn_id="known-turn",
        )
        state = self.store.clear_stale_one_shot(SESSION_A, None)
        self.assertNotIn(SESSION_A, state["one_shot"])

        self.store.set_enabled(
            scope="one-shot",
            enabled=True,
            session_id=SESSION_A,
            project_id=PROJECT_A,
            turn_id=None,
        )
        state = self.store.clear_stale_one_shot(SESSION_A, "new-turn")
        self.assertNotIn(SESSION_A, state["one_shot"])

    def test_active_policy_revision_is_bounded_internal_session_metadata(self) -> None:
        state = self.store.mark_active_policy(SESSION_A, 2)
        entry = state["sessions"][SESSION_A]
        self.assertEqual(2, entry["active_policy_revision"])
        self.assertGreater(entry["last_seen"], 0)
        self.assertNotIn("prompt", self.store.path.read_text(encoding="utf-8"))
        with self.assertRaises(ValueError):
            self.store.mark_active_policy(SESSION_A, 0)

    def test_session_cleanup_preserves_project_global_and_other_sessions(self) -> None:
        self.store.set_enabled(
            scope="global", enabled=True, session_id=SESSION_A, project_id=PROJECT_A
        )
        self.store.set_enabled(
            scope="project", enabled=False, session_id=SESSION_A, project_id=PROJECT_A
        )
        self.store.set_enabled(
            scope="session", enabled=True, session_id=SESSION_A, project_id=PROJECT_A
        )
        self.store.set_enabled(
            scope="one-shot",
            enabled=True,
            session_id=SESSION_A,
            project_id=PROJECT_A,
            turn_id="turn-a",
        )
        self.store.set_enabled(
            scope="session", enabled=True, session_id=SESSION_B, project_id=PROJECT_A
        )

        state = self.store.clear_session(SESSION_A)
        self.assertNotIn(SESSION_A, state["sessions"])
        self.assertNotIn(SESSION_A, state["one_shot"])
        self.assertIn(SESSION_B, state["sessions"])
        self.assertTrue(state["global"]["enabled"])
        self.assertFalse(state["projects"][PROJECT_A]["enabled"])

    def test_thirty_day_ttl_prunes_only_expired_sessions_and_their_one_shots(self) -> None:
        now = 10_000_000

        def seed(state: dict) -> None:
            state["global"]["enabled"] = True
            state["global"]["configured"] = True
            state["projects"][PROJECT_A] = {"enabled": True}
            state["sessions"].update(
                {
                    "expired": {
                        "enabled": True,
                        "compatibility_notice_shown": False,
                        "last_seen": now - SESSION_TTL_SECONDS - 1,
                    },
                    "boundary": {
                        "enabled": True,
                        "compatibility_notice_shown": False,
                        "last_seen": now - SESSION_TTL_SECONDS,
                    },
                    "current": {
                        "enabled": True,
                        "compatibility_notice_shown": False,
                        "last_seen": now - SESSION_TTL_SECONDS - 100,
                    },
                }
            )
            state["one_shot"].update(
                {
                    "expired": {"enabled": True, "turn_id": "old"},
                    "boundary": {"enabled": True, "turn_id": "edge"},
                    "current": {"enabled": True, "turn_id": "keep"},
                }
            )

        self.store.update(seed)
        state = self.store.prune_stale_sessions(now=now, keep_session="current")
        self.assertNotIn("expired", state["sessions"])
        self.assertNotIn("expired", state["one_shot"])
        self.assertIn("boundary", state["sessions"])
        self.assertIn("boundary", state["one_shot"])
        self.assertIn("current", state["sessions"])
        self.assertIn("current", state["one_shot"])
        self.assertTrue(state["global"]["enabled"])
        self.assertTrue(state["projects"][PROJECT_A]["enabled"])

    def test_global_and_project_preferences_persist_across_store_instances(self) -> None:
        self.store.set_enabled(
            scope="global",
            enabled=True,
            session_id=SESSION_A,
            project_id=PROJECT_A,
            profile="conservative",
        )
        self.store.set_enabled(
            scope="project",
            enabled=False,
            session_id=SESSION_A,
            project_id=PROJECT_A,
            profile="fast",
        )
        reopened = StateStore(self.store.path).read()
        self.assertTrue(reopened["global"]["enabled"])
        self.assertEqual("conservative", reopened["global"]["profile"])
        self.assertFalse(reopened["projects"][PROJECT_A]["enabled"])
        self.assertEqual("fast", reopened["projects"][PROJECT_A]["profile"])

    def test_missing_state_directory_is_created_lazily(self) -> None:
        self.assertFalse(self.data_dir.exists())
        self.store.set_enabled(
            scope="session", enabled=True, session_id=SESSION_A, project_id=PROJECT_A
        )
        self.assertTrue(self.data_dir.is_dir())
        self.assertTrue(self.store.path.is_file())

    def test_writes_are_atomic_and_leave_no_temporary_file(self) -> None:
        self.store.set_enabled(
            scope="session", enabled=True, session_id=SESSION_A, project_id=PROJECT_A
        )
        parsed = json.loads(self.store.path.read_text(encoding="utf-8"))
        self.assertEqual(SCHEMA_VERSION, parsed["schema_version"])
        self.assertEqual([], list(self.data_dir.glob(".state-v1-*.tmp")))

    def test_serialization_is_deterministic(self) -> None:
        self.store.set_enabled(
            scope="session",
            enabled=True,
            session_id=SESSION_A,
            project_id=PROJECT_A,
            profile="balanced",
        )
        first = self.store.path.read_bytes()
        self.store.set_enabled(
            scope="session",
            enabled=True,
            session_id=SESSION_A,
            project_id=PROJECT_A,
            profile="balanced",
        )
        second = self.store.path.read_bytes()
        self.assertEqual(first, second)
        self.assertTrue(first.endswith(b"\n"))

    def test_malformed_json_recovers_and_preserves_one_deduplicated_backup(self) -> None:
        self.data_dir.mkdir(parents=True)
        malformed = b'{"schema_version": 1, invalid'
        self.store.path.write_bytes(malformed)

        self.assertEqual(default_state(), self.store.read())
        self.assertEqual(default_state(), self.store.read())
        backups = list(self.data_dir.glob("state-v1.corrupt-*.json"))
        self.assertEqual(1, len(backups))
        self.assertEqual(malformed, backups[0].read_bytes())

    def test_future_schema_recovers_to_default_and_preserves_backup(self) -> None:
        self.data_dir.mkdir(parents=True)
        raw = b'{"schema_version": 999}'
        self.store.path.write_bytes(raw)
        self.assertEqual(default_state(), self.store.read())
        backups = list(self.data_dir.glob("state-v1.corrupt-*.json"))
        self.assertEqual(1, len(backups))
        self.assertEqual(raw, backups[0].read_bytes())

    def test_schema_zero_migrates_supported_legacy_fields(self) -> None:
        migrated = migrate_state({"enabled": True, "profile": "fast"})
        self.assertEqual(SCHEMA_VERSION, migrated["schema_version"])
        self.assertTrue(migrated["global"]["enabled"])
        self.assertEqual("fast", migrated["global"]["profile"])

    def test_invalid_root_and_direct_future_schema_are_rejected(self) -> None:
        with self.assertRaises(StateValidationError):
            migrate_state([])
        with self.assertRaises(StateValidationError):
            migrate_state({"schema_version": SCHEMA_VERSION + 1})

    def test_sanitization_drops_raw_paths_and_unknown_fields(self) -> None:
        dirty = default_state()
        dirty["projects"] = {
            "C:/Users/example/repo": {"enabled": True},
            PROJECT_A: {"enabled": True, "raw_path": "C:/private/repo"},
        }
        dirty["unknown"] = "value"
        clean = sanitize_state(dirty)
        self.assertEqual({PROJECT_A: {"enabled": True}}, clean["projects"])
        self.assertNotIn("unknown", clean)
        self.assertNotIn("raw_path", clean["projects"][PROJECT_A])

    def test_only_hashed_project_identity_is_persisted(self) -> None:
        raw_path = str(Path(self.temp.name) / "private" / "customer-repository")
        identifier = project_id(
            raw_path,
            runner=lambda *args, **kwargs: __import__("subprocess").CompletedProcess(
                args[0], 1, stdout="", stderr="not a repository"
            ),
        )
        self.store.set_enabled(
            scope="project",
            enabled=True,
            session_id=SESSION_A,
            project_id=identifier,
        )
        serialized = self.store.path.read_text(encoding="utf-8")
        self.assertNotIn(raw_path, serialized)
        self.assertIn(identifier, serialized)
        self.assertRegex(identifier, r"^[0-9a-f]{64}$")

    def test_concurrent_updates_do_not_lose_independent_sessions(self) -> None:
        workers = 24
        barrier = threading.Barrier(workers)

        def update(index: int) -> None:
            barrier.wait(timeout=5)
            StateStore(self.store.path).set_enabled(
                scope="session",
                enabled=True,
                session_id=f"session-{index}",
                project_id=PROJECT_A,
            )

        with ThreadPoolExecutor(max_workers=workers) as executor:
            list(executor.map(update, range(workers)))

        state = self.store.read()
        self.assertEqual(
            {f"session-{index}" for index in range(workers)},
            set(state["sessions"]),
        )

    def test_cleanup_lock_contention_times_out_without_corrupting_state(self) -> None:
        self.store.set_enabled(
            scope="one-shot",
            enabled=True,
            session_id=SESSION_A,
            project_id=PROJECT_A,
            turn_id="contended-turn",
        )
        before = self.store.path.read_bytes()
        with state_store_module._CrossPlatformLock(self.store.lock_path, timeout=0.1):
            with self.assertRaises(StateUnavailableError):
                self.store.clear_one_shot(SESSION_A)
        self.assertEqual(before, self.store.path.read_bytes())
        self.assertIn(SESSION_A, self.store.read()["one_shot"])

    def test_unwritable_location_fails_closed_with_specific_error(self) -> None:
        with mock.patch(
            "lib.state_store.tempfile.mkstemp", side_effect=PermissionError("read-only")
        ):
            with self.assertRaises(StateUnavailableError):
                self.store.set_enabled(
                    scope="session",
                    enabled=True,
                    session_id=SESSION_A,
                    project_id=PROJECT_A,
                )

    @unittest.skipIf(os.name == "nt", "POSIX permission bits are not authoritative on Windows")
    def test_state_file_is_user_only_on_posix(self) -> None:
        self.store.set_enabled(
            scope="session", enabled=True, session_id=SESSION_A, project_id=PROJECT_A
        )
        mode = stat.S_IMODE(self.store.path.stat().st_mode)
        self.assertEqual(0o600, mode)

    def test_invalid_scope_and_profile_do_not_write(self) -> None:
        with self.assertRaises(ValueError):
            self.store.set_enabled(
                scope="invalid",
                enabled=True,
                session_id=SESSION_A,
                project_id=PROJECT_A,
            )
        with self.assertRaises(ValueError):
            self.store.set_profile(
                scope="session",
                profile="turbo",
                session_id=SESSION_A,
                project_id=PROJECT_A,
            )
        with self.assertRaises(ValueError):
            self.store.set_profile(
                scope="invalid",
                profile="balanced",
                session_id=SESSION_A,
                project_id=PROJECT_A,
            )
        self.assertFalse(self.store.path.exists())


if __name__ == "__main__":
    unittest.main()
