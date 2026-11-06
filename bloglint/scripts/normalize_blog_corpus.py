#!/usr/bin/env python3
"""Chuẩn hoá Blog Authorship Corpus (barilan) thành JSONL.

Nguồn: https://huggingface.co/datasets/barilan/blog_authorship_corpus
Dữ liệu là các file XML trong thư mục blogs/. Mỗi post có ngày tháng.
Script chỉ đọc file đã tải về, không gọi mạng.
"""

from __future__ import annotations

import argparse
import json
import re
import xml.etree.ElementTree as ET
from pathlib import Path

MONTHS = {
    "jan": 1, "feb": 2, "mar": 3, "apr": 4, "may": 5, "jun": 6,
    "jul": 7, "aug": 8, "sep": 9, "oct": 10, "nov": 11, "dec": 12,
}


def parse_date(value: str) -> str | None:
    parts = [part.strip() for part in value.split(",")]
    if len(parts) != 3:
        return None
    day, month, year = parts
    month_num = MONTHS.get(month.lower()[:3])
    if month_num is None:
        return None
    try:
        return f"{int(year):04d}-{month_num:02d}-{int(day):02d}"
    except ValueError:
        return None


def clean_text(value: str) -> str:
    value = re.sub(r"\s+", " ", value).strip()
    return value


def parse_file(path: Path, max_posts_per_author: int | None = None) -> list[dict]:
    try:
        root = ET.parse(path).getroot()
    except ET.ParseError:
        return []

    stem = path.stem
    fields = stem.split(".")
    author_id = fields[0] if fields else path.stem
    gender = fields[1] if len(fields) > 1 else ""
    age = fields[2] if len(fields) > 2 else ""
    topic = fields[3] if len(fields) > 3 else ""
    sign = fields[4] if len(fields) > 4 else ""

    posts: list[dict] = []
    for post in root.findall(".//post"):
        date_node = post.find("../date")
        # In this corpus, <date> is sibling before <post>, not parent; fallback below.
        date_text = ""
        previous = None
        # ElementTree has no previous sibling easily; search all dates by order.
        text = clean_text("".join(post.itertext()))
        if len(text) < 80:
            continue
        posts.append(
            {
                "author_id": author_id,
                "gender": gender,
                "age": age,
                "topic": topic,
                "zodiac": sign,
                "date": None,
                "text": text,
                "source": "barilan/blog_authorship_corpus",
            }
        )

    # Dates are siblings in XML; pair them by order.
    dates = [clean_text(node.text or "") for node in root.findall(".//date")]
    date_index = 0
    paired_posts = []
    for post in root.findall(".//post"):
        text = clean_text("".join(post.itertext()))
        if len(text) < 80:
            continue
        date_value = dates[date_index] if date_index < len(dates) else ""
        date_index += 1
        paired_posts.append((date_value, text))

    result = []
    for date_value, text in paired_posts:
        if max_posts_per_author is not None and len(result) >= max_posts_per_author:
            break
        result.append(
            {
                "author_id": author_id,
                "gender": gender,
                "age": age,
                "topic": topic,
                "zodiac": sign,
                "date": parse_date(date_value),
                "date_raw": date_value,
                "text": text,
                "source": "barilan/blog_authorship_corpus",
            }
        )
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-dir", required=True, help="Thư mục extracted/blogs")
    parser.add_argument("--output", required=True, help="File JSONL đầu ra")
    parser.add_argument("--limit", type=int, default=5000, help="Số post tối đa")
    parser.add_argument("--max-per-author", type=int, default=3, help="Số post tối đa mỗi tác giả")
    parser.add_argument("--cutoff-year", type=int, default=2022, help="Chỉ giữ post có năm <= cutoff")
    args = parser.parse_args()

    input_dir = Path(args.input_dir)
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    files = sorted(input_dir.glob("*.xml"))
    written = 0
    skipped_date = 0
    with output_path.open("w", encoding="utf-8") as handle:
        for path in files:
            if written >= args.limit:
                break
            for post in parse_file(path, max_posts_per_author=args.max_per_author):
                if written >= args.limit:
                    break
                date = post["date"]
                if date is not None and int(date[:4]) > args.cutoff_year:
                    skipped_date += 1
                    continue
                handle.write(json.dumps(post, ensure_ascii=False) + "\n")
                written += 1

    print(f"Đã ghi {written} post vào {output_path}")
    print(f"Bỏ qua vì sau năm {args.cutoff_year}: {skipped_date}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
