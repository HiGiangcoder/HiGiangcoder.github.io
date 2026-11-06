from __future__ import annotations

import unittest

from bloglint.schema import (
    AnnotationRecord,
    Document,
    Issue,
    SchemaError,
    Span,
    now_iso,
)


class SpanTests(unittest.TestCase):
    def test_valid_span(self) -> None:
        span = Span(start=2, end=5, text="abc")
        self.assertEqual(span.to_dict(), {"start": 2, "end": 5, "text": "abc"})

    def test_negative_start_rejected(self) -> None:
        with self.assertRaises(SchemaError):
            Span(start=-1, end=3, text="abc")

    def test_end_before_start_rejected(self) -> None:
        with self.assertRaises(SchemaError):
            Span(start=5, end=3, text="abc")

    def test_overlap(self) -> None:
        self.assertTrue(Span(0, 5, "abcde").overlaps(Span(4, 6, "ef")))
        self.assertFalse(Span(0, 5, "abcde").overlaps(Span(5, 6, "f")))


class IssueTests(unittest.TestCase):
    def test_roundtrip(self) -> None:
        issue = Issue(
            category="filler_word",
            severity="info",
            message="Từ đệm",
            suggestion="Bỏ đi",
            span=Span(0, 3, "abc"),
            paragraph=1,
        )
        restored = Issue.from_dict(issue.to_dict())
        self.assertEqual(restored.category, "filler_word")
        self.assertEqual(restored.span, Span(0, 3, "abc"))
        self.assertEqual(restored.paragraph, 1)

    def test_invalid_category(self) -> None:
        with self.assertRaises(SchemaError):
            Issue(category="unknown", severity="info", message="x")

    def test_invalid_severity(self) -> None:
        with self.assertRaises(SchemaError):
            Issue(category="clarity", severity="fatal", message="x")

    def test_confidence_bounds(self) -> None:
        with self.assertRaises(SchemaError):
            Issue(category="clarity", severity="info", message="x", confidence=1.2)

    def test_source_must_be_known(self) -> None:
        with self.assertRaises(SchemaError):
            Issue(category="clarity", severity="info", message="x", source="magic")


class DocumentTests(unittest.TestCase):
    def test_hash_is_computed(self) -> None:
        document = Document(path="a.md", title="A", body="nội dung")
        self.assertEqual(len(document.content_sha256), 64)

    def test_explicit_hash_is_kept(self) -> None:
        document = Document(
            path="a.md", title="A", body="nội dung", content_sha256="abc"
        )
        self.assertEqual(document.content_sha256, "abc")


class AnnotationRecordTests(unittest.TestCase):
    def test_roundtrip(self) -> None:
        record = AnnotationRecord(
            source_path="a.md",
            title="A",
            content_sha256="hash",
            model="gpt-oss:120b-cloud",
            issues=[Issue(category="clarity", severity="warning", message="Rõ hơn")],
            created_at=now_iso(),
        )
        restored = AnnotationRecord.from_dict(record.to_dict())
        self.assertEqual(restored.model, record.model)
        self.assertEqual(len(restored.issues), 1)
        self.assertEqual(restored.issues[0].source, "rule")

    def test_issue_dicts_are_converted(self) -> None:
        record = AnnotationRecord(
            source_path="a.md",
            title="A",
            content_sha256="hash",
            model="m",
            issues=[{"category": "style", "severity": "info", "message": "x"}],
        )
        self.assertIsInstance(record.issues[0], Issue)


if __name__ == "__main__":
    unittest.main()
