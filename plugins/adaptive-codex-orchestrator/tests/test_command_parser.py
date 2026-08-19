"""Offline acceptance tests for the deterministic control-language parser."""

from __future__ import annotations

from pathlib import Path
import sys
import unittest
import unicodedata


HOOKS_DIR = Path(__file__).resolve().parents[1] / "hooks"
sys.path.insert(0, str(HOOKS_DIR))

from lib.command_parser import parse_command


class CommandParserMatrixTests(unittest.TestCase):
    def assert_decision(
        self,
        text: object,
        intent: str,
        scope: str | None,
        profile: str | None = None,
        *,
        mode_active: bool = True,
    ) -> None:
        result = parse_command(text, mode_active=mode_active)
        self.assertFalse(result.ambiguous, result)
        self.assertEqual(intent, result.intent, result)
        self.assertEqual(scope, result.scope, result)
        self.assertEqual(profile, result.profile, result)
        self.assertIn(result.confidence, {"medium", "high"})

    def test_required_korean_and_english_command_matrix(self) -> None:
        cases = (
            ("솔 울트라 모드 켜줘", "enable", "session", None),
            ("솔 울트라 켜줘", "enable", "session", None),
            ("울트라 오케스트레이션 활성화해", "enable", "session", None),
            ("이번 작업만 솔 울트라 모드 켜줘", "enable", "one-shot", None),
            ("이 프로젝트에서는 항상 켜줘", "enable", "project", None),
            ("모든 프로젝트에서 기본으로 켜줘", "enable", "global", None),
            ("솔 울트라 모드 꺼줘", "disable", "session", None),
            ("이 프로젝트에서 솔 울트라 모드 꺼줘", "disable", "project", None),
            ("전체 기본 설정에서 꺼줘", "disable", "global", None),
            ("솔 울트라 모드를 켜지 마", "disable", "session", None),
            ("스파크 오케스트레이션 사용하지 마", "disable", "session", None),
            ("빠른 프로필로 바꿔줘", "set_profile", "session", "fast"),
            ("보수적 프로필로 전환해", "set_profile", "session", "conservative"),
            ("Turn on Sol Ultra mode", "enable", "session", None),
            ("Turn Sol Ultra on", "enable", "session", None),
            ("Enable adaptive orchestration", "enable", "session", None),
            ("Use orchestration for this task only", "enable", "one-shot", None),
            ("Enable orchestration for this repository", "enable", "project", None),
            ("Enable orchestration globally", "enable", "global", None),
            ("Turn off Ultra Orchestration", "disable", "session", None),
            ("Disable orchestration for this repository", "disable", "project", None),
            ("Do not enable orchestration", "disable", "session", None),
        )
        for text, intent, scope, profile in cases:
            with self.subTest(text=text):
                self.assert_decision(text, intent, scope, profile)

    def test_status_matrix_has_priority_and_no_control_action(self) -> None:
        for text in (
            "솔 울트라 모드 상태 알려줘",
            "오케스트레이션 켜져 있어?",
            "현재 어떤 오케스트레이션 프로필이야?",
            "Show orchestration status",
            "Is Ultra Orchestration enabled?",
            "Which orchestration profile is active?",
            "$adaptive-orchestration 상태 알려줘",
        ):
            with self.subTest(text=text):
                result = parse_command(text)
                self.assertEqual("status", result.intent, result)
                self.assertFalse(result.ambiguous, result)
                self.assertIsNone(result.scope)
                self.assertIsNone(result.profile)

    def test_explicit_negation_beats_enable_token(self) -> None:
        for text in (
            "솔 울트라 모드를 켜지 마",
            "Do not turn on Sol Ultra mode",
            "Don't enable adaptive orchestration",
        ):
            with self.subTest(text=text):
                self.assertEqual("disable", parse_command(text).intent)

    def test_enable_and_disable_in_same_sentence_is_ambiguous(self) -> None:
        result = parse_command("솔 울트라 모드를 켜고 바로 꺼줘")
        self.assertTrue(result.ambiguous, result)
        self.assertIsNone(result.intent)
        self.assertIn("conflicting", result.reason or "")

        referential = parse_command(
            "Turn off Ultra Orchestration and then turn it on", mode_active=True
        )
        self.assertTrue(referential.ambiguous, referential)
        self.assertIsNone(referential.intent, referential)

    def test_conflicting_scopes_do_not_choose_one(self) -> None:
        result = parse_command(
            "이번 작업만 이 프로젝트에서 솔 울트라 모드 켜줘"
        )
        self.assertTrue(result.ambiguous, result)
        self.assertIsNone(result.intent)
        self.assertEqual("conflicting scopes", result.reason)

    def test_unknown_profile_is_ambiguous(self) -> None:
        for text in (
            "솔 울트라 모드를 터보 프로필로 바꿔줘",
            "Set Ultra Orchestration to the aggressive profile",
        ):
            with self.subTest(text=text):
                result = parse_command(text)
                self.assertTrue(result.ambiguous, result)
                self.assertIsNone(result.intent)
                self.assertEqual("unknown profile", result.reason)

    def test_quoted_examples_are_not_commands(self) -> None:
        for text in (
            '문서 예시는 "솔 울트라 모드 켜줘"입니다.',
            "The README says 'Turn on Sol Ultra mode' as an example.",
            "> Enable adaptive orchestration",
            "`솔 울트라 모드 켜줘`",
            "문서에는 '$adaptive-orchestration 상태 알려줘'라고 적혀 있습니다.",
        ):
            with self.subTest(text=text):
                result = parse_command(text)
                self.assertIsNone(result.intent, result)
                self.assertFalse(result.ambiguous, result)

    def test_fenced_examples_are_not_commands(self) -> None:
        for fence in ("```", "~~~"):
            text = f"예시입니다.\n{fence}text\n솔 울트라 모드 켜줘\n{fence}"
            with self.subTest(fence=fence):
                result = parse_command(text)
                self.assertIsNone(result.intent, result)
                self.assertFalse(result.ambiguous, result)

    def test_long_fenced_examples_remain_masked_at_command_edges(self) -> None:
        text = "\n".join(
            [
                "```text",
                "Turn on Ultra Orchestration",
                *[f"example line {index}" for index in range(20)],
                "```",
                "Explain the documentation example without changing state.",
            ]
        )
        result = parse_command(text)
        self.assertIsNone(result.intent, result)
        self.assertFalse(result.ambiguous, result)

    def test_profile_use_phrases_are_profile_changes_not_activation(self) -> None:
        for phrase, profile in (
            ("솔 울트라 모드를 보수적으로 사용해", "conservative"),
            ("Use the conservative profile", "conservative"),
            ("Set orchestration profile to balanced", "balanced"),
            ("Switch to the fast profile", "fast"),
        ):
            with self.subTest(phrase=phrase):
                result = parse_command(phrase)
                self.assertEqual("set_profile", result.intent, result)
                self.assertEqual("session", result.scope, result)
                self.assertEqual(profile, result.profile, result)

    def test_informational_control_questions_do_not_mutate(self) -> None:
        for phrase in (
            "How do I enable Ultra Orchestration?",
            "Should I enable Ultra Orchestration?",
            "Explain how to enable Ultra Orchestration",
            "솔 울트라 모드는 어떻게 켜나요?",
        ):
            with self.subTest(phrase=phrase):
                result = parse_command(phrase)
                self.assertIsNone(result.intent, result)
                self.assertFalse(result.ambiguous, result)

    def test_long_paste_with_incidental_terms_is_ignored(self) -> None:
        lines = [f"ordinary requirement line {index}" for index in range(20)]
        lines[10] = "문서 예제로 솔 울트라 모드 켜줘 라는 표현을 설명한다"
        result = parse_command("\n".join(lines))
        self.assertIsNone(result.intent, result)
        self.assertFalse(result.ambiguous, result)

    def test_mixed_enable_and_task_sets_remaining_task(self) -> None:
        result = parse_command(
            "솔 울트라 모드 켜줘. 결제 실패 원인을 분석하고 최소 수정으로 해결해줘."
        )
        self.assertEqual("enable", result.intent, result)
        self.assertEqual("session", result.scope, result)
        self.assertTrue(result.contains_remaining_task, result)

    def test_mixed_disable_and_task_sets_remaining_task(self) -> None:
        result = parse_command(
            "솔 울트라 모드 꺼줘. 이어서 결제 모듈 테스트를 실행해줘."
        )
        self.assertEqual("disable", result.intent, result)
        self.assertTrue(result.contains_remaining_task, result)

    def test_nfkc_korean_and_full_width_english_variants(self) -> None:
        decomposed = unicodedata.normalize("NFD", "솔 울트라 모드 켜줘")
        self.assert_decision(decomposed, "enable", "session")
        self.assert_decision(
            "ＴＵＲＮ　ＯＮ　ＳＯＬ　ＵＬＴＲＡ　ＭＯＤＥ",
            "enable",
            "session",
        )

    def test_repeated_whitespace_and_english_case(self) -> None:
        self.assert_decision("솔   울트라\n\t모드   켜줘", "enable", "session")
        self.assert_decision("eNaBlE AdApTiVe OrChEsTrAtIoN", "enable", "session")

    def test_unanchored_mode_and_profile_status_do_not_target_orchestration(self) -> None:
        for phrase in (
            "다크 모드 켜줘",
            "테스트 모드 켜줘",
            "프로덕션 모드 켜줘",
            "사용자 프로필 상태 알려줘",
            "빌드 프로필 상태 알려줘",
            "모드 상태 알려줘",
            "현재 어떤 프로필이야?",
            "Show user profile status",
        ):
            for active in (False, True):
                with self.subTest(phrase=phrase, active=active):
                    result = parse_command(phrase, mode_active=active)
                    self.assertIsNone(result.intent, result)
                    self.assertFalse(result.ambiguous, result)

    def test_referential_controls_require_explicit_skill_context(self) -> None:
        for phrase in (
            "이 모드 꺼줘",
            "Turn this mode off",
            "Disable it",
            "Enable it globally",
        ):
            for active in (False, True):
                with self.subTest(phrase=phrase, active=active):
                    result = parse_command(phrase, mode_active=active)
                    self.assertTrue(result.ambiguous, result)
                    self.assertIsNone(result.intent, result)
                    self.assertEqual(
                        "referential control without an explicit orchestration anchor",
                        result.reason,
                    )

        invoked_disable = parse_command("Disable it", skill_invoked=True)
        self.assertEqual("disable", invoked_disable.intent, invoked_disable)
        self.assertEqual("session", invoked_disable.scope, invoked_disable)

        invoked_enable = parse_command("Enable it globally", skill_invoked=True)
        self.assertEqual("enable", invoked_enable.intent, invoked_enable)
        self.assertEqual("global", invoked_enable.scope, invoked_enable)

        named_skill = parse_command("$adaptive-orchestration 이 모드 꺼줘")
        self.assertEqual("disable", named_skill.intent, named_skill)

    def test_empty_non_string_and_invalid_unicode_are_safe(self) -> None:
        for value in ("", "   \n\t", None, 123, object()):
            with self.subTest(value=repr(value)):
                result = parse_command(value)
                self.assertIsNone(result.intent, result)
                self.assertFalse(result.ambiguous, result)

        result = parse_command("\ud800 솔 울트라 모드 켜줘 \udfff")
        self.assertEqual("enable", result.intent, result)


if __name__ == "__main__":
    unittest.main()
