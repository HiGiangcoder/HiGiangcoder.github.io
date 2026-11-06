"""Đánh giá analyzer trên golden fixture.

Metrics là micro-average theo issue. Một issue được coi là đúng khi cùng
``category`` và span giao nhau (hoặc cùng không có span).
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable

from .diagnostics import analyze_body
from .schema import Issue, SchemaError, Span, TEACHER_CATEGORIES, SEVERITIES


class EvaluationError(RuntimeError):
    """Golden fixture hoặc phép đánh giá không hợp lệ."""


@dataclass
class GoldCase:
    id: str
    title: str
    body: str
    issues: list[Issue] = field(default_factory=list)


def _resolve_span(data: dict, body: str, label: str) -> Span | None:
    span_data = data.get("span")
    if span_data is not None:
        if not isinstance(span_data, dict):
            raise EvaluationError(f"{label}: span phải là object.")
        start = span_data.get("start")
        end = span_data.get("end")
        if not isinstance(start, int) or not isinstance(end, int):
            raise EvaluationError(f"{label}: span.start/end phải là số nguyên.")
        if start < 0 or end < start or end > len(body):
            raise EvaluationError(f"{label}: span nằm ngoài body.")
        return Span(start=start, end=end, text=body[start:end])

    quote = data.get("quote")
    if not quote:
        return None
    if not isinstance(quote, str):
        raise EvaluationError(f"{label}: quote phải là chuỗi.")
    occurrence = data.get("occurrence", 0)
    if not isinstance(occurrence, int) or occurrence < 0:
        raise EvaluationError(f"{label}: occurrence phải là số nguyên >= 0.")

    position = -1
    for _ in range(occurrence + 1):
        position = body.find(quote, position + 1)
        if position == -1:
            raise EvaluationError(f"{label}: không tìm thấy quote lần {occurrence}.")
    return Span(start=position, end=position + len(quote), text=quote)


def load_golden(path: str | Path) -> list[GoldCase]:
    file_path = Path(path)
    if not file_path.exists():
        raise EvaluationError(f"Không tìm thấy golden fixture: {file_path}")

    cases: list[GoldCase] = []
    with file_path.open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            if not line.strip():
                continue
            try:
                data = json.loads(line)
            except json.JSONDecodeError as exc:
                raise EvaluationError(
                    f"{file_path}:{line_number}: JSON không hợp lệ: {exc}"
                ) from exc
            if not isinstance(data, dict):
                raise EvaluationError(f"{file_path}:{line_number}: case phải là object.")

            body = data.get("body")
            if not isinstance(body, str) or not body.strip():
                raise EvaluationError(f"{file_path}:{line_number}: thiếu body.")

            issues: list[Issue] = []
            for index, item in enumerate(data.get("issues", [])):
                label = f"{file_path}:{line_number}:issues[{index}]"
                if not isinstance(item, dict):
                    raise EvaluationError(f"{label}: phải là object.")
                category = item.get("category", "")
                if category not in TEACHER_CATEGORIES | {
                    "sentence_too_long",
                    "paragraph_too_long",
                    "filler_word",
                    "cliche",
                    "repetition",
                    "punctuation",
                    "passive_overuse",
                    "structure",
                }:
                    raise EvaluationError(f"{label}: category không hợp lệ: {category!r}")
                severity = item.get("severity", "warning")
                if severity not in SEVERITIES:
                    raise EvaluationError(f"{label}: severity không hợp lệ: {severity!r}")
                try:
                    issues.append(
                        Issue(
                            category=category,
                            severity=severity,
                            message=item.get("message", "gold"),
                            suggestion=item.get("suggestion", ""),
                            span=_resolve_span(item, body, label),
                            source="rule",
                        )
                    )
                except SchemaError as exc:
                    raise EvaluationError(f"{label}: {exc}") from exc

            cases.append(
                GoldCase(
                    id=str(data.get("id", f"case-{len(cases) + 1}")),
                    title=str(data.get("title", "")),
                    body=body,
                    issues=issues,
                )
            )
    if not cases:
        raise EvaluationError(f"Golden fixture rỗng: {file_path}")
    return cases


def _spans_match(gold: Span | None, predicted: Span | None) -> bool:
    if gold is None or predicted is None:
        return gold is None and predicted is None
    return gold.start < predicted.end and predicted.start < gold.end


def _match_case(
    predicted: list[Issue], gold: list[Issue]
) -> tuple[int, int, int, list[dict]]:
    used: set[int] = set()
    true_positives = 0
    missed: list[Issue] = []

    for gold_issue in gold:
        match_index = None
        for index, predicted_issue in enumerate(predicted):
            if index in used:
                continue
            if predicted_issue.category != gold_issue.category:
                continue
            if _spans_match(gold_issue.span, predicted_issue.span):
                match_index = index
                break
        if match_index is None:
            missed.append(gold_issue)
        else:
            used.add(match_index)
            true_positives += 1

    false_positives = [
        predicted_issue
        for index, predicted_issue in enumerate(predicted)
        if index not in used
    ]
    details = [
        {
            "category": issue.category,
            "message": issue.message,
            "span": issue.span.to_dict() if issue.span else None,
        }
        for issue in missed
    ]
    return true_positives, len(false_positives), len(missed), details


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


Analyzer = Callable[[str, str], list[Issue]]


def evaluate(
    cases: list[GoldCase], analyzer: Analyzer | None = None
) -> dict:
    analyzer = analyzer or (lambda body, title: analyze_body(body, title=title))

    total_tp = total_fp = total_fn = 0
    per_category: dict[str, dict[str, int]] = {}
    case_results: list[dict] = []

    for case in cases:
        predicted = analyzer(case.body, case.title)
        tp, fp, fn, missed = _match_case(predicted, case.issues)
        total_tp += tp
        total_fp += fp
        total_fn += fn

        for category in sorted(
            {*[i.category for i in predicted], *[i.category for i in case.issues]}
        ):
            bucket = per_category.setdefault(
                category,
                {"true_positives": 0, "false_positives": 0, "false_negatives": 0},
            )
            pred_cat = [i for i in predicted if i.category == category]
            gold_cat = [i for i in case.issues if i.category == category]
            cat_tp, cat_fp, cat_fn, _ = _match_case(pred_cat, gold_cat)
            bucket["true_positives"] += cat_tp
            bucket["false_positives"] += cat_fp
            bucket["false_negatives"] += cat_fn

        case_results.append(
            {
                "id": case.id,
                "predicted": len(predicted),
                "gold": len(case.issues),
                "true_positives": tp,
                "false_positives": fp,
                "false_negatives": fn,
                "missed": missed,
            }
        )

    per_category_metrics = {
        category: _metrics(
            values["true_positives"],
            values["false_positives"],
            values["false_negatives"],
        )
        for category, values in sorted(per_category.items())
    }
    return {
        "cases": len(cases),
        "overall": _metrics(total_tp, total_fp, total_fn),
        "per_category": per_category_metrics,
        "case_results": case_results,
    }


def benchmark(golden_path: str | Path, analyzer: Analyzer | None = None) -> dict:
    return evaluate(load_golden(golden_path), analyzer=analyzer)
