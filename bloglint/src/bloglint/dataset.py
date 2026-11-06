"""Lưu annotation append-only và tổng hợp manifest.

Dataset là JSONL, mỗi dòng một ``AnnotationRecord``. Không bao giờ mở file ở
chế độ ghi đè. Khóa chống trùng là ``(content_sha256, model)``.
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path

from .schema import AnnotationRecord, Document, DocumentRecord, Issue, now_iso


class DatasetError(RuntimeError):
    """Dataset không đọc/ghi được."""


@dataclass(frozen=True)
class AppendResult:
    written: int
    skipped: int
    path: Path


def read_records(path: str | Path) -> list[AnnotationRecord]:
    file_path = Path(path)
    if not file_path.exists():
        return []
    records: list[AnnotationRecord] = []
    with file_path.open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            if not line.strip():
                continue
            try:
                data = json.loads(line)
            except json.JSONDecodeError as exc:
                raise DatasetError(
                    f"{file_path}:{line_number}: JSON không hợp lệ: {exc}"
                ) from exc
            try:
                records.append(AnnotationRecord.from_dict(data))
            except Exception as exc:
                raise DatasetError(
                    f"{file_path}:{line_number}: record không hợp lệ: {exc}"
                ) from exc
    return records


def append_records(
    path: str | Path, records: list[AnnotationRecord]
) -> AppendResult:
    """Append record mới, bỏ qua bản trùng (cùng nội dung + model)."""
    file_path = Path(path)
    file_path.parent.mkdir(parents=True, exist_ok=True)

    existing: set[tuple[str, str]] = {
        (record.content_sha256, record.model) for record in read_records(file_path)
    }
    to_write: list[AnnotationRecord] = []
    skipped = 0
    for record in records:
        key = (record.content_sha256, record.model)
        if key in existing:
            skipped += 1
            continue
        existing.add(key)
        to_write.append(record)

    if to_write:
        with file_path.open("a", encoding="utf-8") as handle:
            for record in to_write:
                handle.write(
                    json.dumps(record.to_dict(), ensure_ascii=False, sort_keys=True) + "\n"
                )

    return AppendResult(written=len(to_write), skipped=skipped, path=file_path)


def make_record(
    document: Document,
    issues: list[Issue],
    model: str,
    meta: dict | None = None,
) -> AnnotationRecord:
    return AnnotationRecord(
        source_path=document.path,
        title=document.title,
        content_sha256=document.content_sha256,
        model=model,
        issues=issues,
        meta=meta or {},
    )


def read_documents(path: str | Path) -> list[DocumentRecord]:
    file_path = Path(path)
    if not file_path.exists():
        return []
    documents: list[DocumentRecord] = []
    with file_path.open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            if not line.strip():
                continue
            try:
                data = json.loads(line)
            except json.JSONDecodeError as exc:
                raise DatasetError(
                    f"{file_path}:{line_number}: JSON không hợp lệ: {exc}"
                ) from exc
            try:
                documents.append(DocumentRecord.from_dict(data))
            except Exception as exc:
                raise DatasetError(
                    f"{file_path}:{line_number}: document không hợp lệ: {exc}"
                ) from exc
    return documents


def append_documents(
    path: str | Path, documents: list[DocumentRecord]
) -> AppendResult:
    """Append document mới, bỏ qua bản trùng theo content_sha256."""
    file_path = Path(path)
    file_path.parent.mkdir(parents=True, exist_ok=True)

    existing = {document.content_sha256 for document in read_documents(file_path)}
    to_write: list[DocumentRecord] = []
    skipped = 0
    for document in documents:
        if document.content_sha256 in existing:
            skipped += 1
            continue
        existing.add(document.content_sha256)
        to_write.append(document)

    if to_write:
        with file_path.open("a", encoding="utf-8") as handle:
            for document in to_write:
                handle.write(
                    json.dumps(document.to_dict(), ensure_ascii=False, sort_keys=True) + "\n"
                )

    return AppendResult(written=len(to_write), skipped=skipped, path=file_path)


def make_document_record(document: Document) -> DocumentRecord:
    return DocumentRecord(
        content_sha256=document.content_sha256,
        title=document.title,
        source_path=document.path,
        body=document.body,
        meta={"front_matter_keys": sorted(document.front_matter.keys())},
    )


def build_manifest(data_dir: str | Path) -> dict:
    data_path = Path(data_dir)
    files = sorted(
        path
        for path in data_path.glob("*.jsonl")
        if path.name != "documents.jsonl"
    )
    per_model: dict[str, int] = {}
    per_category: dict[str, int] = {}
    documents: set[str] = set()
    total_records = 0
    total_issues = 0
    file_stats: list[dict] = []

    for file_path in files:
        records = read_records(file_path)
        total_records += len(records)
        file_issues = 0
        for record in records:
            per_model[record.model] = per_model.get(record.model, 0) + 1
            documents.add(record.content_sha256)
            for issue in record.issues:
                per_category[issue.category] = per_category.get(issue.category, 0) + 1
                file_issues += 1
        total_issues += file_issues
        file_stats.append(
            {
                "name": file_path.name,
                "records": len(records),
                "issues": file_issues,
                "size_bytes": file_path.stat().st_size,
            }
        )

    return {
        "generated_at": now_iso(),
        "data_dir": str(data_path),
        "files": file_stats,
        "totals": {
            "records": total_records,
            "documents": len(documents),
            "issues": total_issues,
        },
        "per_model": dict(sorted(per_model.items())),
        "per_category": dict(sorted(per_category.items())),
    }


def write_manifest(data_dir: str | Path, manifest: dict | None = None) -> Path:
    data_path = Path(data_dir)
    data_path.mkdir(parents=True, exist_ok=True)
    target = data_path / "manifest.json"
    payload = manifest if manifest is not None else build_manifest(data_path)

    temp = target.with_name(target.name + ".tmp")
    with temp.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, ensure_ascii=False, indent=2, sort_keys=True)
        handle.write("\n")
    os.replace(temp, target)
    return target
