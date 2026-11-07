#!/usr/bin/env python3
"""Review issue bằng Ollama cloud, append-only.

Mặc định không gọi mạng. Cần --allow-network để review thật.
"""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

from bloglint.config import Settings
from bloglint.dataset import read_documents, read_records
from bloglint.schema import now_iso
from bloglint.teacher import NetworkNotAllowed, OllamaTeacher, TeacherError, _http_post_json


def load_done(path: Path) -> set[tuple[str, int]]:
    done: set[tuple[str, int]] = set()
    if not path.exists():
        return done
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            if not line.strip():
                continue
            try:
                payload = json.loads(line)
            except json.JSONDecodeError:
                continue
            done.add((payload.get("content_sha256", ""), payload.get("issue_index", -1)))
    return done


def build_prompt(document_body: str, issue: dict) -> str:
    return (
        "Bạn là reviewer chất lượng cho các issue chẩn đoán bài viết tiếng Việt.\n"
        "Hãy quyết định issue có đúng và hữu ích không.\n\n"
        "Trả về DUY NHẤT một JSON object:\n"
        "{\n"
        '  "decision": "keep" | "reject" | "modify",\n'
        '  "reason": "lý do ngắn",\n'
        '  "message": "message đã chỉnh (nếu modify, ngược lại null)",\n'
        '  "suggestion": "suggestion đã chỉnh (nếu modify, ngược lại null)",\n'
        '  "reference": "tên tài liệu/quy tắc ngắn hoặc null"\n'
        "}\n\n"
        "Quy tắc:\n"
        "- reject nếu quote không xuất hiện, issue bịa, hoặc không ảnh hưởng chất lượng.\n"
        "- modify nếu issue đúng nhưng message/suggestion chưa tốt.\n"
        "- keep nếu issue đúng và rõ ràng.\n"
        "- reference chỉ điền nếu có căn cứ; không bịa.\n"
        "- Không thêm chữ nào ngoài JSON.\n\n"
        "Bài viết:\n-----\n"
        f"{document_body}\n-----\n\n"
        "Issue cần review:\n"
        f"{json.dumps(issue, ensure_ascii=False)}\n"
    )


def parse_decision(raw: str) -> dict:
    cleaned = raw.strip()
    start = cleaned.find("{")
    end = cleaned.rfind("}")
    if start == -1 or end == -1 or end <= start:
        raise ValueError("Không tìm thấy JSON.")
    payload = json.loads(cleaned[start : end + 1])
    if not isinstance(payload, dict):
        raise ValueError("JSON phải là object.")
    decision = payload.get("decision")
    if decision not in {"keep", "reject", "modify"}:
        raise ValueError(f"decision không hợp lệ: {decision!r}")
    return payload


def main() -> int:
    parser = argparse.ArgumentParser(description="Review issue bằng Ollama cloud")
    parser.add_argument("--annotations", default=None)
    parser.add_argument("--documents", default=None)
    parser.add_argument("--output", default=None)
    parser.add_argument("--limit", type=int, default=20)
    parser.add_argument("--offset", type=int, default=0)
    parser.add_argument("--allow-network", action="store_true")
    parser.add_argument("--model", default=None)
    parser.add_argument("--sleep", type=float, default=1.0)
    args = parser.parse_args()

    settings = Settings.from_env(None)
    annotations_path = Path(args.annotations).expanduser() if args.annotations else settings.data_dir / "annotations.jsonl"
    documents_path = Path(args.documents).expanduser() if args.documents else settings.data_dir / "documents.jsonl"
    output_path = Path(args.output).expanduser() if args.output else settings.data_dir / "review_decisions.jsonl"

    if not args.allow_network:
        print("Cần --allow-network để review.", file=__import__("sys").stderr)
        return 2

    model = args.model or settings.ollama_model
    teacher = OllamaTeacher(
        model=model,
        base_url=settings.ollama_base_url,
        api_key=settings.ollama_api_key,
        timeout=settings.request_timeout,
        allow_network=True,
    )
    if teacher.chat_url.startswith("https://ollama.com") and not settings.ollama_api_key:
        print("Thiếu API key cho Ollama Cloud.", file=__import__("sys").stderr)
        return 2

    documents = {doc.content_sha256: doc for doc in read_documents(documents_path)}
    records = read_records(annotations_path)
    done = load_done(output_path)

    selected_issues: list[tuple] = []
    for record in records:
        for index, issue in enumerate(record.issues):
            selected_issues.append((record, index, issue))
    selected_issues = selected_issues[args.offset : args.offset + args.limit]

    output_path.parent.mkdir(parents=True, exist_ok=True)
    written = 0
    failed = 0
    for position, (record, index, issue) in enumerate(selected_issues, start=1):
        key = (record.content_sha256, index)
        if key in done:
            print(f"[{position}] bỏ qua: đã review")
            continue
        document = documents.get(record.content_sha256)
        if document is None:
            print(f"[{position}] bỏ qua: thiếu document")
            continue
        issue_payload = {
            "category": issue.category,
            "severity": issue.severity,
            "message": issue.message,
            "suggestion": issue.suggestion,
            "quote": issue.span.text if issue.span else None,
        }
        prompt = build_prompt(document.body, issue_payload)
        payload = {
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "stream": False,
            "format": "json",
            "options": {"temperature": 0},
        }
        try:
            if teacher.transport is None:
                response = _http_post_json(
                    teacher.chat_url, payload, teacher._headers(), timeout=teacher.timeout
                )
            else:
                response = teacher.transport(teacher.chat_url, payload, teacher._headers())
            if isinstance(response, dict) and isinstance(response.get("message"), dict):
                raw = response["message"].get("content", "")
            else:
                raw = response.get("response", "") if isinstance(response, dict) else ""
            decision = parse_decision(raw)
        except (TeacherError, ValueError, Exception) as exc:
            print(f"[{position}] lỗi review: {exc}")
            failed += 1
            time.sleep(args.sleep)
            continue

        record_out = {
            "content_sha256": record.content_sha256,
            "source_path": record.source_path,
            "issue_index": index,
            "original": issue_payload,
            "decision": decision.get("decision"),
            "reason": decision.get("reason", ""),
            "reviewed_message": decision.get("message"),
            "reviewed_suggestion": decision.get("suggestion"),
            "reference": decision.get("reference"),
            "model": model,
            "created_at": now_iso(),
        }
        with output_path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(record_out, ensure_ascii=False) + "\n")
        done.add(key)
        written += 1
        print(f"[{position}] {decision.get('decision')}: {issue.category}")
        time.sleep(args.sleep)

    print(f"Hoàn tất: ghi {written}, lỗi {failed}")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())