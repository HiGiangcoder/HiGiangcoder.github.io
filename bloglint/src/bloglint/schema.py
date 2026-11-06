from __future__ import annotations

import hashlib
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


class SchemaError(ValueError):
    """Dữ liệu không khớp schema BlogLint."""


SEVERITIES = ("info", "warning", "error")
SEVERITY_WEIGHTS = {"info": 1, "warning": 3, "error": 6}
SOURCES = ("rule", "teacher")

# Nhóm lỗi rule-based.
RULE_CATEGORIES = frozenset(
    {
        "sentence_too_long",
        "paragraph_too_long",
        "filler_word",
        "cliche",
        "repetition",
        "punctuation",
        "passive_overuse",
        "structure",
    }
)

# Nhóm lỗi teacher có thể trả về.
TEACHER_CATEGORIES = frozenset(
    {
        "clarity",
        "coherence",
        "grammar",
        "spelling",
        "style",
        "factual",
        "punctuation",
        "other",
    }
)

CATEGORIES = RULE_CATEGORIES | TEACHER_CATEGORIES


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _require_str(value: Any, name: str, allow_empty: bool = False) -> str:
    if not isinstance(value, str):
        raise SchemaError(f"{name} phải là chuỗi")
    if not allow_empty and not value.strip():
        raise SchemaError(f"{name} không được rỗng")
    return value


def _require_int(value: Any, name: str, minimum: int | None = None) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise SchemaError(f"{name} phải là số nguyên")
    if minimum is not None and value < minimum:
        raise SchemaError(f"{name} phải >= {minimum}")
    return value


@dataclass(frozen=True)
class Span:
    start: int
    end: int
    text: str

    def __post_init__(self) -> None:
        _require_int(self.start, "span.start", 0)
        _require_int(self.end, "span.end", 0)
        _require_str(self.text, "span.text", allow_empty=True)
        if self.end < self.start:
            raise SchemaError("span.end phải >= span.start")

    def to_dict(self) -> dict:
        return {"start": self.start, "end": self.end, "text": self.text}

    @classmethod
    def from_dict(cls, data: dict) -> "Span":
        if not isinstance(data, dict):
            raise SchemaError("span phải là object")
        return cls(
            start=_require_int(data.get("start"), "span.start", 0),
            end=_require_int(data.get("end"), "span.end", 0),
            text=_require_str(data.get("text", ""), "span.text", allow_empty=True),
        )

    def overlaps(self, other: "Span") -> bool:
        return self.start < other.end and other.start < self.end


@dataclass
class Issue:
    category: str
    severity: str
    message: str
    suggestion: str = ""
    span: Span | None = None
    source: str = "rule"
    paragraph: int | None = None
    confidence: float | None = None

    def __post_init__(self) -> None:
        if self.category not in CATEGORIES:
            raise SchemaError(f"category không hợp lệ: {self.category}")
        if self.severity not in SEVERITIES:
            raise SchemaError(f"severity không hợp lệ: {self.severity}")
        _require_str(self.message, "message")
        _require_str(self.suggestion, "suggestion", allow_empty=True)
        if self.source not in SOURCES:
            raise SchemaError(f"source không hợp lệ: {self.source}")
        if self.paragraph is not None:
            _require_int(self.paragraph, "paragraph", 0)
        if self.confidence is not None:
            if not isinstance(self.confidence, (int, float)) or isinstance(
                self.confidence, bool
            ):
                raise SchemaError("confidence phải là số")
            if not 0.0 <= float(self.confidence) <= 1.0:
                raise SchemaError("confidence phải trong khoảng 0..1")

    def to_dict(self) -> dict:
        return {
            "category": self.category,
            "severity": self.severity,
            "message": self.message,
            "suggestion": self.suggestion,
            "span": self.span.to_dict() if self.span else None,
            "source": self.source,
            "paragraph": self.paragraph,
            "confidence": self.confidence,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Issue":
        if not isinstance(data, dict):
            raise SchemaError("issue phải là object")
        span_data = data.get("span")
        span = Span.from_dict(span_data) if span_data is not None else None
        return cls(
            category=_require_str(data.get("category"), "category"),
            severity=_require_str(data.get("severity"), "severity"),
            message=_require_str(data.get("message"), "message"),
            suggestion=_require_str(
                data.get("suggestion", ""), "suggestion", allow_empty=True
            ),
            span=span,
            source=data.get("source", "rule"),
            paragraph=data.get("paragraph"),
            confidence=data.get("confidence"),
        )


@dataclass(frozen=True)
class Paragraph:
    index: int
    text: str
    start: int
    end: int

    def __post_init__(self) -> None:
        _require_int(self.index, "paragraph.index", 0)
        _require_str(self.text, "paragraph.text", allow_empty=True)
        _require_int(self.start, "paragraph.start", 0)
        _require_int(self.end, "paragraph.end", 0)
        if self.end < self.start:
            raise SchemaError("paragraph.end phải >= paragraph.start")


@dataclass(frozen=True)
class Sentence:
    index: int
    text: str
    start: int
    end: int
    paragraph_index: int

    def __post_init__(self) -> None:
        _require_int(self.index, "sentence.index", 0)
        _require_str(self.text, "sentence.text", allow_empty=True)
        _require_int(self.start, "sentence.start", 0)
        _require_int(self.end, "sentence.end", 0)
        _require_int(self.paragraph_index, "sentence.paragraph", 0)
        if self.end < self.start:
            raise SchemaError("sentence.end phải >= sentence.start")


@dataclass
class Document:
    path: str
    title: str
    body: str
    paragraphs: list[Paragraph] = field(default_factory=list)
    front_matter: dict = field(default_factory=dict)
    content_sha256: str = ""

    def __post_init__(self) -> None:
        _require_str(self.path, "document.path", allow_empty=True)
        _require_str(self.title, "document.title", allow_empty=True)
        if not isinstance(self.body, str):
            raise SchemaError("document.body phải là chuỗi")
        if not isinstance(self.front_matter, dict):
            raise SchemaError("front_matter phải là object")
        if not self.content_sha256:
            self.content_sha256 = hashlib.sha256(
                self.body.encode("utf-8")
            ).hexdigest()

    @property
    def word_count(self) -> int:
        import re

        return len(re.findall(r"\w+", self.body, re.UNICODE))

    def to_dict(self) -> dict:
        return {
            "path": self.path,
            "title": self.title,
            "body": self.body,
            "paragraphs": [
                {
                    "index": p.index,
                    "text": p.text,
                    "start": p.start,
                    "end": p.end,
                }
                for p in self.paragraphs
            ],
            "front_matter": self.front_matter,
            "content_sha256": self.content_sha256,
        }


@dataclass
class AnnotationRecord:
    source_path: str
    title: str
    content_sha256: str
    model: str
    issues: list[Issue] = field(default_factory=list)
    id: str = field(default_factory=lambda: uuid.uuid4().hex)
    created_at: str = field(default_factory=now_iso)
    meta: dict = field(default_factory=dict)

    def __post_init__(self) -> None:
        _require_str(self.source_path, "source_path", allow_empty=True)
        _require_str(self.title, "title", allow_empty=True)
        _require_str(self.content_sha256, "content_sha256")
        _require_str(self.model, "model")
        _require_str(self.id, "id")
        _require_str(self.created_at, "created_at")
        if not isinstance(self.meta, dict):
            raise SchemaError("meta phải là object")
        converted: list[Issue] = []
        for item in self.issues:
            converted.append(item if isinstance(item, Issue) else Issue.from_dict(item))
        self.issues = converted

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "source_path": self.source_path,
            "title": self.title,
            "content_sha256": self.content_sha256,
            "model": self.model,
            "created_at": self.created_at,
            "issues": [issue.to_dict() for issue in self.issues],
            "meta": self.meta,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "AnnotationRecord":
        if not isinstance(data, dict):
            raise SchemaError("record phải là object")
        issues = [Issue.from_dict(item) for item in data.get("issues", [])]
        return cls(
            source_path=data.get("source_path", ""),
            title=data.get("title", ""),
            content_sha256=_require_str(data.get("content_sha256"), "content_sha256"),
            model=_require_str(data.get("model"), "model"),
            issues=issues,
            id=data.get("id") or uuid.uuid4().hex,
            created_at=data.get("created_at") or now_iso(),
            meta=data.get("meta", {}),
        )


@dataclass
class DocumentRecord:
    """Bản sao nội dung bài viết, dùng để export SFT mà không phụ thuộc file gốc."""

    content_sha256: str
    title: str
    source_path: str
    body: str
    created_at: str = field(default_factory=now_iso)
    meta: dict = field(default_factory=dict)

    def __post_init__(self) -> None:
        _require_str(self.content_sha256, "content_sha256")
        _require_str(self.title, "title", allow_empty=True)
        _require_str(self.source_path, "source_path", allow_empty=True)
        if not isinstance(self.body, str):
            raise SchemaError("body phải là chuỗi")
        _require_str(self.created_at, "created_at")
        if not isinstance(self.meta, dict):
            raise SchemaError("meta phải là object")

    def to_dict(self) -> dict:
        return {
            "content_sha256": self.content_sha256,
            "title": self.title,
            "source_path": self.source_path,
            "body": self.body,
            "created_at": self.created_at,
            "meta": self.meta,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "DocumentRecord":
        if not isinstance(data, dict):
            raise SchemaError("document phải là object")
        return cls(
            content_sha256=_require_str(data.get("content_sha256"), "content_sha256"),
            title=data.get("title", ""),
            source_path=data.get("source_path", ""),
            body=data.get("body", ""),
            created_at=data.get("created_at") or now_iso(),
            meta=data.get("meta", {}),
        )
