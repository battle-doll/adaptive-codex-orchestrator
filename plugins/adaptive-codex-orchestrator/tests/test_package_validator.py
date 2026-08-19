from __future__ import annotations

import importlib.util
from pathlib import Path
import tempfile
import unittest


PLUGIN_ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = PLUGIN_ROOT / "scripts" / "validate_package.py"
SPEC = importlib.util.spec_from_file_location("adaptive_validate_package", MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
validate_package = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(validate_package)


class GeneratedBenchmarkDocumentTests(unittest.TestCase):
    def test_only_generated_final_messages_are_excluded(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory)
            generated = (
                repo
                / "benchmarks"
                / "runs"
                / "repeat-r1"
                / "_artifacts"
                / "mapping"
                / "case-01"
                / "final_message.md"
            )
            report = repo / "benchmarks" / "runs" / "repeat-r1" / "REPORT.ko.md"
            ordinary = repo / "docs" / "final_message.md"

            self.assertTrue(
                validate_package.is_generated_benchmark_final_message(generated, repo)
            )
            self.assertFalse(
                validate_package.is_generated_benchmark_final_message(report, repo)
            )
            self.assertFalse(
                validate_package.is_generated_benchmark_final_message(ordinary, repo)
            )


if __name__ == "__main__":
    unittest.main()
