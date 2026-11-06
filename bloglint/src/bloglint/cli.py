"""CLI BlogLint: doctor, analyze, annotate, benchmark, dataset-stats."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from . import __version__
from .config import Settings
from .dataset import append_records, build_manifest, make_record, write_manifest
from .diagnostics import DiagnosticsConfig, analyze_document, summarize
from .evaluation import benchmark
from .schema import Document
from .teacher import NetworkNotAllowed, OllamaTeacher, TeacherError
from .text import load_document


def _print_json(payload: dict) -> None:
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))


def _load(path: Path) -> Document:
    if not path.exists():
        raise FileNotFoundError(f"Không tìm thấy file: {path}")
    return load_document(path)


def _post_paths(paths: list[str]) -> list[Path]:
    result: list[Path] = []
    for raw in paths:
        path = Path(raw).expanduser()
        if path.is_dir():
            result.extend(sorted(path.glob("*.md")))
        else:
            result.append(path)
    return result


def _diagnostics_config(args: argparse.Namespace) -> DiagnosticsConfig:
    return DiagnosticsConfig(
        max_sentence_words=args.max_sentence_words,
        max_paragraph_words=args.max_paragraph_words,
        long_document_words=args.long_document_words,
    )


def cmd_doctor(args: argparse.Namespace) -> int:
    settings = Settings.from_env(args.repo_root)
    import yaml

    posts = sorted(settings.posts_dir.glob("*.md")) if settings.posts_dir.exists() else []
    payload = {
        "bloglint_version": __version__,
        "python": sys.version.split()[0],
        "pyyaml": getattr(yaml, "__version__", "unknown"),
        "settings": settings.public_dict(),
        "posts_found": len(posts),
        "data_dir_exists": settings.data_dir.exists(),
        "network_default": "disabled",
    }
    if args.json:
        _print_json(payload)
        return 0

    print("BlogLint doctor")
    print(f"- version: {payload['bloglint_version']}")
    print(f"- python: {payload['python']}")
    print(f"- pyyaml: {payload['pyyaml']}")
    print(f"- repo: {settings.repo_root}")
    print(f"- posts: {len(posts)} file trong {settings.posts_dir}")
    print(f"- data dir: {settings.data_dir} (tồn tại: {settings.data_dir.exists()})")
    print(f"- teacher model: {settings.ollama_model}")
    print(f"- teacher base URL: {settings.ollama_base_url}")
    print(f"- API key: {'đã cấu hình' if settings.ollama_api_key else 'chưa cấu hình'}")
    print("- network: tắt mặc định; chỉ bật bằng --allow-network")
    return 0


def cmd_analyze(args: argparse.Namespace) -> int:
    config = _diagnostics_config(args)
    documents = [_load(path) for path in _post_paths(args.paths)]
    results = []
    for document in documents:
        issues = analyze_document(document, config=config)
        results.append(
            {
                "path": document.path,
                "title": document.title,
                "words": document.word_count,
                "summary": summarize(issues),
                "issues": [issue.to_dict() for issue in issues],
            }
        )

    if args.json:
        payload = results[0] if len(results) == 1 else {"documents": results}
        _print_json(payload)
        return 0

    for result in results:
        print(f"\n== {result['path']} ==")
        print(f"{result['title']} ({result['words']} từ)")
        summary = result["summary"]
        print(
            f"{summary['total']} issue: "
            f"{summary['by_severity'].get('error', 0)} error, "
            f"{summary['by_severity'].get('warning', 0)} warning, "
            f"{summary['by_severity'].get('info', 0)} info"
        )
        for issue in result["issues"]:
            span = issue.get("span")
            location = f"[{span['start']}:{span['end']}] " if span else ""
            print(f"- {location}{issue['category']} ({issue['severity']}): {issue['message']}")
            if issue.get("suggestion"):
                print(f"  ↳ {issue['suggestion']}")
    return 0


def _default_golden(settings: Settings) -> Path:
    return settings.repo_root / "bloglint" / "fixtures" / "golden.jsonl"


def cmd_benchmark(args: argparse.Namespace) -> int:
    settings = Settings.from_env(args.repo_root)
    golden = Path(args.golden).expanduser() if args.golden else _default_golden(settings)
    result = benchmark(golden)
    if args.json:
        _print_json(result)
        return 0

    overall = result["overall"]
    print(f"Golden: {golden}")
    print(f"Cases: {result['cases']}")
    print(
        "Overall: "
        f"P={overall['precision']:.4f} "
        f"R={overall['recall']:.4f} "
        f"F1={overall['f1']:.4f} "
        f"(TP={overall['true_positives']}, "
        f"FP={overall['false_positives']}, "
        f"FN={overall['false_negatives']})"
    )
    print("\nTheo category:")
    for category, metrics in result["per_category"].items():
        print(
            f"- {category}: P={metrics['precision']:.4f} "
            f"R={metrics['recall']:.4f} F1={metrics['f1']:.4f} "
            f"(TP={metrics['true_positives']}, "
            f"FP={metrics['false_positives']}, "
            f"FN={metrics['false_negatives']})"
        )
    return 0


def cmd_annotate(args: argparse.Namespace) -> int:
    settings = Settings.from_env(args.repo_root)
    document = _load(Path(args.path).expanduser())

    teacher = OllamaTeacher(
        model=settings.ollama_model,
        base_url=settings.ollama_base_url,
        api_key=settings.ollama_api_key,
        timeout=settings.request_timeout,
        allow_network=args.allow_network,
    )

    if not args.allow_network:
        if args.dry_run:
            from .teacher import build_prompt

            print(build_prompt(document))
            print("\n[dry-run] Không gọi mạng. Thêm --allow-network để gọi teacher.")
            return 0
        print(
            "Từ chối gọi teacher: cần --allow-network (hoặc dùng --dry-run).",
            file=sys.stderr,
        )
        return 2

    if teacher.chat_url.startswith("https://ollama.com") and not settings.ollama_api_key:
        print(
            "Thiếu BLOGLINT_OLLAMA_API_KEY/OLLAMA_API_KEY cho Ollama Cloud.",
            file=sys.stderr,
        )
        return 2

    try:
        result = teacher.annotate(document, allow_network=True)
    except NetworkNotAllowed as exc:
        print(str(exc), file=sys.stderr)
        return 2
    except TeacherError as exc:
        print(f"Teacher lỗi: {exc}", file=sys.stderr)
        return 1

    payload = {
        "path": document.path,
        "title": document.title,
        "model": result.model,
        "issues": [issue.to_dict() for issue in result.issues],
    }
    if args.json:
        _print_json(payload)
    else:
        print(f"Teacher: {result.model}")
        print(f"{len(result.issues)} issue")
        for issue in result.issues:
            print(f"- {issue.category} ({issue.severity}): {issue.message}")
            if issue.suggestion:
                print(f"  ↳ {issue.suggestion}")

    if args.append_dataset:
        record = make_record(
            document,
            result.issues,
            model=result.model,
            meta={"prompt_version": "v1", "source": "teacher", "raw_chars": len(result.raw)},
        )
        appended = append_records(args.append_dataset, [record])
        manifest = build_manifest(Path(args.append_dataset).parent)
        write_manifest(Path(args.append_dataset).parent, manifest)
        print(
            f"Dataset: ghi {appended.written}, bỏ qua {appended.skipped} → {appended.path}",
            file=sys.stderr,
        )
    return 0


def cmd_dataset_stats(args: argparse.Namespace) -> int:
    settings = Settings.from_env(args.repo_root)
    data_dir = Path(args.data_dir).expanduser() if args.data_dir else settings.data_dir
    manifest = build_manifest(data_dir)
    if args.write_manifest:
        target = write_manifest(data_dir, manifest)
        print(f"Đã ghi manifest: {target}")
    if args.json:
        _print_json(manifest)
        return 0

    totals = manifest["totals"]
    print(f"Data dir: {data_dir}")
    print(
        f"{totals['records']} record, {totals['documents']} document, "
        f"{totals['issues']} issue"
    )
    if manifest["per_model"]:
        print("Theo model:")
        for model, count in manifest["per_model"].items():
            print(f"- {model}: {count}")
    if manifest["per_category"]:
        print("Theo category:")
        for category, count in manifest["per_category"].items():
            print(f"- {category}: {count}")
    if not manifest["files"]:
        print("(chưa có file JSONL nào)")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="bloglint", description="BlogLint CLI")
    parser.add_argument("--version", action="version", version=f"bloglint {__version__}")
    parser.add_argument(
        "--repo-root",
        default=None,
        help="Thư mục repo blog (mặc định lấy từ vị trí package).",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    doctor = subparsers.add_parser("doctor", help="Kiểm tra môi trường, không gọi mạng.")
    doctor.add_argument("--json", action="store_true")
    doctor.set_defaults(func=cmd_doctor)

    analyze = subparsers.add_parser("analyze", help="Chạy rule-based diagnostics.")
    analyze.add_argument("paths", nargs="+", help="File hoặc thư mục Markdown.")
    analyze.add_argument("--json", action="store_true")
    analyze.add_argument("--max-sentence-words", type=int, default=40)
    analyze.add_argument("--max-paragraph-words", type=int, default=220)
    analyze.add_argument("--long-document-words", type=int, default=600)
    analyze.set_defaults(func=cmd_analyze)

    annotate = subparsers.add_parser("annotate", help="Gọi teacher (cần quyền mạng).")
    annotate.add_argument("path", help="File Markdown cần annotate.")
    annotate.add_argument("--dry-run", action="store_true", help="Chỉ in prompt.")
    annotate.add_argument("--allow-network", action="store_true", help="Cho phép gọi Ollama.")
    annotate.add_argument("--json", action="store_true")
    annotate.add_argument(
        "--append-dataset", default=None, help="Ghi kết quả vào file JSONL (append-only)."
    )
    annotate.set_defaults(func=cmd_annotate)

    bench = subparsers.add_parser("benchmark", help="Đánh giá trên golden fixture.")
    bench.add_argument("--golden", default=None)
    bench.add_argument("--json", action="store_true")
    bench.set_defaults(func=cmd_benchmark)

    stats = subparsers.add_parser("dataset-stats", help="Thống kê dataset JSONL.")
    stats.add_argument("--data-dir", default=None)
    stats.add_argument("--write-manifest", action="store_true")
    stats.add_argument("--json", action="store_true")
    stats.set_defaults(func=cmd_dataset_stats)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return args.func(args)
    except FileNotFoundError as exc:
        print(str(exc), file=sys.stderr)
        return 2
    except Exception as exc:  # pragma: no cover - fallback an toàn cho CLI
        print(f"Lỗi: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
