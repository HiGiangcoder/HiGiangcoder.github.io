#!/usr/bin/env python3
"""Annotate một corpus tiếng Việt bằng Ollama teacher, append-only.

Mặc định không gọi mạng. Cần --allow-network để annotate thật.
"""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

from bloglint.config import Settings
from bloglint.dataset import (
    append_documents,
    append_records,
    make_document_record,
    make_record,
    read_records,
)
from bloglint.schema import Document
from bloglint.teacher import NetworkNotAllowed, OllamaTeacher, TeacherError
from bloglint.text import document_from_body


def load_corpus(path: Path) -> list[dict]:
    rows = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                rows.append(json.loads(line))
    return rows


def existing_hashes(annotations_path: Path) -> set[str]:
    return {record.content_sha256 for record in read_records(annotations_path)}


def main() -> int:
    parser = argparse.ArgumentParser(description="Annotate corpus tiếng Việt bằng Ollama")
    parser.add_argument("--corpus", required=True, help="JSONL corpus, field 'text'")
    parser.add_argument("--annotations", default=None)
    parser.add_argument("--documents", default=None)
    parser.add_argument("--limit", type=int, default=5)
    parser.add_argument("--offset", type=int, default=0)
    parser.add_argument("--allow-network", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--retries", type=int, default=2, help="Số lần thử lại khi teacher lỗi")
    parser.add_argument("--sleep", type=float, default=1.0, help="Delay giữa các bài")
    args = parser.parse_args()

    settings = Settings.from_env(None)
    annotations_path = Path(args.annotations).expanduser() if args.annotations else settings.data_dir / "annotations.jsonl"
    documents_path = Path(args.documents).expanduser() if args.documents else settings.data_dir / "documents.jsonl"

    corpus = load_corpus(Path(args.corpus).expanduser())
    selected = corpus[args.offset : args.offset + args.limit]
    print(f"Corpus: {len(corpus)} bài, chọn {len(selected)} bài (offset={args.offset})")

    if args.dry_run:
        for index, row in enumerate(selected, start=1):
            text = row.get("text", "")
            print(f"[{index}] {len(text)} ký tự: {text[:120].replace(chr(10), ' ')}")
        return 0

    if not args.allow_network:
        print("Cần --allow-network để annotate.", file=__import__("sys").stderr)
        return 2

    teacher = OllamaTeacher(
        model=settings.ollama_model,
        base_url=settings.ollama_base_url,
        api_key=settings.ollama_api_key,
        timeout=settings.request_timeout,
        allow_network=True,
    )
    if teacher.chat_url.startswith("https://ollama.com") and not settings.ollama_api_key:
        print("Thiếu API key cho Ollama Cloud.", file=__import__("sys").stderr)
        return 2

    seen = existing_hashes(annotations_path)
    done = 0
    skipped = 0
    failed = 0
    for index, row in enumerate(selected, start=1):
        text = row.get("text", "").strip()
        if len(text) < 200:
            print(f"[{index}] bỏ qua: text quá ngắn")
            skipped += 1
            continue
        title = row.get("title") or f"Bài corpus {args.offset + index}"
        document = document_from_body(text, title=title, path=f"corpus/{args.offset + index}")
        if document.content_sha256 in seen:
            print(f"[{index}] bỏ qua: đã annotate")
            skipped += 1
            continue
        for attempt in range(1, args.retries + 1):
            try:
                result = teacher.annotate(document, allow_network=True)
                break
            except (NetworkNotAllowed, TeacherError) as exc:
                if attempt == args.retries:
                    print(f"[{index}] lỗi teacher sau {attempt} lần: {exc}")
                    failed += 1
                    result = None
                else:
                    print(f"[{index}] thử {attempt} lỗi: {exc}; thử lại...")
                    time.sleep(args.sleep)
        if result is None:
            continue
        record = make_record(
            document,
            result.issues,
            model=result.model,
            meta={"prompt_version": "v1", "source": "teacher", "raw_chars": len(result.raw), "corpus": Path(args.corpus).name},
        )
        doc_record = make_document_record(document)
        append_records(annotations_path, [record])
        append_documents(documents_path, [doc_record])
        seen.add(document.content_sha256)
        done += 1
        print(f"[{index}] OK: {len(result.issues)} issue")
        time.sleep(args.sleep)

    print(f"Hoàn tất: ghi {done}, bỏ qua {skipped}, lỗi {failed}")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
