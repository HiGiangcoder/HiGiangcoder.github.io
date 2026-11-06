"""Teacher client cho Ollama (local hoặc cloud).

Nguyên tắc an toàn:

- Không gọi mạng trừ khi caller truyền ``allow_network=True``.
- Transport có thể inject để test, không cần mạng thật.
- Không log hay trả lại API key.
"""

from __future__ import annotations

import difflib
import json
import re
import unicodedata
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from typing import Callable

from .schema import CATEGORIES, SEVERITIES, Document, Issue, SchemaError, Span

DEFAULT_FORMAT_INSTRUCTION = """Bạn là biên tập viên tiếng Việt. Hãy đọc bài viết và chỉ ra các vấn đề
thực sự ảnh hưởng tới chất lượng. Không khen, không viết lại toàn bài.

Trả về DUY NHẤT một JSON object theo cấu trúc:

{
  "issues": [
    {
      "category": "clarity | coherence | grammar | spelling | style | factual | punctuation | other",
      "severity": "info | warning | error",
      "message": "mô tả ngắn gọn bằng tiếng Việt",
      "suggestion": "gợi ý sửa cụ thể",
      "quote": "trích nguyên văn một đoạn ngắn trong bài"
    }
  ]
}

Quy tắc:
- Mỗi issue phải có ``quote`` xuất hiện nguyên văn trong bài.
- Không bịa lỗi. Nếu bài không có vấn đề đáng kể, trả ``{"issues": []}``.
- Tối đa 20 issue, ưu tiên vấn đề rõ ràng nhất.
- Không thêm chữ nào ngoài JSON."""


class TeacherError(RuntimeError):
    """Lỗi chung của teacher."""


class NetworkNotAllowed(TeacherError):
    """Chưa được phép gọi mạng."""


class TeacherResponseError(TeacherError):
    """Response của teacher không đúng định dạng."""


@dataclass
class TeacherResult:
    issues: list[Issue]
    raw: str
    prompt: str
    model: str
    meta: dict = field(default_factory=dict)


def build_prompt(document: Document) -> str:
    return (
        f"{DEFAULT_FORMAT_INSTRUCTION}\n\n"
        f"Tiêu đề: {document.title or '(không có)'}\n"
        f"Độ dài: {document.word_count} từ\n"
        "----- BẮT ĐẦU BÀI -----\n"
        f"{document.body}\n"
        "----- KẾT THÚC BÀI -----"
    )


def extract_json(text: str) -> dict:
    """Bóc JSON khỏi response, chấp nhận code fence hoặc lời dẫn thừa."""
    if not isinstance(text, str) or not text.strip():
        raise TeacherResponseError("Teacher trả về nội dung rỗng.")

    cleaned = text.strip()
    fence = re.search(r"```(?:json)?\s*(.*?)```", cleaned, re.DOTALL | re.IGNORECASE)
    if fence:
        cleaned = fence.group(1).strip()

    try:
        payload = json.loads(cleaned)
    except json.JSONDecodeError:
        start = cleaned.find("{")
        end = cleaned.rfind("}")
        if start == -1 or end == -1 or end <= start:
            raise TeacherResponseError("Không tìm thấy JSON trong response.")
        try:
            payload = json.loads(cleaned[start : end + 1])
        except json.JSONDecodeError as exc:
            raise TeacherResponseError(f"JSON không hợp lệ: {exc}") from exc

    if isinstance(payload, list):
        payload = {"issues": payload}
    if not isinstance(payload, dict) or not isinstance(payload.get("issues"), list):
        raise TeacherResponseError("JSON phải có object với mảng 'issues'.")
    return payload


def _normalize_with_map(text: str) -> tuple[str, list[int]]:
    """Gộp mọi khoảng trắng thành một space và giữ map về vị trí gốc."""
    chars: list[str] = []
    mapping: list[int] = []
    in_whitespace = False
    for index, char in enumerate(text):
        if char.isspace():
            if not in_whitespace and chars:
                chars.append(" ")
                mapping.append(index)
            in_whitespace = True
        else:
            chars.append(char)
            mapping.append(index)
            in_whitespace = False
    while chars and chars[-1] == " ":
        chars.pop()
        mapping.pop()
    return "".join(chars), mapping


def _normalize_alnum_with_map(text: str) -> tuple[str, list[int]]:
    """Bỏ markdown/dấu câu/khác biệt hoa thường, giữ map về vị trí gốc.

    Dùng làm lớp fallback cuối: teacher thường bỏ ``**``, đổi dấu câu hoặc
    viết hoa chữ đầu câu trong quote.
    """
    normalized = unicodedata.normalize("NFC", text)
    if len(normalized) != len(text):  # pragma: no cover - hiếm với tiếng Việt
        normalized = text

    chars: list[str] = []
    mapping: list[int] = []
    pending_space = False
    for index, char in enumerate(normalized):
        if char.isalnum():
            if pending_space and chars:
                chars.append(" ")
                mapping.append(index)
            pending_space = False
            chars.append(char.lower())
            mapping.append(index)
        else:
            pending_space = bool(chars)
    return "".join(chars), mapping


def _find_quote_span(body: str, quote: str) -> Span | None:
    """Tìm quote chính xác, sau đó thử các lớp chuẩn hoá tăng dần."""
    position = body.find(quote)
    if position != -1:
        return Span(start=position, end=position + len(quote), text=quote)

    # Lớp 1: gộp khoảng trắng (Markdown xuống dòng giữa câu).
    normalized_body, mapping = _normalize_with_map(body)
    normalized_quote, _ = _normalize_with_map(quote)
    if normalized_quote:
        position = normalized_body.find(normalized_quote)
        if position != -1:
            start = mapping[position]
            end = mapping[position + len(normalized_quote) - 1] + 1
            return Span(start=start, end=end, text=body[start:end])

    # Lớp 2: bỏ markdown, dấu câu, khác biệt hoa thường.
    alnum_body, alnum_mapping = _normalize_alnum_with_map(body)
    alnum_quote, _ = _normalize_alnum_with_map(quote)
    if not alnum_quote:
        return None
    position = alnum_body.find(alnum_quote)
    if position != -1:
        start = alnum_mapping[position]
        end = alnum_mapping[position + len(alnum_quote) - 1] + 1
        return Span(start=start, end=end, text=body[start:end])

    # Lớp 3: quote gần đúng nhưng teacher đổi một từ ở đầu/cuối câu.
    # Chỉ chấp nhận khi phần khớp dài và chiếm phần lớn quote.
    if len(alnum_quote) < 30:
        return None
    match = difflib.SequenceMatcher(
        None, alnum_body, alnum_quote, autojunk=False
    ).find_longest_match(0, len(alnum_body), 0, len(alnum_quote))
    if match.size < 30 or match.size / len(alnum_quote) < 0.85:
        return None
    start = alnum_mapping[match.a]
    end = alnum_mapping[match.a + match.size - 1] + 1
    return Span(start=start, end=end, text=body[start:end])


def issues_from_payload(payload: dict, body: str) -> list[Issue]:
    issues: list[Issue] = []
    for index, item in enumerate(payload.get("issues", [])):
        if not isinstance(item, dict):
            raise TeacherResponseError(f"issues[{index}] phải là object.")

        category = str(item.get("category", "")).strip()
        severity = str(item.get("severity", "")).strip()
        if category not in CATEGORIES:
            raise TeacherResponseError(f"issues[{index}] có category không hợp lệ: {category!r}")
        if severity not in SEVERITIES:
            raise TeacherResponseError(f"issues[{index}] có severity không hợp lệ: {severity!r}")

        message = str(item.get("message", "")).strip()
        if not message:
            raise TeacherResponseError(f"issues[{index}] thiếu message.")

        quote = str(item.get("quote", "")).strip()
        span = None
        if quote:
            span = _find_quote_span(body, quote)
            if span is None:
                raise TeacherResponseError(
                    f"issues[{index}] có quote không xuất hiện trong bài: {quote[:60]!r}"
                )

        try:
            issues.append(
                Issue(
                    category=category,
                    severity=severity,
                    message=message,
                    suggestion=str(item.get("suggestion", "")).strip(),
                    span=span,
                    source="teacher",
                    confidence=item.get("confidence"),
                )
            )
        except SchemaError as exc:
            raise TeacherResponseError(f"issues[{index}]: {exc}") from exc
    return issues


def _http_post_json(
    url: str, payload: dict, headers: dict[str, str], timeout: float = 120.0
) -> dict:
    data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    request = urllib.request.Request(
        url,
        data=data,
        headers={"Content-Type": "application/json", **headers},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            raw = response.read().decode("utf-8")
    except urllib.error.HTTPError as exc:
        detail = ""
        try:
            detail = exc.read().decode("utf-8")[:300]
        except Exception:  # pragma: no cover - chỉ để báo lỗi
            pass
        raise TeacherError(f"Ollama trả về HTTP {exc.code}: {detail}") from exc
    except urllib.error.URLError as exc:
        raise TeacherError(f"Không kết nối được Ollama: {exc.reason}") from exc

    try:
        return json.loads(raw)
    except json.JSONDecodeError as exc:
        raise TeacherResponseError("Ollama trả về JSON không hợp lệ.") from exc


Transport = Callable[[str, dict, dict[str, str]], dict]


@dataclass
class OllamaTeacher:
    model: str
    base_url: str
    api_key: str | None = None
    timeout: float = 120.0
    allow_network: bool = False
    transport: Transport | None = None

    @property
    def chat_url(self) -> str:
        return f"{self.base_url.rstrip('/')}/api/chat"

    def _headers(self) -> dict[str, str]:
        if self.api_key:
            return {"Authorization": f"Bearer {self.api_key}"}
        return {}

    def annotate(
        self, document: Document, allow_network: bool | None = None
    ) -> TeacherResult:
        permitted = self.allow_network if allow_network is None else allow_network
        if not permitted:
            raise NetworkNotAllowed(
                "Gọi teacher cần --allow-network (hoặc allow_network=True)."
            )

        prompt = build_prompt(document)
        payload = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "stream": False,
            "format": "json",
            "options": {"temperature": 0},
        }

        if self.transport is None:
            response = _http_post_json(
                self.chat_url, payload, self._headers(), timeout=self.timeout
            )
        else:
            response = self.transport(self.chat_url, payload, self._headers())

        if not isinstance(response, dict):
            raise TeacherResponseError("Response của Ollama phải là object.")
        message = response.get("message")
        if isinstance(message, dict):
            raw = message.get("content", "")
        else:
            raw = response.get("response", "")
        if not isinstance(raw, str):
            raise TeacherResponseError("Response của Ollama thiếu nội dung text.")

        payload_json = extract_json(raw)
        issues = issues_from_payload(payload_json, document.body)
        return TeacherResult(
            issues=issues,
            raw=raw,
            prompt=prompt,
            model=self.model,
            meta={"done": response.get("done"), "base_url": self.base_url},
        )
