"""Đánh giá output của Student trên annotation đã có.

Student được kỳ vọng trả về JSON issue có ``quote``. Module này:

1. đọc predictions JSONL;
2. tìm lại quote trong body để lấy span;
3. so với gold annotation (category + span giao nhau);
4. báo precision/recall/F1 micro và theo category.

Không gọi model, không tải checkpoint.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path

from .audit import TRAIN_CATEGORIES
from .dataset import read_documents, read_records
from .schema import AnnotationRecord, DocumentRecord, Issue, Span
from .teacher import _find_quote_span


class StudentEvalError(RuntimeError):
    """Prediction hoặc gold không hợp lệ."""


@dataclass
class Prediction:
    source_path: str
    content_sha256: str
    issues: list[dict] = field(default_factory=list)
    raw_ok: bool = True
    error: str = ""


def _issues_from_payload(payload: dict) -> list[dict]:
    issues = payload.get("issues")
    if issues is None and isinstance(payload.get("messages"), list):
        assistant = [
            message
            for message in payload["messages"]
            if isinstance(message, dict) and message.get("role") == "assistant"
        ]
        if not assistant:
            raise StudentEvalError("messages không có assistant.")
        content = assistant[-1].get("content", "")
        try:
            payload = json.loads(content)
        except json.JSONDecodeError as exc:
            raise StudentEvalError(f"assistant content không phải JSON: {exc}") from exc
        issues = payload.get("issues")
    if not isinstance(issues, list):
        raise StudentEvalError("prediction phải có mảng 'issues'.")
    return issues


def load_predictions(path: str | Path) -> dict[str, Prediction]:
    file_path = Path(path)
    if not file_path.exists():
        raise StudentEvalError(f"Không tìm thấy predictions: {file_path}")

    predictions: dict[str, Prediction] = {}
    with file_path.open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            if not line.strip():
                continue
            try:
                payload = json.loads(line)
            except json.JSONDecodeError as exc:
                raise StudentEvalError(
                    f"{file_path}:{line_number}: JSON không hợp lệ: {exc}"
                ) from exc
            if not isinstance(payload, dict):
                raise StudentEvalError(f"{file_path}:{line_number}: phải là object.")

            source_path = str(payload.get("source_path", ""))
            content_sha256 = str(payload.get("content_sha256", ""))
            if not content_sha256:
                raise StudentEvalError(
                    f"{file_path}:{line_number}: thiếu content_sha256."
                )
            try:
                issues = _issues_from_payload(payload)
            except StudentEvalError as exc:
                predictions[content_sha256] = Prediction(
                    source_path=source_path,
                    content_sha256=content_sha256,
                    raw_ok=False,
                    error=str(exc),
                )
                continue
            predictions[content_sha256] = Prediction(
                source_path=source_path,
                content_sha256=content_sha256,
                issues=issues,
            )
    return predictions


def _resolve_predicted_issues(
    prediction: Prediction,
    document: DocumentRecord,
    categories: frozenset[str] | set[str],
) -> tuple[list[Issue], int, list[dict]]:
    issues: list[Issue] = []
    invalid = 0
    invalid_details: list[dict] = []
    for index, item in enumerate(prediction.issues):
        if not isinstance(item, dict):
            invalid += 1
            invalid_details.append(
                {"index": index, "reason": "issue không phải object"}
            )
            continue
        category = item.get("category")
        severity = item.get("severity", "warning")
        message = item.get("message", "")
        suggestion = item.get("suggestion", "")
        quote = item.get("quote")
        if category not in categories:
            continue
        if not isinstance(quote, str) or not quote.strip():
            invalid += 1
            invalid_details.append(
                {"index": index, "reason": "thiếu quote", "category": category}
            )
            continue
        span = _find_quote_span(document.body, quote)
        if span is None:
            invalid += 1
            invalid_details.append(
                {
                    "index": index,
                    "reason": "quote không khớp body",
                    "category": category,
                    "quote": quote,
                }
            )
            continue
        try:
            issues.append(
                Issue(
                    category=category,
                    severity=severity,
                    message=message or "prediction",
                    suggestion=suggestion,
                    span=span,
                    source="teacher",
                )
            )
        except Exception as exc:  # schema error từ output model
            invalid += 1
            invalid_details.append(
                {"index": index, "reason": f"issue không hợp lệ: {exc}"}
            )
    return issues, invalid, invalid_details


def _match(
    predicted: list[Issue], gold: list[Issue]
) -> tuple[int, int, int, list[dict], list[dict], list[tuple[Issue, Issue]]]:
    used: set[int] = set()
    true_positives = 0
    missed: list[dict] = []
    matches: list[tuple[Issue, Issue]] = []
    for gold_issue in gold:
        match_index = None
        for index, predicted_issue in enumerate(predicted):
            if index in used:
                continue
            if predicted_issue.category != gold_issue.category:
                continue
            if gold_issue.span is None or predicted_issue.span is None:
                continue
            if gold_issue.span.overlaps(predicted_issue.span):
                match_index = index
                break
        if match_index is None:
            missed.append(
                {
                    "category": gold_issue.category,
                    "message": gold_issue.message,
                    "span": gold_issue.span.to_dict() if gold_issue.span else None,
                }
            )
        else:
            used.add(match_index)
            true_positives += 1
            matches.append((gold_issue, predicted[match_index]))
    false_positives = [
        {
            "category": issue.category,
            "message": issue.message,
            "span": issue.span.to_dict() if issue.span else None,
        }
        for index, issue in enumerate(predicted)
        if index not in used
    ]
    return (
        true_positives,
        len(false_positives),
        len(missed),
        missed,
        false_positives,
        matches,
    )


def _safe_div(numerator: int, denominator: int) -> float:
    return numerator / denominator if denominator else 0.0


def _metrics(tp: int, fp: int, fn: int) -> dict:
    precision = _safe_div(tp, tp + fp)
    recall = _safe_div(tp, tp + fn)
    f1 = _safe_div(2 * precision * recall, precision + recall)
    return {
        "true_positives": tp,
        "false_positives": fp,
        "false_negatives": fn,
        "precision": precision,
        "recall": recall,
        "f1": f1,
    }


def _split_hashes(path: str | Path | None) -> set[str] | None:
    if path is None:
        return None
    file_path = Path(path)
    if not file_path.exists():
        raise StudentEvalError(f"Không tìm thấy split: {file_path}")
    hashes: set[str] = set()
    with file_path.open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            if not line.strip():
                continue
            try:
                payload = json.loads(line)
            except json.JSONDecodeError as exc:
                raise StudentEvalError(
                    f"{file_path}:{line_number}: JSON không hợp lệ: {exc}"
                ) from exc
            meta = payload.get("meta", {})
            content_hash = meta.get("content_sha256") or payload.get("content_sha256")
            if not content_hash:
                raise StudentEvalError(
                    f"{file_path}:{line_number}: thiếu content_sha256."
                )
            hashes.add(str(content_hash))
    return hashes


def evaluate_predictions(
    predictions_path: str | Path,
    annotations_path: str | Path,
    documents_path: str | Path,
    split_path: str | Path | None = None,
    categories: frozenset[str] | set[str] | None = None,
) -> dict:
    allowed = TRAIN_CATEGORIES if categories is None else frozenset(categories)
    if not allowed:
        raise StudentEvalError("Danh sách category rỗng.")

    predictions = load_predictions(predictions_path)
    documents = {doc.content_sha256: doc for doc in read_documents(documents_path)}
    records = read_records(annotations_path)
    split_hashes = _split_hashes(split_path)

    totals = {"tp": 0, "fp": 0, "fn": 0}
    per_category: dict[str, dict[str, int]] = {}
    invalid_quotes = 0
    invalid_details: list[dict] = []
    missing_predictions: list[str] = []
    evaluated_documents = 0
    skipped_documents = 0
    gold_issues = 0
    predicted_issues = 0
    per_document: list[dict] = []

    for record in records:
        if split_hashes is not None and record.content_sha256 not in split_hashes:
            continue
        document = documents.get(record.content_sha256)
        if document is None:
            skipped_documents += 1
            continue
        gold = [
            issue
            for issue in record.issues
            if issue.category in allowed and issue.span is not None
        ]
        prediction = predictions.get(record.content_sha256)
        invalid = 0
        details: list[dict] = []
        if prediction is None:
            missing_predictions.append(record.source_path)
            predicted: list[Issue] = []
        else:
            predicted, invalid, details = _resolve_predicted_issues(
                prediction, document, allowed
            )
            invalid_quotes += invalid
            for detail in details:
                invalid_details.append(
                    {"source_path": record.source_path, **detail}
                )

        tp, fp, fn, missed, false_positives, matches = _match(predicted, gold)
        totals["tp"] += tp
        totals["fp"] += fp + invalid
        totals["fn"] += fn
        evaluated_documents += 1
        gold_issues += len(gold)
        predicted_issues += len(predicted)

        for gold_issue in gold:
            per_category.setdefault(gold_issue.category, {"tp": 0, "fp": 0, "fn": 0})
        for issue in predicted:
            per_category.setdefault(issue.category, {"tp": 0, "fp": 0, "fn": 0})

        for gold_issue, _ in matches:
            per_category[gold_issue.category]["tp"] += 1
        for gold_issue in gold:
            if not any(
                gold_issue is matched_gold for matched_gold, _ in matches
            ):
                per_category[gold_issue.category]["fn"] += 1
        matched_predictions = {id(pred_issue) for _, pred_issue in matches}
        for pred_issue in predicted:
            if id(pred_issue) not in matched_predictions:
                per_category[pred_issue.category]["fp"] += 1
        for detail in details:
            category = detail.get("category")
            if category in per_category:
                per_category[category]["fp"] += 1

        per_document.append(
            {
                "source_path": record.source_path,
                "content_sha256": record.content_sha256,
                "gold_issues": len(gold),
                "predicted_issues": len(predicted),
                "true_positives": tp,
                "false_positives": fp,
                "false_negatives": fn,
            }
        )

    overall = _metrics(totals["tp"], totals["fp"], totals["fn"])
    predicted_total = predicted_issues + invalid_quotes
    result = {
        "predictions_path": str(predictions_path),
        "annotations_path": str(annotations_path),
        "documents_path": str(documents_path),
        "split_path": str(split_path) if split_path else None,
        "categories": sorted(allowed),
        "documents": {
            "evaluated": evaluated_documents,
            "skipped_missing_document": skipped_documents,
            "missing_predictions": len(missing_predictions),
        },
        "issues": {
            "gold": gold_issues,
            "predicted_valid": predicted_issues,
            "predicted_invalid": invalid_quotes,
            "quote_match_rate": _safe_div(predicted_issues, predicted_total),
        },
        "overall": overall,
        "per_category": {
            category: _metrics(values["tp"], values["fp"], values["fn"])
            for category, values in sorted(per_category.items())
        },
        "missing_predictions": missing_predictions,
        "invalid_predictions": invalid_details,
        "per_document": per_document,
    }
    return result
