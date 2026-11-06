from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from bloglint.dataset import append_documents, append_records, make_document_record, make_record
from bloglint.schema import Issue, Span
from bloglint.sft import SFTError, export_sft
from bloglint.text import load_document


def write_post(path: Path, body: str, title: str = "Bài") -> Path:
    path.write_text(f"---\ntitle: {title}\n---\n{body}", encoding="utf-8")
    return path


def prepare(
    temp: Path, posts: list[tuple[str, str]], model: str = "teacher"
) -> tuple[Path, Path]:
    data_dir = temp / "data"
    annotations = data_dir / "annotations.jsonl"
    documents = data_dir / "documents.jsonl"

    records = []
    sidecars = []
    for index, (name, body) in enumerate(posts):
        path = write_post(temp / name, body)
        document = load_document(path)
        records.append(
            make_record(
                document,
                [
                    Issue(
                        category="clarity",
                        severity="info",
                        message=f"lỗi {index}",
                        span=Span(start=0, end=3, text=body[:3]),
                    )
                ],
                model=model,
            )
        )
        sidecars.append(make_document_record(document))

    append_records(annotations, records)
    append_documents(documents, sidecars)
    return annotations, documents


class ExportTests(unittest.TestCase):
    def test_export_creates_disjoint_train_val(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            temp_path = Path(temp)
            posts = [(f"bai-{index}.md", f"Nội dung bài số {index}.") for index in range(6)]
            annotations, documents = prepare(temp_path, posts)
            output = temp_path / "sft"

            result = export_sft(annotations, documents, output, val_ratio=0.34, seed=7)
            self.assertEqual(result.train_examples + result.val_examples, 6)
            self.assertGreater(result.val_examples, 0)
            self.assertLess(result.val_examples, 6)

            train = [
                json.loads(line)
                for line in (output / "train.jsonl").read_text(encoding="utf-8").splitlines()
            ]
            val = [
                json.loads(line)
                for line in (output / "val.jsonl").read_text(encoding="utf-8").splitlines()
            ]
            train_hashes = {row["meta"]["content_sha256"] for row in train}
            val_hashes = {row["meta"]["content_sha256"] for row in val}
            self.assertFalse(train_hashes & val_hashes)

            assistant = json.loads(train[0]["messages"][1]["content"])
            self.assertIn("quote", assistant["issues"][0])
            self.assertNotIn("span", assistant["issues"][0])

            info = json.loads((output / "dataset_info.json").read_text(encoding="utf-8"))
            self.assertEqual(info["train_examples"], len(train))
            self.assertEqual(info["val_examples"], len(val))
            self.assertEqual(info["unique_documents"], 6)

    def test_export_refuses_to_overwrite(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            temp_path = Path(temp)
            annotations, documents = prepare(
                temp_path, [("bai.md", "Nội dung bài.")]
            )
            output = temp_path / "sft"
            export_sft(annotations, documents, output, val_ratio=0.0)

            with self.assertRaises(SFTError):
                export_sft(annotations, documents, output, val_ratio=0.0)

    def test_export_without_documents_fails(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            temp_path = Path(temp)
            annotations, documents = prepare(
                temp_path, [("bai.md", "Nội dung bài.")]
            )
            documents.unlink()

            with self.assertRaises(SFTError):
                export_sft(annotations, documents, temp_path / "sft")

    def test_model_filter(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            temp_path = Path(temp)
            annotations, documents = prepare(
                temp_path, [("bai.md", "Nội dung bài.")], model="model-a"
            )
            with self.assertRaises(SFTError):
                export_sft(
                    annotations,
                    documents,
                    temp_path / "sft",
                    model="model-b",
                )


if __name__ == "__main__":
    unittest.main()
