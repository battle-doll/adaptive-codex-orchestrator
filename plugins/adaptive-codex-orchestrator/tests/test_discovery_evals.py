from __future__ import annotations

import copy
import json
from pathlib import Path
import sys
import unittest


PLUGIN_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = PLUGIN_ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

from validate_package import Validator, validate_discovery_payload  # noqa: E402


class DiscoveryEvalTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.payload = json.loads(
            (PLUGIN_ROOT / "evals" / "discovery-cases.json").read_text(encoding="utf-8")
        )

    def validate(self, payload: dict[str, object]) -> list[str]:
        validator = Validator()
        validate_discovery_payload(payload, validator)
        return validator.errors

    def test_checked_in_golden_set_is_valid(self) -> None:
        self.assertEqual(self.validate(self.payload), [])

    def test_count_regression_is_rejected(self) -> None:
        payload = copy.deepcopy(self.payload)
        payload["negative"].pop()
        errors = self.validate(payload)
        self.assertTrue(any("negative dataset must contain exactly 20" in error for error in errors))
        self.assertTrue(any("exactly 50 cases" in error for error in errors))

    def test_locale_regression_is_rejected(self) -> None:
        payload = copy.deepcopy(self.payload)
        for case in payload["direct"]:
            case["language"] = "en"
        errors = self.validate(payload)
        self.assertTrue(any("direct cases must include Korean and English" in error for error in errors))
        self.assertTrue(any("exactly 5 ko cases" in error for error in errors))

    def test_selection_regression_is_rejected(self) -> None:
        payload = copy.deepcopy(self.payload)
        payload["negative"][0]["expected_selection"] = "select"
        errors = self.validate(payload)
        self.assertTrue(any("must use expected_selection=do_not_select" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
