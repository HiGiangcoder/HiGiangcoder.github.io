"""Audit dataset annotation trước khi export SFT.

Module này chỉ đọc dữ liệu và tạo báo cáo; không sửa dataset, không gọi mạng.
"""

from __future__ import annotations

import hashlib
from pathlib import Path

from .dataset import read_documents, read_records
from .schema import AnnotationRecord, DocumentRecord, Issue, now_iso

# Category dùng cho SFT chính. Factual chỉ để tham khảo vì cần kiểm chứng ngoài.
TRAIN_CATEGORIES = frozenset({"clarity", "coherence", "grammar", "spelling", "style"})

SHORT_QUOTE_CHARS = 16
SHORT_QUOTE_WORDS = 3


def _issue_ref(
    record: AnnotationRecord, index: int, issue: Issue, reason: str
) -> dict:
    return {
        "source_path": record.source_path,
        "content_sha256": record.content_sha256,
        "issue_index": index,
        "category": issue.category,
        "severity": issue.severity,
        "reason": reason,
        "message": issue.message,
        "quote": issue.span.text if issue.span else None,
        "span": issue.span.to_dict() if issue.span else None,
    }


def _span_key(issue: Issue) -> tuple[int, int] | None:
    if issue.span is None:
        return None
    return (issue.span.start, issue.span.end)


def audit_dataset(
    annotations_path: str | Path, documents_path: str | Path
) -> dict:
    records = read_records(annotations_path)
    documents = {doc.content_sha256: doc for doc in read_documents(documents_path)}

    per_category: dict[str, int] = {}
    per_severity: dict[str, int] = {}
    per_model: dict[str, int] = {}
    train_category_issues = 0

    missing_documents: list[dict] = []
    body_hash_mismatches: list[dict] = []
    span_mismatches: list[dict] = []
    duplicate_issues: list[dict] = []
    same_span_multiple_categories: list[dict] = []
    overlapping_same_category: list[dict] = []
    short_quotes: list[dict] = []
    missing_suggestions: list[dict] = []
    factual_needs_review: list[dict] = []
    out_of_scope: list[dict] = []

    for record in records:
        per_model[record.model] = per_model.get(record.model, 0) + 1
        document = documents.get(record.content_sha256)
        if document is None:
            missing_documents.append(
                {
                    "source_path": record.source_path,
                    "content_sha256": record.content_sha256,
                }
            )
            continue
        actual_hash = hashlib.sha256(document.body.encode("utf-8")).hexdigest()
        if actual_hash != document.content_sha256:
            body_hash_mismatches.append(
                {
                    "source_path": record.source_path,
                    "content_sha256": document.content_sha256,
                    "actual_sha256": actual_hash,
                }
            )

        per_key: dict[tuple[str, int, int], list[int]] = {}
        per_span: dict[tuple[int, int], list[tuple[int, str]]] = {}
        per_category_spans: dict[str, list[tuple[int, int, Issue, int]]] = {}

        for index, issue in enumerate(record.issues):
            per_category[issue.category] = per_category.get(issue.category, 0) + 1
            per_severity[issue.severity] = per_severity.get(issue.severity, 0) + 1
            if issue.category in TRAIN_CATEGORIES:
                train_category_issues += 1
            else:
                out_of_scope.append(_issue_ref(record, index, issue, "ngoài category train"))

            if issue.category == "factual":
                factual_needs_review.append(
                    _issue_ref(record, index, issue, "factual cần kiểm chứng thủ công")
                )
            if not issue.suggestion.strip():
                missing_suggestions.append(
                    _issue_ref(record, index, issue, "thiếu suggestion")
                )

            if issue.span is None:
                span_mismatches.append(
                    _issue_ref(record, index, issue, "issue không có span/quote")
                )
                continue

            start, end = issue.span.start, issue.span.end
            if start < 0 or end < start or end > len(document.body):
                span_mismatches.append(
                    _issue_ref(record, index, issue, "span nằm ngoài body")
                )
                continue
            if document.body[start:end] != issue.span.text:
                span_mismatches.append(
                    _issue_ref(record, index, issue, "span.text không khớp body")
                )

            quote = issue.span.text.strip()
            if len(quote) < SHORT_QUOTE_CHARS or len(quote.split()) < SHORT_QUOTE_WORDS:
                short_quotes.append(
                    _issue_ref(record, index, issue, "quote quá ngắn, tín hiệu yếu")
                )

            key = (issue.category, start, end)
            per_key.setdefault(key, []).append(index)
            per_span.setdefault((start, end), []).append((index, issue.category))
            per_category_spans.setdefault(issue.category, []).append(
                (start, end, issue, index)
            )

        for (category, start, end), indices in per_key.items():
            if len(indices) > 1:
                duplicate_issues.append(
                    {
                        "source_path": record.source_path,
                        "category": category,
                        "span": {"start": start, "end": end},
                        "issue_indices": indices,
                    }
                )

        for (start, end), entries in per_span.items():
            categories = {category for _, category in entries}
            if len(categories) > 1:
                same_span_multiple_categories.append(
                    {
                        "source_path": record.source_path,
                        "span": {"start": start, "end": end},
                        "categories": sorted(categories),
                        "issue_indices": [index for index, _ in entries],
                    }
                )

        for category, entries in per_category_spans.items():
            for position, (start, end, issue, index) in enumerate(entries):
                for other_start, other_end, other_issue, other_index in entries[position + 1 :]:
                    if start < other_end and other_start < end:
                        overlapping_same_category.append(
                            {
                                "source_path": record.source_path,
                                "category": category,
                                "span": {"start": start, "end": end},
                                "other_span": {"start": other_start, "end": other_end},
                                "issue_indices": [index, other_index],
                                "messages": [issue.message, other_issue.message],
                            }
                        )

    blocking = (
        len(missing_documents)
        + len(body_hash_mismatches)
        + len(span_mismatches)
        + len(duplicate_issues)
    )
    warnings = (
        len(same_span_multiple_categories)
        + len(overlapping_same_category)
        + len(short_quotes)
        + len(missing_suggestions)
        + len(factual_needs_review)
        + sum(1 for item in out_of_scope if item["category"] != "factual")
    )

    return {
        "generated_at": now_iso(),
        "annotations_path": str(annotations_path),
        "documents_path": str(documents_path),
        "totals": {
            "records": len(records),
            "documents": len(documents),
            "issues": sum(per_category.values()),
            "train_category_issues": train_category_issues,
            "blocking": blocking,
            "warnings": warnings,
        },
        "per_category": dict(sorted(per_category.items())),
        "per_severity": dict(sorted(per_severity.items())),
        "per_model": dict(sorted(per_model.items())),
        "findings": {
            "missing_documents": missing_documents,
            "body_hash_mismatches": body_hash_mismatches,
            "span_mismatches": span_mismatches,
            "duplicate_issues": duplicate_issues,
            "same_span_multiple_categories": same_span_multiple_categories,
            "overlapping_same_category": overlapping_same_category,
            "short_quotes": short_quotes,
            "missing_suggestions": missing_suggestions,
            "factual_needs_review": factual_needs_review,
            "out_of_scope": out_of_scope,
        },
    }


def render_review_markdown(
    report: dict,
    records: list[AnnotationRecord],
    documents: list[DocumentRecord],
) -> str:
    """Tạo review sheet đọc được, mỗi issue có checkbox để người dùng duyệt."""
    by_hash = {document.content_sha256: document for document in documents}
    lines = [
        "# BlogLint dataset review",
        "",
        f"- Sinh lúc: {report['generated_at']}",
        f"- Record: {report['totals']['records']}",
        f"- Document: {report['totals']['documents']}",
        f"- Issue: {report['totals']['issues']}",
        f"- Blocking: {report['totals']['blocking']}",
        f"- Warning: {report['totals']['warnings']}",
        "",
        "Quy ước: đánh dấu `[x]` nếu issue đúng và muốn giữ làm target SFT.",
        "Sửa trực tiếp nội dung nếu cần; quyết định cuối cùng nên được lưu riêng.",
        "",
    ]

    for record in records:
        document = by_hash.get(record.content_sha256)
        lines.append(f"## {record.title or record.source_path}")
        lines.append("")
        lines.append(f"- Nguồn: `{record.source_path}`")
        lines.append(f"- Hash: `{record.content_sha256}`")
        lines.append(f"- Model: `{record.model}`")
        if document is None:
            lines.append("- **THIẾU DOCUMENT**")
        lines.append("")
        for index, issue in enumerate(record.issues):
            category = issue.category
            if category == "factual":
                note = " [factual: cần kiểm chứng ngoài]"
            elif category not in TRAIN_CATEGORIES:
                note = " [ngoài category train]"
            else:
                note = ""
            lines.append(
                f"- [ ] **{index}. {category}/{issue.severity}**{note}: {issue.message}"
            )
            if issue.suggestion:
                lines.append(f"  - Gợi ý: {issue.suggestion}")
            if issue.span:
                lines.append(f"  - Quote: `{issue.span.text}`")
            else:
                lines.append("  - Quote: **THIẾU**")
        lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def write_review_sheet(
    annotations_path: str | Path,
    documents_path: str | Path,
    output_path: str | Path,
) -> Path:
    report = audit_dataset(annotations_path, documents_path)
    records = read_records(annotations_path)
    documents = read_documents(documents_path)
    target = Path(output_path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(
        render_review_markdown(report, records, documents), encoding="utf-8"
    )
    return target
