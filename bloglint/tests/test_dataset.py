from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from bloglint.dataset import (
    DatasetError,
    append_records,
    build_manifest,
    make_record,
    read_records,
    write_manifest,
)
from bloglint.schema import AnnotationRecord, Issue
from bloglint.text import document_from_body


def record(body: str, model: str = "gpt-oss:120b-cloud", message: str = "x") -> AnnotationRecord:
    document = document_from_body(body, title="Bài", path="bai.md")
    return make_record(
        document,
        [Issue(category="clarity", severity="info", message=message)],
        model=model,
        meta={"source": "test"},
    )


class AppendTests(unittest.TestCase):
    def test_append_and_read(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "data" / "annotations.jsonl"
            first = record("Nội dung một.")
            result = append_records(path, [first])
            self.assertEqual(result.written, 1)
            self.assertEqual(result.skipped, 0)

            records = read_records(path)
            self.assertEqual(len(records), 1)
            self.assertEqual(records[0].content_sha256, first.content_sha256)

    def test_duplicate_is_skipped(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "annotations.jsonl"
            append_records(path, [record("Nội dung một.")])
            before = path.read_bytes()

            result = append_records(path, [record("Nội dung một.")])
            self.assertEqual(result.written, 0)
            self.assertEqual(result.skipped, 1)
            self.assertEqual(path.read_bytes(), before)

    def test_same_body_different_model_is_not_duplicate(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "annotations.jsonl"
            append_records(path, [record("Nội dung một.", model="model-a")])
            result = append_records(path, [record("Nội dung một.", model="model-b")])
            self.assertEqual(result.written, 1)
            self.assertEqual(len(read_records(path)), 2)

    def test_existing_content_is_not_overwritten(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "annotations.jsonl"
            append_records(path, [record("Nội dung gốc.")])
            original = path.read_bytes()

            append_records(path, [record("Nội dung mới.")])
            after = path.read_bytes()

            self.assertTrue(after.startswith(original))
            self.assertEqual(len(read_records(path)), 2)

    def test_missing_file_reads_empty(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            self.assertEqual(read_records(Path(temp) / "none.jsonl"), [])


class ManifestTests(unittest.TestCase):
    def test_counts_and_categories(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            data_dir = Path(temp) / "data"
            path = data_dir / "annotations.jsonl"
            append_records(
                path,
                [
                    record("Nội dung một.", message="a"),
                    record("Nội dung hai.", message="b"),
                ],
            )
            manifest = build_manifest(data_dir)
            self.assertEqual(manifest["totals"]["records"], 2)
            self.assertEqual(manifest["totals"]["documents"], 2)
            self.assertEqual(manifest["totals"]["issues"], 2)
            self.assertEqual(manifest["per_model"]["gpt-oss:120b-cloud"], 2)
            self.assertEqual(manifest["per_category"]["clarity"], 2)

    def test_write_manifest(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            data_dir = Path(temp) / "data"
            append_records(data_dir / "annotations.jsonl", [record("Nội dung một.")])
            target = write_manifest(data_dir)
            payload = json.loads(target.read_text(encoding="utf-8"))
            self.assertEqual(payload["totals"]["records"], 1)

    def test_empty_manifest(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            manifest = build_manifest(Path(temp) / "missing")
            self.assertEqual(manifest["totals"]["records"], 0)
            self.assertEqual(manifest["files"], [])


class ValidationTests(unittest.TestCase):
    def test_invalid_json_line_raises(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "bad.jsonl"
            path.write_text("{not json}\n", encoding="utf-8")
            with self.assertRaises(DatasetError):
                read_records(path)

    def test_invalid_record_raises(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "bad.jsonl"
            path.write_text('{"model": "m"}\n', encoding="utf-8")
            with self.assertRaises(DatasetError):
                read_records(path)


if __name__ == "__main__":
    unittest.main()
