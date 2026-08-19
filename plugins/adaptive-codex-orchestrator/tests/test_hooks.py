"""Offline fixture and lifecycle tests for the current Codex hook adapter."""

from __future__ import annotations

import copy
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest import mock


PLUGIN_ROOT = Path(__file__).resolve().parents[1]
HOOKS_DIR = PLUGIN_ROOT / "hooks"
FIXTURES_DIR = Path(__file__).resolve().parent / "fixtures" / "hooks"
sys.path.insert(0, str(HOOKS_DIR))

import runtime
from lib.hook_output import context_output, encode_output, is_valid_output
from lib import policy_loader
from lib.project_identity import project_id
from lib.state_store import (
    STATE_LOCK_TIMEOUT_SECONDS,
    StateStore,
    StateUnavailableError,
    effective_state,
)


FIXTURE_BY_EVENT = {
    "SessionStart": "session_start.json",
    "UserPromptSubmit": "user_prompt_submit.json",
    "SubagentStart": "subagent_start.json",
    "Stop": "stop.json",
    "SessionEnd": "session_end.json",
}


class HookRuntimeTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.cwd = self.root / "workspace"
        self.cwd.mkdir()
        self.data_dir = self.root / "plugin-data"
        self.environ = {
            "PLUGIN_ROOT": str(PLUGIN_ROOT),
            "PLUGIN_DATA": str(self.data_dir),
        }
        self.store = StateStore.from_data_dir(self.data_dir)
        self.project_hash = project_id(str(self.cwd))

    def fixture(self, event: str, **updates: object) -> dict:
        value = json.loads(
            (FIXTURES_DIR / FIXTURE_BY_EVENT[event]).read_text(encoding="utf-8")
        )
        value["cwd"] = str(self.cwd)
        value.update(updates)
        return value

    def handle(self, payload: object, *, environ: dict[str, str] | None = None) -> dict:
        return runtime.handle_event(
            payload,
            environ=self.environ if environ is None else environ,
            plugin_root=PLUGIN_ROOT,
        )

    def context(self, result: dict) -> str:
        self.assertTrue(is_valid_output(result), result)
        specific = result.get("hookSpecificOutput")
        self.assertIsInstance(specific, dict, result)
        return specific["additionalContext"]

    def enable_session(
        self,
        *,
        session_id: str = "fixture-session",
        profile: str = "balanced",
    ) -> None:
        self.store.set_enabled(
            scope="session",
            enabled=True,
            session_id=session_id,
            project_id=self.project_hash,
            profile=profile,
        )

    def test_fixture_set_matches_every_runtime_supported_event(self) -> None:
        self.assertEqual(set(runtime.SUPPORTED_EVENTS), set(FIXTURE_BY_EVENT))
        for event, filename in FIXTURE_BY_EVENT.items():
            with self.subTest(event=event):
                payload = json.loads((FIXTURES_DIR / filename).read_text(encoding="utf-8"))
                self.assertEqual(event, payload["hook_event_name"])
                self.assertIsInstance(payload["session_id"], str)
                self.assertIn("cwd", payload)

    def test_every_fixture_produces_valid_current_output_shape(self) -> None:
        for event in FIXTURE_BY_EVENT:
            with self.subTest(event=event):
                result = self.handle(self.fixture(event))
                self.assertTrue(is_valid_output(result), result)
                encoded = encode_output(result)
                self.assertEqual(result, json.loads(encoded))

    def test_hooks_json_declares_exact_runtime_events_and_cross_platform_commands(self) -> None:
        config = json.loads((HOOKS_DIR / "hooks.json").read_text(encoding="utf-8"))
        self.assertEqual(set(runtime.SUPPORTED_EVENTS), set(config["hooks"]))
        for event, groups in config["hooks"].items():
            self.assertIsInstance(groups, list)
            self.assertGreaterEqual(len(groups), 1)
            for group in groups:
                self.assertIsInstance(group["hooks"], list)
                for handler in group["hooks"]:
                    self.assertEqual("command", handler["type"])
                    self.assertIn("${PLUGIN_ROOT}", handler["command"])
                    self.assertIn("${PLUGIN_ROOT}", handler["commandWindows"])
                    self.assertLessEqual(handler["timeout"], 5)
        self.assertEqual(
            "startup|resume|clear|compact",
            config["hooks"]["SessionStart"][0]["matcher"],
        )
        self.assertLessEqual(config["hooks"]["SessionEnd"][0]["hooks"][0]["timeout"], 3)
        for event in ("Stop", "SessionEnd"):
            timeout = config["hooks"][event][0]["hooks"][0]["timeout"]
            self.assertGreater(timeout, STATE_LOCK_TIMEOUT_SECONDS)

    def test_disabled_session_start_emits_nothing(self) -> None:
        result = self.handle(self.fixture("SessionStart"))
        self.assertEqual({}, result)
        self.assertFalse(self.store.path.exists())

    def test_enabled_session_start_injects_compact_task_aware_policy(self) -> None:
        self.enable_session()
        result = self.handle(self.fixture("SessionStart"))
        text = self.context(result)
        self.assertEqual(
            "SessionStart", result["hookSpecificOutput"]["hookEventName"]
        )
        self.assertIn("balanced", text.casefold())
        self.assertIn("parent", text.casefold())
        self.assertIn("clear single-file", text.casefold())
        self.assertIn("four-module mapping defaults to zero", text.casefold())
        self.assertIn("at most two disjoint", text.casefold())
        self.assertLess(len(text), 1800)
        self.assertNotIn("configured fast worker", text.casefold())
        self.assertNotIn("compatibility mode", text.casefold())
        self.assertEqual(
            runtime.ACTIVE_POLICY_REVISION,
            self.store.read()["sessions"]["fixture-session"]["active_policy_revision"],
        )

    def test_model_fallback_setting_drives_compact_runtime_behavior(self) -> None:
        model_policy = policy_loader.load_model_policy(PLUGIN_ROOT)
        self.assertFalse(model_policy["allow_host_default_fallback"])
        text = policy_loader.compact_reminder(PLUGIN_ROOT, "balanced")
        self.assertIn("without retry or host-default substitution", text)
        for profile, limits in policy_loader.PROFILE_LIMITS.items():
            with self.subTest(profile=profile):
                self.assertEqual(1, limits["max_writers"])
                self.assertEqual(0, limits["max_retries"])

    def test_session_start_does_not_eagerly_load_detailed_runtime_policy(self) -> None:
        self.enable_session()
        with mock.patch.object(
            policy_loader,
            "load_runtime_policy",
            side_effect=AssertionError("detailed policy must be lazy"),
        ):
            result = self.handle(self.fixture("SessionStart"))
        self.assertIn("Ultra Orchestration is active", self.context(result))

    def test_compaction_session_start_reinjects_policy_with_explicit_prefix(self) -> None:
        self.enable_session(profile="conservative")
        result = self.handle(self.fixture("SessionStart", source="compact"))
        text = self.context(result)
        self.assertIn("context was compacted", text.casefold())
        self.assertIn("conservative", text.casefold())

    def test_session_start_prunes_expired_other_session_as_lifecycle_fallback(self) -> None:
        def seed(state: dict) -> None:
            state["sessions"].update(
                {
                    "fixture-session": {
                        "enabled": True,
                        "profile": "balanced",
                        "compatibility_notice_shown": False,
                        "last_seen": 0,
                    },
                    "expired-session": {
                        "enabled": True,
                        "compatibility_notice_shown": False,
                        "last_seen": 0,
                    },
                }
            )
            state["one_shot"]["expired-session"] = {
                "enabled": True,
                "turn_id": "expired-turn",
            }

        self.store.update(seed)
        result = self.handle(self.fixture("SessionStart"))
        self.assertTrue(is_valid_output(result), result)
        state = self.store.read()
        self.assertIn("fixture-session", state["sessions"])
        self.assertNotIn("expired-session", state["sessions"])
        self.assertNotIn("expired-session", state["one_shot"])
        self.assertGreater(state["sessions"]["fixture-session"]["last_seen"], 0)

    def test_unreadable_transcript_path_is_never_required(self) -> None:
        self.enable_session()
        payload = self.fixture(
            "SessionStart",
            transcript_path=str(self.root / "does-not-exist" / "rollout.jsonl"),
        )
        result = self.handle(payload)
        self.assertTrue(is_valid_output(result), result)
        self.assertIn("Ultra Orchestration is active", self.context(result))

    def test_enable_only_request_applies_session_state(self) -> None:
        payload = self.fixture("UserPromptSubmit", prompt="솔 울트라 모드 켜줘")
        result = self.handle(payload)
        text = self.context(result)
        state = self.store.read()
        resolved = effective_state(state, "fixture-session", self.project_hash)
        self.assertTrue(resolved["enabled"])
        self.assertEqual("session", resolved["state_source"])
        self.assertIn("command applied: enabled", text.casefold())
        self.assertIn("gpt-5.3-codex-spark", text)

    def test_enable_and_task_request_gets_policy_in_same_turn(self) -> None:
        payload = self.fixture(
            "UserPromptSubmit",
            prompt=(
                "솔 울트라 모드 켜줘. 현재 프로젝트에서 결제 실패 원인을 분석하고 "
                "최소 수정으로 해결해줘."
            ),
        )
        result = self.handle(payload)
        text = self.context(result)
        self.assertIn("command applied: enabled", text.casefold())
        self.assertIn("local reproducible bug", text.casefold())
        self.assertTrue(
            effective_state(self.store.read(), "fixture-session", self.project_hash)[
                "enabled"
            ]
        )

    def test_one_shot_enable_and_task_is_bound_to_current_turn(self) -> None:
        payload = self.fixture(
            "UserPromptSubmit",
            prompt=(
                "이번 작업만 빠른 프로필로 솔 울트라 모드를 켜고, "
                "서로 독립적인 모듈을 병렬 분석해줘."
            ),
            turn_id="turn-one-shot",
        )
        result = self.handle(payload)
        text = self.context(result)
        state = self.store.read()
        entry = state["one_shot"]["fixture-session"]
        self.assertTrue(entry["enabled"])
        self.assertEqual("fast", entry["profile"])
        self.assertEqual("turn-one-shot", entry["turn_id"])
        self.assertIn("profile: fast", text.casefold())

    def test_status_request_is_strictly_read_only(self) -> None:
        self.enable_session(profile="fast")
        before = self.store.path.read_bytes()
        result = self.handle(
            self.fixture("UserPromptSubmit", prompt="오케스트레이션 켜져 있어?")
        )
        after = self.store.path.read_bytes()
        self.assertEqual(before, after)
        text = self.context(result)
        self.assertIn("Ultra Orchestration: ON", text)
        self.assertIn("Profile: fast", text)
        self.assertIn("Ultra reasoning verified: no", text)

    def test_ambiguous_command_is_strictly_read_only(self) -> None:
        self.store.set_enabled(
            scope="global",
            enabled=True,
            session_id="fixture-session",
            project_id=self.project_hash,
        )
        before = self.store.path.read_bytes()
        result = self.handle(
            self.fixture(
                "UserPromptSubmit",
                prompt="이번 작업만 이 프로젝트에서 솔 울트라 모드 켜줘",
            )
        )
        self.assertEqual(before, self.store.path.read_bytes())
        self.assertIn("ambiguous", self.context(result).casefold())

    def test_generic_disable_creates_session_off_without_erasing_durable_state(self) -> None:
        self.store.set_enabled(
            scope="global",
            enabled=True,
            session_id="fixture-session",
            project_id=self.project_hash,
            profile="balanced",
        )
        self.store.set_enabled(
            scope="project",
            enabled=True,
            session_id="fixture-session",
            project_id=self.project_hash,
            profile="fast",
        )
        result = self.handle(
            self.fixture("UserPromptSubmit", prompt="솔 울트라 모드 꺼줘")
        )
        state = self.store.read()
        self.assertFalse(state["sessions"]["fixture-session"]["enabled"])
        self.assertTrue(state["projects"][self.project_hash]["enabled"])
        self.assertTrue(state["global"]["enabled"])
        self.assertFalse(
            effective_state(state, "fixture-session", self.project_hash)["enabled"]
        )
        text = self.context(result)
        self.assertIn("Ultra Orchestration: OFF", text)
        self.assertIn("Do not apply prior orchestration policy", text)

    def test_profile_change_without_scope_applies_to_session(self) -> None:
        self.store.set_enabled(
            scope="global",
            enabled=True,
            session_id="fixture-session",
            project_id=self.project_hash,
        )
        result = self.handle(
            self.fixture("UserPromptSubmit", prompt="빠른 프로필로 바꿔줘")
        )
        state = self.store.read()
        self.assertEqual("fast", state["sessions"]["fixture-session"]["profile"])
        self.assertTrue(
            effective_state(state, "fixture-session", self.project_hash)["enabled"]
        )
        self.assertIn("profile updated", self.context(result).casefold())

    def test_active_ordinary_request_gets_only_compact_reminder(self) -> None:
        self.enable_session()
        first = self.handle(
            self.fixture(
                "UserPromptSubmit",
                prompt="결제 실패 원인을 분석하고 최소 수정으로 해결해줘.",
            )
        )
        text = self.context(first)
        self.assertIn("is active", text.casefold())
        self.assertIn("defaults to zero", text.casefold())
        self.assertLess(len(text), 1800)
        self.assertNotIn("command applied", text.casefold())
        second = self.handle(
            self.fixture(
                "UserPromptSubmit",
                turn_id="fixture-turn-2",
                prompt="같은 버그의 관련 테스트를 확인해줘.",
            )
        )
        self.assertEqual({}, second)

    def test_old_policy_revision_gets_one_compact_refresh(self) -> None:
        self.enable_session()
        self.store.mark_active_policy(
            "fixture-session", runtime.ACTIVE_POLICY_REVISION - 1
        )

        first = self.handle(
            self.fixture(
                "UserPromptSubmit",
                prompt="네 개의 작은 모듈 진입점과 테스트를 매핑해줘.",
            )
        )
        self.assertIn(
            "four-module mapping defaults to zero", self.context(first).casefold()
        )
        self.assertEqual(
            runtime.ACTIVE_POLICY_REVISION,
            self.store.read()["sessions"]["fixture-session"]["active_policy_revision"],
        )

        second = self.handle(
            self.fixture(
                "UserPromptSubmit",
                turn_id="fixture-turn-2",
                prompt="같은 매핑 결과를 정리해줘.",
            )
        )
        self.assertEqual({}, second)

    def test_generic_modes_and_profile_status_never_mutate_orchestration_state(self) -> None:
        self.store.set_enabled(
            scope="global",
            enabled=False,
            session_id="fixture-session",
            project_id=self.project_hash,
        )
        before = self.store.path.read_bytes()
        prompts = (
            "다크 모드 켜줘",
            "테스트 모드 켜줘",
            "프로덕션 모드 켜줘",
            "편집 모드 꺼줘",
            "사용자 프로필 상태 알려줘",
        )
        for index, prompt in enumerate(prompts):
            with self.subTest(prompt=prompt):
                self.handle(
                    self.fixture(
                        "UserPromptSubmit", turn_id=f"negative-{index}", prompt=prompt
                    )
                )
                self.assertEqual(before, self.store.path.read_bytes())
                self.assertFalse(
                    effective_state(
                        self.store.read(), "fixture-session", self.project_hash
                    )["enabled"]
                )

    def test_referential_disable_is_read_only_without_confirmed_discourse_target(self) -> None:
        for active in (False, True):
            with self.subTest(active=active):
                self.store.set_enabled(
                    scope="session",
                    enabled=active,
                    session_id="fixture-session",
                    project_id=self.project_hash,
                )
                before = self.store.path.read_bytes()
                result = self.handle(
                    self.fixture("UserPromptSubmit", prompt="이 모드 꺼줘")
                )
                self.assertEqual(before, self.store.path.read_bytes())
                self.assertIn("ambiguous", self.context(result).casefold())

    def test_disabled_ordinary_request_emits_nothing_and_does_not_write(self) -> None:
        result = self.handle(
            self.fixture("UserPromptSubmit", prompt="결제 실패 원인을 분석해줘.")
        )
        self.assertEqual({}, result)
        self.assertFalse(self.store.path.exists())

    def test_spark_subagent_start_gets_model_reported_bounded_contract(self) -> None:
        self.enable_session()
        before = self.store.path.read_bytes()
        result = self.handle(self.fixture("SubagentStart"))
        self.assertEqual(before, self.store.path.read_bytes())
        text = self.context(result)
        self.assertIn("reports `gpt-5.3-codex-spark` as the active model", text)
        self.assertIn("Do not expand scope or spawn another subagent", text)
        self.assertIn("read-only", text)
        self.assertIn("not proof of completed model usage", text)
        expected_fields = (
            "conclusion",
            "evidence",
            "files_and_lines",
            "tests_or_checks",
            "risks",
            "recommended_parent_action",
        )
        field_contract = text.split("exactly these six top-level fields", 1)[1]
        positions = [field_contract.index(field) for field in expected_fields]
        self.assertEqual(sorted(positions), positions)
        self.assertIn("Do not draft a user-facing final answer", text)

    def test_unknown_subagent_model_gets_generic_contract_without_false_claim(self) -> None:
        self.enable_session()
        payload = self.fixture("SubagentStart")
        payload.pop("model")
        text = self.context(self.handle(payload))
        self.assertIn("confirmed model is unavailable", text)
        self.assertNotIn("reports `gpt-5.3-codex-spark` as the active model", text)

    def test_non_spark_subagent_does_not_get_spark_contract(self) -> None:
        self.enable_session()
        result = self.handle(
            self.fixture("SubagentStart", model="gpt-5.6-terra")
        )
        self.assertEqual({}, result)

    def test_subagent_permission_mode_does_not_mutate_state_or_grant_permissions(self) -> None:
        self.enable_session()
        before = self.store.path.read_bytes()
        result = self.handle(
            self.fixture("SubagentStart", permission_mode="bypassPermissions")
        )
        self.assertEqual(before, self.store.path.read_bytes())
        text = self.context(result)
        self.assertNotIn("approve", text.casefold())
        self.assertNotIn("elevate", text.casefold())

    def test_stop_clears_one_shot_and_returns_empty_json_without_continuation(self) -> None:
        self.store.set_enabled(
            scope="global",
            enabled=False,
            session_id="fixture-session",
            project_id=self.project_hash,
        )
        self.store.set_enabled(
            scope="one-shot",
            enabled=True,
            session_id="fixture-session",
            project_id=self.project_hash,
            turn_id="fixture-turn",
        )
        result = self.handle(self.fixture("Stop"))
        self.assertEqual({}, result)
        self.assertNotIn("fixture-session", self.store.read()["one_shot"])
        self.assertFalse(self.store.read()["global"]["enabled"])
        self.assertNotIn("decision", result)
        self.assertNotIn("continue", result)

    def test_next_turn_expires_stale_one_shot_if_stop_was_skipped(self) -> None:
        self.store.set_enabled(
            scope="one-shot",
            enabled=True,
            session_id="fixture-session",
            project_id=self.project_hash,
            turn_id="old-turn",
        )
        result = self.handle(
            self.fixture(
                "UserPromptSubmit",
                turn_id="new-turn",
                prompt="결제 실패 원인을 분석해줘.",
            )
        )
        self.assertEqual({}, result)
        self.assertNotIn("fixture-session", self.store.read()["one_shot"])

    def test_next_prompt_expires_one_shot_when_stop_and_turn_ids_are_missing(self) -> None:
        self.store.set_enabled(
            scope="one-shot",
            enabled=True,
            session_id="fixture-session",
            project_id=self.project_hash,
            turn_id=None,
        )
        payload = self.fixture(
            "UserPromptSubmit", prompt="결제 실패 원인을 분석해줘."
        )
        payload.pop("turn_id", None)
        self.assertEqual({}, self.handle(payload))
        self.assertNotIn("fixture-session", self.store.read()["one_shot"])

    def test_one_shot_profile_change_expires_on_next_turn_without_stop(self) -> None:
        first = self.fixture(
            "UserPromptSubmit",
            turn_id="profile-turn-1",
            prompt="Use the fast profile for this task only",
        )
        self.handle(first)
        state = self.store.read()
        self.assertEqual("fast", state["one_shot"]["fixture-session"]["profile"])
        self.assertEqual(
            "profile-turn-1", state["one_shot"]["fixture-session"]["turn_id"]
        )

        second = self.fixture(
            "UserPromptSubmit",
            turn_id="profile-turn-2",
            prompt="Inspect the current file without changing orchestration state.",
        )
        self.assertEqual({}, self.handle(second))
        state = self.store.read()
        self.assertNotIn("fixture-session", state["one_shot"])
        resolved = effective_state(state, "fixture-session", self.project_hash)
        self.assertEqual("balanced", resolved["profile"])

    def test_session_end_clears_only_its_session_and_one_shot(self) -> None:
        self.store.set_enabled(
            scope="global",
            enabled=True,
            session_id="fixture-session",
            project_id=self.project_hash,
        )
        self.store.set_enabled(
            scope="project",
            enabled=True,
            session_id="fixture-session",
            project_id=self.project_hash,
        )
        self.enable_session()
        self.store.set_enabled(
            scope="one-shot",
            enabled=True,
            session_id="fixture-session",
            project_id=self.project_hash,
            turn_id="fixture-turn",
        )
        self.store.set_enabled(
            scope="session",
            enabled=True,
            session_id="other-session",
            project_id=self.project_hash,
        )

        self.assertEqual({}, self.handle(self.fixture("SessionEnd")))
        state = self.store.read()
        self.assertNotIn("fixture-session", state["sessions"])
        self.assertNotIn("fixture-session", state["one_shot"])
        self.assertIn("other-session", state["sessions"])
        self.assertTrue(state["global"]["enabled"])
        self.assertTrue(state["projects"][self.project_hash]["enabled"])

    def test_cleanup_lock_contention_fails_open_and_next_prompt_recovers(self) -> None:
        self.store.set_enabled(
            scope="one-shot",
            enabled=True,
            session_id="fixture-session",
            project_id=self.project_hash,
            turn_id="contended-turn",
        )
        before = self.store.path.read_bytes()
        with mock.patch.object(
            StateStore,
            "clear_one_shot",
            side_effect=StateUnavailableError("timed out waiting for state lock"),
        ):
            self.assertEqual({}, self.handle(self.fixture("Stop")))
        self.assertEqual(before, self.store.path.read_bytes())

        recovered = self.handle(
            self.fixture(
                "UserPromptSubmit",
                turn_id="after-contention",
                prompt="ordinary follow-up",
            )
        )
        self.assertEqual({}, recovered)
        self.assertNotIn("fixture-session", self.store.read()["one_shot"])

    def test_missing_plugin_data_control_request_gets_diagnostic(self) -> None:
        payload = self.fixture("UserPromptSubmit", prompt="솔 울트라 모드 켜줘")
        result = self.handle(payload, environ={"PLUGIN_ROOT": str(PLUGIN_ROOT)})
        text = self.context(result)
        self.assertIn("could not access plugin-owned state", text)
        self.assertIn("No persistent mode change was applied", text)

    def test_missing_plugin_data_ordinary_request_fails_silently(self) -> None:
        payload = self.fixture("UserPromptSubmit", prompt="결제 실패를 분석해줘")
        self.assertEqual(
            {}, self.handle(payload, environ={"PLUGIN_ROOT": str(PLUGIN_ROOT)})
        )

    def test_missing_plugin_data_directory_is_created(self) -> None:
        self.assertFalse(self.data_dir.exists())
        self.handle(self.fixture("UserPromptSubmit", prompt="솔 울트라 모드 켜줘"))
        self.assertTrue(self.store.path.is_file())

    def test_missing_plugin_root_uses_packaged_runtime_location(self) -> None:
        result = runtime.handle_event(
            self.fixture("UserPromptSubmit", prompt="솔 울트라 모드 켜줘"),
            environ={"PLUGIN_DATA": str(self.data_dir)},
            plugin_root=None,
        )
        text = self.context(result)
        self.assertIn("gpt-5.3-codex-spark", text)
        self.assertTrue(self.store.path.is_file())

    def test_state_unavailable_control_request_fails_safe_with_diagnostic(self) -> None:
        payload = self.fixture("UserPromptSubmit", prompt="솔 울트라 모드 켜줘")
        with mock.patch.object(
            runtime.StateStore, "read", side_effect=StateUnavailableError("read-only")
        ):
            result = self.handle(payload)
        self.assertIn("could not access plugin-owned state", self.context(result))

    def test_unknown_event_and_unsupported_schema_do_not_mutate_state(self) -> None:
        self.enable_session()
        before = self.store.path.read_bytes()
        unknown = self.fixture("UserPromptSubmit", hook_event_name="FutureEvent")
        self.assertEqual({}, self.handle(unknown))
        unsupported = self.fixture("UserPromptSubmit", schema_version=2)
        self.assertEqual({}, self.handle(unsupported))
        self.assertEqual(before, self.store.path.read_bytes())

    def test_invalid_session_identifier_is_ignored_without_state_file(self) -> None:
        payload = self.fixture(
            "UserPromptSubmit",
            session_id="../../bad id",
            prompt="솔 울트라 모드 켜줘",
        )
        self.assertEqual({}, self.handle(payload))
        self.assertFalse(self.store.path.exists())

    def test_project_command_without_usable_cwd_does_not_write_placeholder_project(self) -> None:
        payload = self.fixture(
            "UserPromptSubmit", prompt="Enable orchestration for this repository"
        )
        payload.pop("cwd")
        result = self.handle(payload)
        state = self.store.read()
        self.assertEqual({}, state["projects"])
        text = self.context(result)
        self.assertIn("No project preference was changed", text)

    def test_compatibility_notice_is_shown_once_per_session(self) -> None:
        first = self.handle(
            self.fixture(
                "UserPromptSubmit",
                prompt="솔 울트라 모드 켜줘",
                model="gpt-5.6-terra",
            )
        )
        first_text = self.context(first)
        self.assertIn("compatibility mode", first_text.casefold())
        self.assertIn("Ultra reasoning cannot be programmatically verified", first_text)

        second = self.handle(
            self.fixture(
                "UserPromptSubmit",
                turn_id="fixture-turn-2",
                prompt="결제 실패 원인을 분석해줘.",
                model="gpt-5.6-terra",
            )
        )
        self.assertEqual({}, second)
        self.assertTrue(
            self.store.read()["sessions"]["fixture-session"][
                "compatibility_notice_shown"
            ]
        )

    def test_known_sol_parent_does_not_show_compatibility_notice(self) -> None:
        result = self.handle(
            self.fixture("UserPromptSubmit", prompt="솔 울트라 모드 켜줘")
        )
        text = self.context(result)
        self.assertNotIn("active in compatibility mode", text.casefold())
        self.assertIn("Compatibility mode: no", text)

    def test_unknown_parent_model_reports_unavailable_without_ultra_claim(self) -> None:
        payload = self.fixture("UserPromptSubmit", prompt="솔 울트라 모드 켜줘")
        payload.pop("model")
        text = self.context(self.handle(payload))
        self.assertIn("Parent model detected: unavailable", text)
        self.assertIn("Ultra reasoning verified: no", text)
        self.assertNotIn("Ultra reasoning verified: yes", text)

    def test_prompt_and_source_code_are_never_persisted(self) -> None:
        secret = "TOP_SECRET_SOURCE_TOKEN_7f8a"
        prompt = (
            "솔 울트라 모드 켜줘. 다음 코드를 분석해줘: "
            f"password = '{secret}'"
        )
        self.handle(self.fixture("UserPromptSubmit", prompt=prompt))
        persisted = self.store.path.read_text(encoding="utf-8")
        self.assertNotIn(secret, persisted)
        self.assertNotIn(prompt, persisted)
        self.assertNotIn("password", persisted)

    def test_invalid_json_cli_input_returns_empty_json_and_exit_zero(self) -> None:
        process = subprocess.run(
            [sys.executable, str(HOOKS_DIR / "runtime.py")],
            input=b"{not-json",
            capture_output=True,
            cwd=self.cwd,
            env={**os.environ, **self.environ},
            check=False,
            timeout=10,
        )
        self.assertEqual(0, process.returncode)
        self.assertEqual({}, json.loads(process.stdout.decode("utf-8")))
        self.assertEqual(b"", process.stderr)

    def test_oversized_cli_input_returns_empty_json_and_exit_zero(self) -> None:
        process = subprocess.run(
            [sys.executable, str(HOOKS_DIR / "runtime.py")],
            input=b"x" * (runtime.MAX_INPUT_BYTES + 1),
            capture_output=True,
            cwd=self.cwd,
            env={**os.environ, **self.environ},
            check=False,
            timeout=10,
        )
        self.assertEqual(0, process.returncode)
        self.assertEqual({}, json.loads(process.stdout.decode("utf-8")))
        self.assertEqual(b"", process.stderr)

    def test_valid_cli_fixture_emits_one_json_object(self) -> None:
        payload = self.fixture("UserPromptSubmit", prompt="Show orchestration status")
        process = subprocess.run(
            [sys.executable, str(HOOKS_DIR / "runtime.py")],
            input=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
            capture_output=True,
            cwd=self.cwd,
            env={**os.environ, **self.environ},
            check=False,
            timeout=10,
        )
        self.assertEqual(0, process.returncode)
        decoded = json.loads(process.stdout.decode("utf-8"))
        self.assertTrue(is_valid_output(decoded), decoded)
        self.assertEqual(1, len(process.stdout.decode("utf-8").splitlines()))

    def test_native_platform_launcher_forwards_stdin_and_stdout(self) -> None:
        payload = self.fixture("UserPromptSubmit", prompt="Show orchestration status")
        if os.name == "nt":
            command = [
                "powershell.exe",
                "-NoLogo",
                "-NoProfile",
                "-NonInteractive",
                "-ExecutionPolicy",
                "Bypass",
                "-File",
                str(HOOKS_DIR / "run_runtime.ps1"),
            ]
        else:
            command = ["/bin/sh", str(HOOKS_DIR / "run_runtime.sh")]
        process = subprocess.run(
            command,
            input=json.dumps(payload).encode("utf-8"),
            capture_output=True,
            cwd=self.cwd,
            env={**os.environ, **self.environ},
            check=False,
            timeout=15,
        )
        self.assertEqual(0, process.returncode, process.stderr.decode(errors="replace"))
        decoded = json.loads(process.stdout.decode("utf-8-sig"))
        self.assertTrue(is_valid_output(decoded), decoded)
        self.assertEqual("UserPromptSubmit", decoded["hookSpecificOutput"]["hookEventName"])

    def test_output_adapter_rejects_unsupported_or_empty_context_shapes(self) -> None:
        self.assertEqual({}, context_output("SessionStart", "  "))
        self.assertFalse(is_valid_output({"decision": "block"}))
        self.assertFalse(
            is_valid_output(
                {
                    "hookSpecificOutput": {
                        "hookEventName": "Stop",
                        "additionalContext": "invalid for Stop",
                    }
                }
            )
        )
        with self.assertRaises(ValueError):
            encode_output({"continue": False})


if __name__ == "__main__":
    unittest.main()
