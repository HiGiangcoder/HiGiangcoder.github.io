from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from bloglint.dataset import (
    append_documents,
    append_records,
    make_document_record,
    make_record,
)
from bloglint.schema import Issue, Span
from bloglint.student_eval import evaluate_predictions
from bloglint.text import document_from_body


BODY = "Nội dung bài viết rõ ràng."


def gold_dataset(temp: Path, bodies: list[str] | None = None) -> tuple[Path, Path, list[dict]]:
    bodies = bodies or [BODY]
    records = []
    documents = []
    meta = []
    for index, body in enumerate(bodies):
        document = document_from_body(body, title=f"Bài {index}", path=f"bai-{index}.md")
        issue = Issue(
            category="clarity",
            severity="warning",
            message="gold",
            suggestion="sửa",
            span=Span(0, 17, body[:17]),
        )
        record = make_record(document, [issue], model="teacher")
        records.append(record)
        documents.append(make_document_record(document))
        meta.append(
            {
                "content_sha256": record.content_sha256,
                "source_path": record.source_path,
            }
        )
    annotations = temp / "annotations.jsonl"
    docs_path = temp / "documents.jsonl"
    append_records(annotations, records)
    append_documents(docs_path, documents)
    return annotations, docs_path, meta


def write_predictions(path: Path, rows: list[dict]) -> None:
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")


class StudentEvalTests(unittest.TestCase):
    def test_precision_recall_and_invalid_quote(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            temp_path = Path(temp)
            annotations, documents, meta = gold_dataset(temp_path)
            predictions = temp_path / "predictions.jsonl"
            write_predictions(
                predictions,
                [
                    {
                        "content_sha256": meta[0]["content_sha256"],
                        "issues": [
                            {
                                "category": "clarity",
                                "severity": "warning",
                                "message": "đúng",
                                "suggestion": "sửa",
                                "quote": "Nội dung bài viết",
                            },
                            {
                                "category": "style",
                                "severity": "info",
                                "message": "sai category",
                                "suggestion": "sửa",
                                "quote": "Nội dung bài viết",
                            },
                            {
                                "category": "clarity",
                                "severity": "warning",
                                "message": "quote sai",
                                "suggestion": "sửa",
                                "quote": "không có trong bài",
                            },
                        ],
                    }
                ],
            )

            result = evaluate_predictions(predictions, annotations, documents)
            self.assertEqual(result["overall"]["true_positives"], 1)
            self.assertEqual(result["overall"]["false_positives"], 2)
            self.assertEqual(result["overall"]["false_negatives"], 0)
            self.assertEqual(result["issues"]["predicted_invalid"], 1)
            self.assertAlmostEqual(result["issues"]["quote_match_rate"], 2 / 3)
            self.assertEqual(result["per_category"]["clarity"]["f1"], 2 / 3)
            self.assertEqual(result["per_category"]["style"]["precision"], 0.0)

    def test_missing_prediction_counts_as_false_negative(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            temp_path = Path(temp)
            annotations, documents, _ = gold_dataset(temp_path)
            predictions = temp_path / "predictions.jsonl"
            write_predictions(predictions, [])

            result = evaluate_predictions(predictions, annotations, documents)
            self.assertEqual(result["documents"]["missing_predictions"], 1)
            self.assertEqual(result["overall"]["false_negatives"], 1)
            self.assertEqual(result["overall"]["recall"], 0.0)

    def test_split_limits_evaluated_documents(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            temp_path = Path(temp)
            annotations, documents, meta = gold_dataset(
                temp_path, [BODY, "Một câu khác cũng rõ ràng."]
            )
            predictions = temp_path / "predictions.jsonl"
            write_predictions(
                predictions,
                [
                    {
                        "content_sha256": row["content_sha256"],
                        "issues": [
                            {
                                "category": "clarity",
                                "severity": "warning",
                                "message": "đúng",
                                "suggestion": "sửa",
                                "quote": "Nội dung bài viết" if index == 0 else "Một câu khác",
                            }
                        ],
                    }
                    for index, row in enumerate(meta)
                ],
            )
            split = temp_path / "val.jsonl"
            write_predictions(split, [{"meta": {"content_sha256": meta[1]["content_sha256"]}}])

            result = evaluate_predictions(
                predictions, annotations, documents, split_path=split
            )
            self.assertEqual(result["documents"]["evaluated"], 1)
            self.assertEqual(result["overall"]["true_positives"], 1)

    def test_assistant_message_format_is_accepted(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            temp_path = Path(temp)
            annotations, documents, meta = gold_dataset(temp_path)
            predictions = temp_path / "predictions.jsonl"
            assistant = json.dumps(
                {
                    "issues": [
                        {
                            "category": "clarity",
                            "severity": "warning",
                            "message": "đúng",
                            "suggestion": "sửa",
                            "quote": "Nội dung bài viết",
                        }
                    ]
                }
            )
            write_predictions(
                predictions,
                [
                    {
                        "content_sha256": meta[0]["content_sha256"],
                        "messages": [
                            {"role": "user", "content": "..."},
                            {"role": "assistant", "content": assistant},
                        ],
                    }
                ],
            )
            result = evaluate_predictions(predictions, annotations, documents)
            self.assertEqual(result["overall"]["true_positives"], 1)


if __name__ == "__main__":
    unittest.main()
