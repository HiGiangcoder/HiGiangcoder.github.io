from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from bloglint.evaluation import (
    EvaluationError,
    GoldCase,
    benchmark,
    evaluate,
    load_golden,
)
from bloglint.schema import Issue, Span

FIXTURES = Path(__file__).resolve().parents[1] / "fixtures"


def issue(category: str, start: int | None = None, end: int | None = None) -> Issue:
    span = Span(start, end, "x") if start is not None and end is not None else None
    return Issue(category=category, severity="info", message="x", span=span)


class GoldenFixtureTests(unittest.TestCase):
    def test_load_golden(self) -> None:
        cases = load_golden(FIXTURES / "golden.jsonl")
        self.assertEqual(len(cases), 5)
        self.assertTrue(all(case.body for case in cases))
        self.assertEqual(cases[0].issues[0].category, "cliche")
        self.assertIsNotNone(cases[0].issues[0].span)
        self.assertEqual(cases[-1].issues, [])

    def test_missing_fixture_rejected(self) -> None:
        with self.assertRaises(EvaluationError):
            load_golden(FIXTURES / "không-tồn-tại.jsonl")

    def test_bad_quote_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "bad.jsonl"
            path.write_text(
                json.dumps(
                    {
                        "body": "Nội dung.",
                        "issues": [{"category": "clarity", "quote": "không có"}],
                    },
                    ensure_ascii=False,
                )
                + "\n",
                encoding="utf-8",
            )
            with self.assertRaises(EvaluationError):
                load_golden(path)

    def test_span_out_of_bounds_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "bad.jsonl"
            path.write_text(
                json.dumps(
                    {
                        "body": "Ngắn.",
                        "issues": [
                            {
                                "category": "clarity",
                                "span": {"start": 0, "end": 999},
                            }
                        ],
                    },
                    ensure_ascii=False,
                )
                + "\n",
                encoding="utf-8",
            )
            with self.assertRaises(EvaluationError):
                load_golden(path)


class MatchingTests(unittest.TestCase):
    def test_perfect_match_with_overlap(self) -> None:
        case = GoldCase(
            id="x",
            title="",
            body="abcdef",
            issues=[issue("clarity", 0, 3)],
        )
        result = evaluate([case], lambda body, title: [issue("clarity", 1, 4)])
        self.assertEqual(result["overall"]["true_positives"], 1)
        self.assertEqual(result["overall"]["f1"], 1.0)

    def test_wrong_category_is_fp_and_fn(self) -> None:
        case = GoldCase(
            id="x",
            title="",
            body="abcdef",
            issues=[issue("clarity", 0, 3)],
        )
        result = evaluate([case], lambda body, title: [issue("style", 0, 3)])
        self.assertEqual(result["overall"]["false_positives"], 1)
        self.assertEqual(result["overall"]["false_negatives"], 1)
        self.assertEqual(result["overall"]["precision"], 0.0)
        self.assertEqual(result["overall"]["recall"], 0.0)

    def test_non_overlapping_span_is_fp_and_fn(self) -> None:
        case = GoldCase(
            id="x",
            title="",
            body="abcdef",
            issues=[issue("clarity", 0, 2)],
        )
        result = evaluate([case], lambda body, title: [issue("clarity", 3, 5)])
        self.assertEqual(result["overall"]["false_positives"], 1)
        self.assertEqual(result["overall"]["false_negatives"], 1)

    def test_structure_issue_without_span_matches(self) -> None:
        case = GoldCase(
            id="x",
            title="",
            body="abcdef",
            issues=[issue("structure")],
        )
        result = evaluate([case], lambda body, title: [issue("structure")])
        self.assertEqual(result["overall"]["f1"], 1.0)

    def test_empty_prediction(self) -> None:
        case = GoldCase(
            id="x",
            title="",
            body="abcdef",
            issues=[issue("clarity", 0, 1)],
        )
        result = evaluate([case], lambda body, title: [])
        self.assertEqual(result["overall"]["true_positives"], 0)
        self.assertEqual(result["overall"]["false_negatives"], 1)
        self.assertEqual(result["overall"]["f1"], 0.0)

    def test_extra_prediction_is_false_positive(self) -> None:
        case = GoldCase(id="x", title="", body="abcdef", issues=[])
        result = evaluate([case], lambda body, title: [issue("clarity", 0, 1)])
        self.assertEqual(result["overall"]["false_positives"], 1)
        self.assertEqual(result["overall"]["f1"], 0.0)


class BenchmarkTests(unittest.TestCase):
    def test_benchmark_runs_on_fixture(self) -> None:
        result = benchmark(FIXTURES / "golden.jsonl")
        self.assertEqual(result["cases"], 5)
        self.assertGreaterEqual(result["overall"]["f1"], 0.9)
        self.assertGreater(result["overall"]["true_positives"], 0)

    def test_per_category_present(self) -> None:
        result = benchmark(FIXTURES / "golden.jsonl")
        self.assertIn("cliche", result["per_category"])
        self.assertIn("punctuation", result["per_category"])


if __name__ == "__main__":
    unittest.main()
