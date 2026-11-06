"""Export annotation records thành dữ liệu SFT cho Student.

Module này chỉ chuẩn bị dữ liệu, không tải model và không huấn luyện.
"""

from __future__ import annotations

import json
import random
from dataclasses import dataclass
from pathlib import Path

from .audit import TRAIN_CATEGORIES
from .dataset import read_documents, read_records
from .schema import AnnotationRecord, DocumentRecord, now_iso
from .teacher import build_prompt
from .text import document_from_body, split_paragraphs


class SFTError(RuntimeError):
    """Không thể export SFT."""


@dataclass(frozen=True)
class ExportResult:
    output_dir: Path
    train_examples: int
    val_examples: int
    skipped_missing_documents: int
    skipped_no_in_scope_issues: int
    info: dict


def _chunk_body(body: str, max_chars: int) -> list[tuple[int, int]]:
    """Chia body theo đoạn, không vượt quá ``max_chars`` nếu có thể."""
    if max_chars <= 0 or len(body) <= max_chars:
        return [(0, len(body))] if body else []

    paragraphs = split_paragraphs(body)
    if not paragraphs:
        return [(0, len(body))]

    chunks: list[tuple[int, int]] = []
    current_start: int | None = None
    current_end = 0

    def flush() -> None:
        nonlocal current_start, current_end
        if current_start is not None:
            chunks.append((current_start, current_end))
            current_start = None

    for paragraph in paragraphs:
        if paragraph.end - paragraph.start > max_chars:
            flush()
            offset = paragraph.start
            while offset < paragraph.end:
                end = min(offset + max_chars, paragraph.end)
                chunks.append((offset, end))
                offset = end
            continue
        if current_start is None:
            current_start, current_end = paragraph.start, paragraph.end
        elif paragraph.end - current_start <= max_chars:
            current_end = paragraph.end
        else:
            flush()
            current_start, current_end = paragraph.start, paragraph.end
    flush()
    return chunks


def _chunks_with_issues(
    record: AnnotationRecord,
    body: str,
    max_chars: int,
    categories: frozenset[str] | set[str],
) -> list[tuple[int, int, int, list]]:
    """Gán mỗi issue vào chunk chứa điểm bắt đầu của span."""
    chunks = _chunk_body(body, max_chars)
    if not chunks:
        return []

    assigned: list[tuple[int, int, int, list]] = []
    for index, (start, end) in enumerate(chunks):
        issues = [
            issue
            for issue in record.issues
            if issue.category in categories
            and issue.span is not None
            and start <= issue.span.start < end
        ]
        if not issues:
            continue
        # Nếu issue vượt quá cuối chunk, mở rộng chunk để quote còn nguyên.
        end = min(len(body), max(end, max(issue.span.end for issue in issues)))
        assigned.append((index, start, end, issues))
    return assigned


def _assistant_payload(
    record: AnnotationRecord,
    categories: frozenset[str] | set[str] | None = None,
    issues: list | None = None,
) -> str:
    """Target đúng schema prompt yêu cầu: dùng ``quote`` thay vì offset nội bộ."""
    allowed = TRAIN_CATEGORIES if categories is None else frozenset(categories)
    selected = record.issues if issues is None else issues
    payload_issues = []
    for issue in selected:
        if issue.category not in allowed:
            continue
        item = {
            "category": issue.category,
            "severity": issue.severity,
            "message": issue.message,
            "suggestion": issue.suggestion,
        }
        if issue.span is not None:
            item["quote"] = issue.span.text
        payload_issues.append(item)
    return json.dumps({"issues": payload_issues}, ensure_ascii=False, sort_keys=True)


def example_from_record(
    record: AnnotationRecord,
    document: DocumentRecord,
    categories: frozenset[str] | set[str] | None = None,
    body: str | None = None,
    title: str | None = None,
    extra_meta: dict | None = None,
    selected_issues: list | None = None,
) -> dict:
    prompt_body = document.body if body is None else body
    prompt_title = document.title if title is None else title
    prompt = build_prompt(
        document_from_body(
            prompt_body, title=prompt_title, path=document.source_path
        )
    )
    allowed = TRAIN_CATEGORIES if categories is None else frozenset(categories)
    payload_issues = record.issues if selected_issues is None else selected_issues
    meta = {
        "content_sha256": record.content_sha256,
        "source_path": record.source_path,
        "title": record.title,
        "model": record.model,
        "issue_count": len(
            [issue for issue in payload_issues if issue.category in allowed]
        ),
    }
    if extra_meta:
        meta.update(extra_meta)
    return {
        "messages": [
            {"role": "user", "content": prompt},
            {
                "role": "assistant",
                "content": _assistant_payload(
                    record, categories=allowed, issues=payload_issues
                ),
            },
        ],
        "meta": meta,
    }


def export_sft(
    annotations_path: str | Path,
    documents_path: str | Path,
    output_dir: str | Path,
    val_ratio: float = 0.2,
    seed: int = 42,
    model: str | None = None,
    categories: frozenset[str] | set[str] | None = None,
    max_chars: int = 6000,
) -> ExportResult:
    if not 0.0 <= val_ratio < 1.0:
        raise SFTError("val_ratio phải trong khoảng [0, 1).")
    if max_chars < 0:
        raise SFTError("max_chars phải >= 0 (0 = không chia).")

    allowed = TRAIN_CATEGORIES if categories is None else frozenset(categories)
    if not allowed:
        raise SFTError("Danh sách category rỗng.")

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
    no_in_scope = 0
    chunks = 0
    for record in records:
        if not any(issue.category in allowed for issue in record.issues):
            no_in_scope += 1
            continue
        document = documents.get(record.content_sha256)
        if document is None:
            missing += 1
            continue
        for chunk_index, start, end, issues in _chunks_with_issues(
            record, document.body, max_chars, allowed
        ):
            chunks += 1
            examples.append(
                (
                    record.content_sha256,
                    example_from_record(
                        record,
                        document,
                        categories=allowed,
                        body=document.body[start:end],
                        title=f"{document.title} [phần {chunk_index + 1}]"
                        if max_chars > 0 and len(document.body) > max_chars
                        else None,
                        extra_meta={
                            "chunk_index": chunk_index,
                            "chunk_start": start,
                            "chunk_end": end,
                        },
                        selected_issues=issues,
                    ),
                )
            )
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
        "categories": sorted(allowed),
        "max_chars": max_chars,
        "train_examples": len(train),
        "val_examples": len(val),
        "chunks_with_issues": chunks,
        "unique_documents": len(hashes),
        "skipped_missing_documents": missing,
        "skipped_no_in_scope_issues": no_in_scope,
    }
    with (out / "dataset_info.json").open("w", encoding="utf-8") as handle:
        json.dump(info, handle, ensure_ascii=False, indent=2, sort_keys=True)
        handle.write("\n")

    return ExportResult(
        output_dir=out,
        train_examples=len(train),
        val_examples=len(val),
        skipped_missing_documents=missing,
        skipped_no_in_scope_issues=no_in_scope,
        info=info,
    )
