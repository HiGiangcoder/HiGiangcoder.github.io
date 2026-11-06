from __future__ import annotations

import hashlib
import re
from pathlib import Path

import yaml

from .schema import Document, Paragraph, Sentence

FRONT_MATTER_RE = re.compile(
    r"\A---[ \t]*\r?\n(.*?)\r?\n---[ \t]*(?:\r?\n|\Z)", re.DOTALL
)
SENTENCE_END_RE = re.compile(r"[.!?…]+[\"'”’)]*")


class MarkdownError(ValueError):
    """Không đọc được Markdown/front matter."""


def split_front_matter(text: str) -> tuple[dict, str, int]:
    """Trả về (metadata, body, body_offset).

    Offset luôn tính trong ``body`` để span không bị lệch vì front matter.
    """
    if not text.startswith("---"):
        return {}, text, 0

    match = FRONT_MATTER_RE.match(text)
    if not match:
        return {}, text, 0

    raw_meta = match.group(1)
    try:
        metadata = yaml.safe_load(raw_meta) or {}
    except yaml.YAMLError as exc:  # pragma: no cover - thông báo cụ thể
        raise MarkdownError(f"Front matter YAML không hợp lệ: {exc}") from exc

    if not isinstance(metadata, dict):
        raise MarkdownError("Front matter phải là YAML object")

    return metadata, text[match.end() :], match.end()


def _blank(match: re.Match) -> str:
    """Thay nội dung bằng khoảng trắng nhưng giữ nguyên newline/offset."""
    return re.sub(r"[^\n]", " ", match.group(0))


def mask_code(text: str) -> str:
    """Ẩn code block/inline code/URL để rule không bắt lỗi trong đó."""
    masked = re.sub(r"```.*?```", _blank, text, flags=re.DOTALL)
    masked = re.sub(r"`[^`\n]*`", _blank, masked)
    masked = re.sub(r"<!--.*?-->", _blank, masked, flags=re.DOTALL)
    masked = re.sub(r"https?://\S+", _blank, masked)
    return masked


def split_paragraphs(body: str) -> list[Paragraph]:
    """Chia đoạn theo dòng trống, giữ offset tuyệt đối trong body."""
    paragraphs: list[Paragraph] = []
    lines = body.splitlines(keepends=True)
    offset = 0
    raw_start: int | None = None
    buffer: list[str] = []

    def emit() -> None:
        nonlocal raw_start, buffer
        if raw_start is None:
            return
        raw = "".join(buffer)
        leading = len(raw) - len(raw.lstrip())
        text = raw.strip()
        if text:
            start = raw_start + leading
            paragraphs.append(
                Paragraph(
                    index=len(paragraphs),
                    text=text,
                    start=start,
                    end=start + len(text),
                )
            )
        raw_start = None
        buffer = []

    for line in lines:
        if line.rstrip("\r\n").strip():
            if raw_start is None:
                raw_start = offset
            buffer.append(line)
        else:
            emit()
        offset += len(line)
    emit()
    return paragraphs


def split_sentences(
    text: str, absolute_start: int, paragraph_index: int
) -> list[Sentence]:
    """Chia câu đơn giản theo dấu kết câu, giữ offset tuyệt đối."""
    sentences: list[Sentence] = []
    start = 0

    def emit(end: int) -> None:
        nonlocal start
        segment = text[start:end]
        leading = len(segment) - len(segment.lstrip())
        trailing = len(segment) - len(segment.rstrip())
        clean = segment.strip()
        if clean:
            abs_start = absolute_start + start + leading
            abs_end = absolute_start + end - trailing
            sentences.append(
                Sentence(
                    index=len(sentences),
                    text=clean,
                    start=abs_start,
                    end=abs_end,
                    paragraph_index=paragraph_index,
                )
            )
        start = end

    for match in SENTENCE_END_RE.finditer(text):
        emit(match.end())
    if start < len(text):
        emit(len(text))
    return sentences


def count_words(text: str) -> int:
    return len(re.findall(r"\w+", text, re.UNICODE))


def document_from_body(
    body: str, title: str = "", path: str = "<memory>"
) -> Document:
    paragraphs = split_paragraphs(body)
    return Document(
        path=path,
        title=title,
        body=body,
        paragraphs=paragraphs,
        front_matter={},
        content_sha256=hashlib.sha256(body.encode("utf-8")).hexdigest(),
    )


def load_document(path: str | Path, title: str | None = None) -> Document:
    file_path = Path(path)
    raw = file_path.read_text(encoding="utf-8")
    metadata, body, _ = split_front_matter(raw)
    document_title = str(metadata.get("title") or title or file_path.stem)
    paragraphs = split_paragraphs(body)
    return Document(
        path=str(file_path),
        title=document_title,
        body=body,
        paragraphs=paragraphs,
        front_matter=metadata,
        content_sha256=hashlib.sha256(body.encode("utf-8")).hexdigest(),
    )
