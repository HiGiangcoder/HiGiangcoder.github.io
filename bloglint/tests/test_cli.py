from __future__ import annotations

import io
import json
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

from bloglint.cli import main

FIXTURES = Path(__file__).resolve().parents[1] / "fixtures"
REPO_ROOT = Path(__file__).resolve().parents[2]


def run(argv: list[str]) -> tuple[int, str, str]:
    stdout = io.StringIO()
    stderr = io.StringIO()
    with redirect_stdout(stdout), redirect_stderr(stderr):
        code = main(argv)
    return code, stdout.getvalue(), stderr.getvalue()


class DoctorTests(unittest.TestCase):
    def test_doctor_runs_without_network(self) -> None:
        code, stdout, _ = run(["--repo-root", str(REPO_ROOT), "doctor"])
        self.assertEqual(code, 0)
        self.assertIn("BlogLint doctor", stdout)
        self.assertIn("network: tắt mặc định", stdout)
        self.assertIn("API key:", stdout)


class AnalyzeTests(unittest.TestCase):
    def test_analyze_json(self) -> None:
        code, stdout, _ = run(["analyze", str(FIXTURES / "sample_post.md"), "--json"])
        self.assertEqual(code, 0)
        payload = json.loads(stdout)
        self.assertEqual(payload["path"], str(FIXTURES / "sample_post.md"))
        categories = {issue["category"] for issue in payload["issues"]}
        self.assertIn("cliche", categories)
        self.assertIn("filler_word", categories)

    def test_missing_file_returns_2(self) -> None:
        code, _, stderr = run(["analyze", str(FIXTURES / "không-có.md")])
        self.assertEqual(code, 2)
        self.assertIn("Không tìm thấy file", stderr)


class AnnotateGuardTests(unittest.TestCase):
    def test_dry_run_does_not_need_network(self) -> None:
        code, stdout, _ = run(
            ["annotate", str(FIXTURES / "sample_post.md"), "--dry-run"]
        )
        self.assertEqual(code, 0)
        self.assertIn("BẮT ĐẦU BÀI", stdout)
        self.assertIn("[dry-run]", stdout)

    def test_network_requires_flag(self) -> None:
        code, _, stderr = run(["annotate", str(FIXTURES / "sample_post.md")])
        self.assertEqual(code, 2)
        self.assertIn("--allow-network", stderr)


class BenchmarkCommandTests(unittest.TestCase):
    def test_benchmark_json(self) -> None:
        code, stdout, _ = run(["benchmark", "--json"])
        self.assertEqual(code, 0)
        payload = json.loads(stdout)
        self.assertEqual(payload["cases"], 5)
        self.assertIn("f1", payload["overall"])


class DatasetStatsTests(unittest.TestCase):
    def test_empty_data_dir(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            code, stdout, _ = run(["dataset-stats", "--data-dir", temp, "--json"])
            self.assertEqual(code, 0)
            payload = json.loads(stdout)
            self.assertEqual(payload["totals"]["records"], 0)


if __name__ == "__main__":
    unittest.main()
