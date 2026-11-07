"""Rule-based diagnostics tiếng Việt.

Toàn bộ rule chạy offline, deterministic và giữ offset ký tự trong ``body``.
Thứ tự issue được sắp xếp cố định để test và so sánh ổn định.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from .schema import Document, Issue, Paragraph, Span
from .text import count_words, document_from_body, mask_code, split_sentences

# Từ đệm / cụm từ làm câu yếu.
FILLER_PHRASES = (
    "thực sự",
    "thật sự",
    "vô cùng",
    "cực kỳ",
    "hết sức",
    "rất là",
    "kiểu như",
    "đại loại là",
    "nói chung là",
    "nhìn chung thì",
    "một cách nào đó",
    "có vẻ như",
    "dường như",
)

# Sáo ngữ thường gặp trong văn viết blog.
CLICHE_PHRASES = (
    "trong thời đại ngày nay",
    "trong xã hội hiện đại",
    "không thể phủ nhận rằng",
    "không ngoa khi nói rằng",
    "ai cũng biết rằng",
    "như chúng ta đã biết",
    "có thể nói rằng",
    "điều này có nghĩa là",
    "ngày nay",
)

STOP_WORDS = frozenset(
    {
        "và",
        "là",
        "của",
        "có",
        "không",
        "những",
        "các",
        "một",
        "được",
        "cho",
        "trong",
        "khi",
        "với",
        "này",
        "đó",
        "thì",
        "mà",
        "để",
        "từ",
        "như",
        "ra",
        "vào",
        "lên",
        "xuống",
        "rồi",
        "vẫn",
        "cũng",
        "sẽ",
        "đã",
        "đang",
        "bị",
        "bởi",
        "vì",
        "nên",
        "nhưng",
        "hoặc",
        "nếu",
        "thế",
        "nó",
        "họ",
        "ta",
        "tôi",
        "bạn",
        "chúng",
        "người",
    }
)

HEADING_RE = re.compile(r"^\s{0,3}#{1,6}\s+\S", re.MULTILINE)
CONSECUTIVE_WORD_RE = re.compile(r"\b(\w+)(?:\s+\1\b)+", re.IGNORECASE | re.UNICODE)
WORD_RE = re.compile(r"\w+", re.UNICODE)
SPACE_BEFORE_PUNCT_RE = re.compile(r"[ \t]+[,.;:!?]")
MISSING_SPACE_AFTER_PUNCT_RE = re.compile(r"[.,;:!?](?=[^\s\d.,;:!?])")
REPEATED_PUNCT_RE = re.compile(r"([!?])\1{2,}")


# Tham chiếu ngắn gọn tới các nguyên tắc viết phổ biến; không phải trích dẫn học thuật.
RULE_REFERENCES = {
    "sentence_too_long": "Plain Language: giữ câu ngắn, rõ ý",
    "paragraph_too_long": "Web writing: chia đoạn theo ý chính",
    "filler_word": "Style guide: tránh từ đệm làm yếu câu",
    "cliche": "Style guide: tránh sáo ngữ chung chung",
    "repetition": "Style guide: tránh lặp từ không cần thiết",
    "punctuation": "Quy tắc chính tả tiếng Việt: khoảng trắng và dấu câu",
    "passive_overuse": "Style guide: ưu tiên câu chủ động",
    "structure": "Web content: dùng heading cho bài dài",
}


@dataclass(frozen=True)
class DiagnosticsConfig:
    max_sentence_words: int = 40
    max_paragraph_words: int = 220
    long_document_words: int = 600
    repetition_min_count: int = 4
    passive_min_count: int = 3
    passive_min_paragraph_words: int = 50


def _span(body: str, start: int, end: int) -> Span:
    return Span(start=start, end=end, text=body[start:end])


def _phrase_matches(masked: str) -> list[tuple[int, int, str, str]]:
    """Tìm cụm từ, ưu tiên cụm dài và bỏ qua cụm chồng lấn."""
    phrases: list[tuple[str, str]] = [
        *((phrase, "filler_word") for phrase in FILLER_PHRASES),
        *((phrase, "cliche") for phrase in CLICHE_PHRASES),
    ]
    phrases.sort(key=lambda item: len(item[0]), reverse=True)

    found: list[tuple[int, int, str, str]] = []
    for phrase, category in phrases:
        pattern = re.compile(
            r"(?<!\w)" + re.escape(phrase) + r"(?!\w)", re.IGNORECASE | re.UNICODE
        )
        for match in pattern.finditer(masked):
            if any(match.start() < end and start < match.end() for start, end, _, _ in found):
                continue
            found.append((match.start(), match.end(), category, phrase))
    return found


def _check_sentences(
    body: str, masked: str, paragraph: Paragraph, config: DiagnosticsConfig
) -> list[Issue]:
    issues: list[Issue] = []
    masked_paragraph = masked[paragraph.start : paragraph.end]
    for sentence in split_sentences(masked_paragraph, paragraph.start, paragraph.index):
        words = count_words(sentence.text)
        if words <= config.max_sentence_words:
            continue
        issues.append(
            Issue(
                category="sentence_too_long",
                severity="warning",
                message=(
                    f"Câu dài {words} từ (ngưỡng {config.max_sentence_words}). "
                    "Nên tách thành 2–3 câu ngắn hơn."
                ),
                suggestion="Tách câu tại các ý phụ hoặc thay dấu phẩy bằng dấu chấm.",
                span=_span(body, sentence.start, sentence.end),
                paragraph=paragraph.index,
                reference=RULE_REFERENCES["sentence_too_long"],
            )
        )
    return issues


def _check_paragraph(
    body: str, masked_paragraph: str, paragraph: Paragraph, config: DiagnosticsConfig
) -> list[Issue]:
    issues: list[Issue] = []
    words = count_words(masked_paragraph)
    if words > config.max_paragraph_words:
        issues.append(
            Issue(
                category="paragraph_too_long",
                severity="warning",
                message=(
                    f"Đoạn dài {words} từ (ngưỡng {config.max_paragraph_words}). "
                    "Nên chia thành các đoạn nhỏ hơn."
                ),
                suggestion="Tách đoạn theo từng ý chính, mỗi đoạn 3–6 câu.",
                span=_span(body, paragraph.start, paragraph.end),
                paragraph=paragraph.index,
                reference=RULE_REFERENCES["paragraph_too_long"],
            )
        )

    if words >= config.passive_min_paragraph_words:
        passive_count = sum(
            1 for match in WORD_RE.finditer(masked_paragraph) if match.group(0).lower() == "bị"
        )
        if passive_count >= config.passive_min_count:
            issues.append(
                Issue(
                    category="passive_overuse",
                    severity="info",
                    message=(
                        f"Đoạn dùng “bị” {passive_count} lần. "
                        "Có thể chuyển sang câu chủ động để rõ ý hơn."
                    ),
                    suggestion="Xem lại các câu bị động và chọn cách diễn đạt chủ động.",
                    span=_span(body, paragraph.start, paragraph.end),
                    paragraph=paragraph.index,
                    reference=RULE_REFERENCES["passive_overuse"],
                )
            )

    seen_words: dict[str, list[re.Match]] = {}
    for match in WORD_RE.finditer(masked_paragraph):
        word = match.group(0).lower()
        if len(word) < 2 or word in STOP_WORDS:
            continue
        seen_words.setdefault(word, []).append(match)

    for word, matches in sorted(seen_words.items()):
        if len(matches) < config.repetition_min_count:
            continue
        first = matches[0]
        issues.append(
            Issue(
                category="repetition",
                severity="info",
                message=(
                    f"Từ “{word}” lặp {len(matches)} lần trong một đoạn. "
                    "Nên thay bằng từ đồng nghĩa hoặc đại từ."
                ),
                suggestion="Kiểm tra xem việc lặp từ có phải là dụng ý tu từ không.",
                span=_span(
                    body,
                    paragraph.start + first.start(),
                    paragraph.start + first.end(),
                ),
                paragraph=paragraph.index,
                reference=RULE_REFERENCES["repetition"],
            )
        )

    for match in CONSECUTIVE_WORD_RE.finditer(masked_paragraph):
        issues.append(
            Issue(
                category="repetition",
                severity="warning",
                message=f"Cụm từ bị lặp liền nhau: “{match.group(0)}”.",
                suggestion="Bỏ một lần lặp nếu không phải dụng ý nhấn mạnh.",
                span=_span(
                    body,
                    paragraph.start + match.start(),
                    paragraph.start + match.end(),
                ),
                paragraph=paragraph.index,
                reference=RULE_REFERENCES["repetition"],
            )
        )
    return issues


def _check_punctuation(body: str, masked: str) -> list[Issue]:
    issues: list[Issue] = []
    for match in SPACE_BEFORE_PUNCT_RE.finditer(masked):
        issues.append(
            Issue(
                category="punctuation",
                severity="warning",
                message="Có khoảng trắng trước dấu câu.",
                suggestion="Bỏ khoảng trắng trước dấu câu.",
                span=_span(body, match.start(), match.end()),
                reference=RULE_REFERENCES["punctuation"],
            )
        )
    for match in MISSING_SPACE_AFTER_PUNCT_RE.finditer(masked):
        issues.append(
            Issue(
                category="punctuation",
                severity="warning",
                message="Thiếu khoảng trắng sau dấu câu.",
                suggestion="Thêm một khoảng trắng sau dấu câu.",
                span=_span(body, match.start(), match.end()),
                reference=RULE_REFERENCES["punctuation"],
            )
        )
    for match in REPEATED_PUNCT_RE.finditer(masked):
        issues.append(
            Issue(
                category="punctuation",
                severity="info",
                message="Dấu câu được lặp quá nhiều lần.",
                suggestion="Giữ tối đa một dấu chấm than hoặc dấu hỏi.",
                span=_span(body, match.start(), match.end()),
                reference=RULE_REFERENCES["punctuation"],
            )
        )
    return issues


def _check_structure(body: str, total_words: int, config: DiagnosticsConfig) -> list[Issue]:
    if total_words < config.long_document_words:
        return []
    if HEADING_RE.search(body):
        return []
    return [
        Issue(
            category="structure",
            severity="info",
            message=(
                f"Bài dài khoảng {total_words} từ nhưng chưa có tiêu đề mục. "
                "Nên thêm heading để người đọc dễ theo dõi."
            ),
            suggestion="Thêm các mục ## cho từng phần chính của bài.",
            reference=RULE_REFERENCES["structure"],
        )
    ]


def _sort_key(issue: Issue) -> tuple:
    if issue.span is None:
        return (10**12, 10**12, issue.category, issue.message)
    return (issue.span.start, issue.span.end, issue.category, issue.message)


def analyze_document(
    document: Document, config: DiagnosticsConfig | None = None
) -> list[Issue]:
    """Chạy toàn bộ rule trên một ``Document``."""
    config = config or DiagnosticsConfig()
    body = document.body
    masked = mask_code(body)
    # mask_code thay ký tự bằng khoảng trắng nên độ dài phải giữ nguyên.
    if len(masked) != len(body):  # pragma: no cover - bất biến nội bộ
        raise AssertionError("mask_code làm thay đổi độ dài văn bản")

    issues: list[Issue] = []
    for paragraph in document.paragraphs:
        masked_paragraph = masked[paragraph.start : paragraph.end]
        issues.extend(_check_sentences(body, masked, paragraph, config))
        issues.extend(_check_paragraph(body, masked_paragraph, paragraph, config))

    for start, end, category, phrase in _phrase_matches(masked):
        if category == "filler_word":
            message = f"Cụm từ đệm “{phrase}” làm câu thiếu tự nhiên."
            suggestion = "Cân nhắc bỏ cụm từ này nếu không cần thiết."
        else:
            message = f"Cụm từ sáo ngữ “{phrase}”."
            suggestion = "Thay bằng cách diễn đạt cụ thể, gắn với nội dung bài."
        issues.append(
            Issue(
                category=category,
                severity="info",
                message=message,
                suggestion=suggestion,
                span=_span(body, start, end),
                reference=RULE_REFERENCES[category],
            )
        )

    issues.extend(_check_punctuation(body, masked))
    issues.extend(_check_structure(body, count_words(masked), config))

    deduped: dict[tuple, Issue] = {}
    for issue in issues:
        span = issue.span
        key = (
            issue.category,
            issue.severity,
            issue.message,
            span.start if span else None,
            span.end if span else None,
        )
        deduped.setdefault(key, issue)

    return sorted(deduped.values(), key=_sort_key)


def analyze_body(
    body: str, title: str = "", config: DiagnosticsConfig | None = None
) -> list[Issue]:
    """Tiện dụng cho admin: phân tích trực tiếp Markdown body."""
    return analyze_document(document_from_body(body, title=title), config=config)


def summarize(issues: list[Issue]) -> dict:
    counts = {"error": 0, "warning": 0, "info": 0}
    categories: dict[str, int] = {}
    for issue in issues:
        counts[issue.severity] = counts.get(issue.severity, 0) + 1
        categories[issue.category] = categories.get(issue.category, 0) + 1
    return {
        "total": len(issues),
        "by_severity": counts,
        "by_category": dict(sorted(categories.items())),
    }
