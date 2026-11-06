from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from bloglint.audit import audit_dataset, render_review_markdown, write_review_sheet
from bloglint.dataset import (
    append_documents,
    append_records,
    make_document_record,
    make_record,
    read_documents,
    read_records,
)
from bloglint.schema import Issue, Span
from bloglint.text import document_from_body


def issue(
    body: str,
    start: int = 0,
    end: int = 17,
    category: str = "clarity",
    quote: str | None = None,
) -> Issue:
    text = quote if quote is not None else body[start:end]
    return Issue(
        category=category,
        severity="warning",
        message="mô tả",
        suggestion="gợi ý",
        span=Span(start=start, end=end, text=text),
    )


def dataset(temp: Path, body: str, issues: list[Issue], with_document: bool = True):
    document = document_from_body(body, title="Bài", path="bai.md")
    record = make_record(document, issues, model="teacher")
    annotations = temp / "annotations.jsonl"
    documents = temp / "documents.jsonl"
    append_records(annotations, [record])
    if with_document:
        append_documents(documents, [make_document_record(document)])
    return annotations, documents


class AuditTests(unittest.TestCase):
    def test_clean_dataset_has_no_blocking(self) -> None:
        body = "Nội dung bài viết rõ ràng."
        with tempfile.TemporaryDirectory() as temp:
            annotations, documents = dataset(Path(temp), body, [issue(body)])
            report = audit_dataset(annotations, documents)
            self.assertEqual(report["totals"]["blocking"], 0)
            self.assertEqual(report["totals"]["issues"], 1)
            self.assertEqual(report["per_category"]["clarity"], 1)

    def test_duplicate_issue_is_blocking(self) -> None:
        body = "Nội dung bài viết rõ ràng."
        with tempfile.TemporaryDirectory() as temp:
            annotations, documents = dataset(
                Path(temp), body, [issue(body), issue(body)]
            )
            report = audit_dataset(annotations, documents)
            self.assertEqual(report["totals"]["blocking"], 1)
            self.assertEqual(len(report["findings"]["duplicate_issues"]), 1)

    def test_missing_document_is_blocking(self) -> None:
        body = "Nội dung bài viết rõ ràng."
        with tempfile.TemporaryDirectory() as temp:
            annotations, documents = dataset(
                Path(temp), body, [issue(body)], with_document=False
            )
            report = audit_dataset(annotations, documents)
            self.assertEqual(len(report["findings"]["missing_documents"]), 1)
            self.assertEqual(report["totals"]["blocking"], 1)

    def test_span_mismatch_is_blocking(self) -> None:
        body = "Nội dung bài viết rõ ràng."
        with tempfile.TemporaryDirectory() as temp:
            annotations, documents = dataset(
                Path(temp), body, [issue(body, quote="sai nội dung")]
            )
            report = audit_dataset(annotations, documents)
            self.assertEqual(len(report["findings"]["span_mismatches"]), 1)
            self.assertEqual(report["totals"]["blocking"], 1)

    def test_short_quote_is_warning(self) -> None:
        body = "Nội dung bài viết rõ ràng."
        with tempfile.TemporaryDirectory() as temp:
            annotations, documents = dataset(
                Path(temp), body, [issue(body, start=0, end=8)]
            )
            report = audit_dataset(annotations, documents)
            self.assertEqual(len(report["findings"]["short_quotes"]), 1)
            self.assertEqual(report["totals"]["blocking"], 0)
            self.assertGreaterEqual(report["totals"]["warnings"], 1)

    def test_factual_is_flagged_out_of_scope(self) -> None:
        body = "Nội dung bài viết rõ ràng."
        with tempfile.TemporaryDirectory() as temp:
            annotations, documents = dataset(
                Path(temp), body, [issue(body, category="factual")]
            )
            report = audit_dataset(annotations, documents)
            self.assertEqual(len(report["findings"]["factual_needs_review"]), 1)
            self.assertEqual(len(report["findings"]["out_of_scope"]), 1)
            self.assertEqual(report["totals"]["train_category_issues"], 0)

    def test_review_sheet_and_writer(self) -> None:
        body = "Nội dung bài viết rõ ràng."
        with tempfile.TemporaryDirectory() as temp:
            temp_path = Path(temp)
            annotations, documents = dataset(temp_path, body, [issue(body)])
            report = audit_dataset(annotations, documents)
            text = render_review_markdown(
                report, read_records(annotations), read_documents(documents)
            )
            self.assertIn("BlogLint dataset review", text)
            self.assertIn("- [ ]", text)
            self.assertIn("Bài", text)

            target = write_review_sheet(
                annotations, documents, temp_path / "review.md"
            )
            self.assertTrue(target.exists())
            self.assertIn("BlogLint dataset review", target.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
