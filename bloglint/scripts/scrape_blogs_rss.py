#!/usr/bin/env python3
"""Cào blog từ RSS feed, chỉ giữ bài xuất bản trước cutoff (mặc định 2022-12-31).

Mục đích: tránh nội dung sinh bởi AI (chủ yếu sau 2022) và tôn trọng nguồn công khai.
Script chỉ đọc RSS, không đăng nhập, không bypass paywall, có rate limit.
"""

from __future__ import annotations

import argparse
import json
import re
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

import feedparser
from bs4 import BeautifulSoup

DEFAULT_CUTOFF = "2022-12-31"


def parse_date(value: str | None) -> datetime | None:
    if not value:
        return None
    for fmt in (
        "%a, %d %b %Y %H:%M:%S %z",
        "%a, %d %b %Y %H:%M:%S %Z",
        "%Y-%m-%dT%H:%M:%S%z",
        "%Y-%m-%dT%H:%M:%SZ",
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d",
    ):
        try:
            parsed = datetime.strptime(value.strip(), fmt)
            if parsed.tzinfo is None:
                parsed = parsed.replace(tzinfo=timezone.utc)
            return parsed
        except ValueError:
            continue
    try:
        import email.utils

        parsed_tuple = email.utils.parsedate_to_datetime(value)
        if parsed_tuple.tzinfo is None:
            parsed_tuple = parsed_tuple.replace(tzinfo=timezone.utc)
        return parsed_tuple
    except (TypeError, ValueError, OverflowError):
        return None


def clean_html(value: str | None) -> str:
    if not value:
        return ""
    soup = BeautifulSoup(value, "html.parser")
    for tag in soup(["script", "style"]):
        tag.decompose()
    return re.sub(r"\s+", " ", soup.get_text(" ")).strip()


def extract_entry(entry, cutoff: datetime) -> dict | None:
    published = (
        entry.get("published")
        or entry.get("updated")
        or entry.get("created")
    )
    published_dt = parse_date(published)
    if published_dt is None:
        return None
    if published_dt > cutoff:
        return None

    content = ""
    if entry.get("content"):
        content = entry["content"][0].get("value", "")
    elif entry.get("summary"):
        content = entry["summary"]
    elif entry.get("description"):
        content = entry["description"]

    title = clean_html(entry.get("title", ""))
    text = clean_html(content)
    if len(text) < 120:
        return None

    return {
        "title": title,
        "link": entry.get("link", ""),
        "author": entry.get("author", ""),
        "published": published_dt.isoformat(),
        "text": text,
        "source_feed": entry.get("feed_url", ""),
        "source": "rss",
    }


def crawl_feed(feed_url: str, cutoff: datetime, delay: float) -> list[dict]:
    parsed = feedparser.parse(feed_url)
    if parsed.bozo and not parsed.entries:
        print(f"[WARN] Không parse được feed: {feed_url} ({parsed.bozo_exception})")
        return []
    results = []
    for entry in parsed.entries:
        entry["feed_url"] = feed_url
        row = extract_entry(entry, cutoff)
        if row is not None:
            results.append(row)
    time.sleep(delay)
    return results


def main() -> int:
    parser = argparse.ArgumentParser(description="Cào blog qua RSS, lọc bài trước cutoff")
    parser.add_argument("--feeds", required=True, help="File chứa danh sách RSS URL, mỗi dòng một URL")
    parser.add_argument("--output", required=True, help="File JSONL đầu ra")
    parser.add_argument("--cutoff", default=DEFAULT_CUTOFF, help="Ngày cutoff YYYY-MM-DD")
    parser.add_argument("--delay", type=float, default=1.0, help="Delay giữa các feed (giây)")
    parser.add_argument("--max-posts", type=int, default=1000, help="Số post tối đa")
    args = parser.parse_args()

    cutoff = datetime.fromisoformat(args.cutoff).replace(tzinfo=timezone.utc)
    feed_urls = [
        line.strip()
        for line in Path(args.feeds).read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.strip().startswith("#")
    ]

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    seen_links: set[str] = set()
    written = 0
    with output_path.open("w", encoding="utf-8") as handle:
        for feed_url in feed_urls:
            if written >= args.max_posts:
                break
            print(f"Đang cào: {feed_url}")
            for row in crawl_feed(feed_url, cutoff, args.delay):
                if written >= args.max_posts:
                    break
                if row["link"] and row["link"] in seen_links:
                    continue
                if row["link"]:
                    seen_links.add(row["link"])
                handle.write(json.dumps(row, ensure_ascii=False) + "\n")
                handle.flush()
                written += 1
            print(f"  -> tổng hiện tại: {written}")

    print(f"Đã ghi {written} post vào {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
