"""Export annotation records thành dữ liệu SFT cho Student.

Module này chỉ chuẩn bị dữ liệu, không tải model và không huấn luyện.
"""

from __future__ import annotations

import json
import random
from dataclasses import dataclass
from pathlib import Path

from .dataset import read_documents, read_records
from .schema import AnnotationRecord, DocumentRecord, now_iso
from .teacher import build_prompt
from .text import document_from_body


class SFTError(RuntimeError):
    """Không thể export SFT."""


@dataclass(frozen=True)
class ExportResult:
    output_dir: Path
    train_examples: int
    val_examples: int
    skipped_missing_documents: int
    info: dict


def _assistant_payload(record: AnnotationRecord) -> str:
    """Target đúng schema prompt yêu cầu: dùng ``quote`` thay vì offset nội bộ."""
    issues = []
    for issue in record.issues:
        item = {
            "category": issue.category,
            "severity": issue.severity,
            "message": issue.message,
            "suggestion": issue.suggestion,
        }
        if issue.span is not None:
            item["quote"] = issue.span.text
        issues.append(item)
    return json.dumps({"issues": issues}, ensure_ascii=False, sort_keys=True)


def example_from_record(
    record: AnnotationRecord, document: DocumentRecord
) -> dict:
    prompt = build_prompt(
        document_from_body(document.body, title=document.title, path=document.source_path)
    )
    return {
        "messages": [
            {"role": "user", "content": prompt},
            {"role": "assistant", "content": _assistant_payload(record)},
        ],
        "meta": {
            "content_sha256": record.content_sha256,
            "source_path": record.source_path,
            "title": record.title,
            "model": record.model,
            "issue_count": len(record.issues),
        },
    }


def export_sft(
    annotations_path: str | Path,
    documents_path: str | Path,
    output_dir: str | Path,
    val_ratio: float = 0.2,
    seed: int = 42,
    model: str | None = None,
) -> ExportResult:
    if not 0.0 <= val_ratio < 1.0:
        raise SFTError("val_ratio phải trong khoảng [0, 1).")

    records = [
        record
        for record in read_records(annotations_path)
        if model is None or record.model == model
    ]
    if not records:
        raise SFTError("Không có annotation record nào để export.")

    documents = {doc.content_sha256: doc for doc in read_documents(documents_path)}
    if not documents:
        raise SFTError(
            f"Không có document nào trong {documents_path}. "
            "Chạy backfill-documents trước."
        )

    examples: list[tuple[str, dict]] = []
    missing = 0
    for record in records:
        document = documents.get(record.content_sha256)
        if document is None:
            missing += 1
            continue
        examples.append((record.content_sha256, example_from_record(record, document)))
    if not examples:
        raise SFTError("Không join được annotation với document nào.")

    hashes = sorted({content_hash for content_hash, _ in examples})
    rng = random.Random(seed)
    rng.shuffle(hashes)
    val_count = 0
    if len(hashes) >= 5 and val_ratio > 0:
        val_count = max(1, round(len(hashes) * val_ratio))
    val_hashes = set(hashes[:val_count])

    train = [example for content_hash, example in examples if content_hash not in val_hashes]
    val = [example for content_hash, example in examples if content_hash in val_hashes]
    if not train:
        raise SFTError("Tập train rỗng; giảm val_ratio hoặc thêm dữ liệu.")

    out = Path(output_dir)
    targets = [out / "train.jsonl", out / "val.jsonl", out / "dataset_info.json"]
    existing = [path for path in targets if path.exists()]
    if existing:
        raise SFTError(
            "Output đã tồn tại, không ghi đè: " + ", ".join(str(path) for path in existing)
        )
    out.mkdir(parents=True, exist_ok=True)

    def write_jsonl(path: Path, rows: list[dict]) -> None:
        with path.open("w", encoding="utf-8") as handle:
            for row in rows:
                handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")

    write_jsonl(out / "train.jsonl", train)
    write_jsonl(out / "val.jsonl", val)

    info = {
        "created_at": now_iso(),
        "annotations": str(annotations_path),
        "documents": str(documents_path),
        "seed": seed,
        "val_ratio": val_ratio,
        "model": model,
        "train_examples": len(train),
        "val_examples": len(val),
        "unique_documents": len(hashes),
        "skipped_missing_documents": missing,
    }
    with (out / "dataset_info.json").open("w", encoding="utf-8") as handle:
        json.dump(info, handle, ensure_ascii=False, indent=2, sort_keys=True)
        handle.write("\n")

    return ExportResult(
        output_dir=out,
        train_examples=len(train),
        val_examples=len(val),
        skipped_missing_documents=missing,
        info=info,
    )
