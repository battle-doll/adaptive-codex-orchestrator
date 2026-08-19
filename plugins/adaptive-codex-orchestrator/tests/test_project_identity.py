"""Tests for deterministic, privacy-preserving project identity."""

from __future__ import annotations

import hashlib
from pathlib import Path
import subprocess
import sys
import unittest


HOOKS_DIR = Path(__file__).resolve().parents[1] / "hooks"
sys.path.insert(0, str(HOOKS_DIR))

from lib.project_identity import discover_repository_root, normalize_path, project_id


class ProjectIdentityTests(unittest.TestCase):
    def test_git_repository_root_is_used_for_nested_directory(self) -> None:
        calls: list[tuple[list[str], dict]] = []

        def runner(args: list[str], **kwargs: object) -> subprocess.CompletedProcess[str]:
            calls.append((args, kwargs))
            return subprocess.CompletedProcess(args, 0, stdout="/srv/repo\n", stderr="")

        root = discover_repository_root("/srv/repo/src/deep", runner=runner)
        self.assertEqual("/srv/repo", root)
        self.assertEqual(
            ["git", "-C", "/srv/repo/src/deep", "rev-parse", "--show-toplevel"],
            calls[0][0],
        )
        self.assertIs(calls[0][1]["shell"], False)
        self.assertIs(calls[0][1]["check"], False)
        self.assertEqual(1.5, calls[0][1]["timeout"])

    def test_nested_directories_share_the_same_git_project_id(self) -> None:
        def runner(args: list[str], **kwargs: object) -> subprocess.CompletedProcess[str]:
            return subprocess.CompletedProcess(args, 0, stdout="/srv/repo\n", stderr="")

        first = project_id("/srv/repo/src", runner=runner, platform="posix")
        second = project_id("/srv/repo/tests/unit", runner=runner, platform="posix")
        self.assertEqual(first, second)

    def test_non_git_directory_falls_back_to_cwd(self) -> None:
        def runner(args: list[str], **kwargs: object) -> subprocess.CompletedProcess[str]:
            return subprocess.CompletedProcess(args, 128, stdout="", stderr="not a repo")

        cwd = "/srv/plain-directory"
        self.assertEqual(cwd, discover_repository_root(cwd, runner=runner))
        expected = hashlib.sha256(cwd.encode("utf-8")).hexdigest()
        self.assertEqual(expected, project_id(cwd, runner=runner, platform="posix"))

    def test_git_executable_unavailable_falls_back(self) -> None:
        def runner(*args: object, **kwargs: object) -> subprocess.CompletedProcess[str]:
            raise FileNotFoundError("git")

        self.assertEqual("/srv/plain", discover_repository_root("/srv/plain", runner=runner))

    def test_git_timeout_falls_back(self) -> None:
        def runner(*args: object, **kwargs: object) -> subprocess.CompletedProcess[str]:
            raise subprocess.TimeoutExpired("git", timeout=0.01)

        self.assertEqual(
            "/srv/slow",
            discover_repository_root("/srv/slow", runner=runner, timeout=0.01),
        )

    def test_git_os_error_falls_back(self) -> None:
        def runner(*args: object, **kwargs: object) -> subprocess.CompletedProcess[str]:
            raise OSError("unavailable")

        self.assertEqual("/srv/plain", discover_repository_root("/srv/plain", runner=runner))

    def test_windows_paths_normalize_case_separators_and_dot_segments(self) -> None:
        variants = (
            "C:\\Users\\Example\\Repo\\src\\..\\",
            r"c:/users/example/repo",
            "C:\\USERS\\EXAMPLE\\REPO\\",
        )
        normalized = {normalize_path(value, platform="windows") for value in variants}
        self.assertEqual({"c:/users/example/repo"}, normalized)

    def test_windows_drive_root_keeps_root_separator(self) -> None:
        self.assertEqual("c:/", normalize_path("C:\\", platform="windows"))

    def test_posix_paths_normalize_separators_and_dot_segments(self) -> None:
        self.assertEqual(
            "/srv/repo",
            normalize_path(r"/srv/project/../repo/", platform="posix"),
        )
        self.assertEqual("/", normalize_path("/", platform="posix"))

    def test_posix_normalization_preserves_case(self) -> None:
        self.assertNotEqual(
            normalize_path("/srv/Repo", platform="posix"),
            normalize_path("/srv/repo", platform="posix"),
        )

    def test_equivalent_windows_paths_have_stable_hash(self) -> None:
        def not_git(args: list[str], **kwargs: object) -> subprocess.CompletedProcess[str]:
            return subprocess.CompletedProcess(args, 1, stdout="", stderr="")

        first = project_id(r"C:\Users\Example\Repo", platform="windows", runner=not_git)
        second = project_id("c:/users/example/repo/", platform="windows", runner=not_git)
        self.assertEqual(first, second)

    def test_equivalent_posix_paths_have_stable_hash(self) -> None:
        def not_git(args: list[str], **kwargs: object) -> subprocess.CompletedProcess[str]:
            return subprocess.CompletedProcess(args, 1, stdout="", stderr="")

        first = project_id("/srv/repo/./src/..", platform="posix", runner=not_git)
        second = project_id("/srv/repo", platform="posix", runner=not_git)
        self.assertEqual(first, second)

    def test_project_id_contains_no_raw_path(self) -> None:
        raw = "/srv/private/customer-name/repository"

        def not_git(args: list[str], **kwargs: object) -> subprocess.CompletedProcess[str]:
            return subprocess.CompletedProcess(args, 1, stdout="", stderr="")

        identifier = project_id(raw, platform="posix", runner=not_git)
        self.assertNotIn("private", identifier)
        self.assertNotIn(raw, identifier)
        self.assertRegex(identifier, r"^[0-9a-f]{64}$")

    def test_empty_git_stdout_falls_back(self) -> None:
        def runner(args: list[str], **kwargs: object) -> subprocess.CompletedProcess[str]:
            return subprocess.CompletedProcess(args, 0, stdout="  \n", stderr="")

        self.assertEqual("/srv/plain", discover_repository_root("/srv/plain", runner=runner))


if __name__ == "__main__":
    unittest.main()
