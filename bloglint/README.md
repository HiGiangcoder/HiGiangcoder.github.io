# BlogLint

Trợ lý chẩn đoán bài viết tiếng Việt cho blog Jekyll trong repo này.

- **Teacher (M1)**: `gpt-oss:120b-cloud` qua Ollama, chỉ gọi khi có `--allow-network`.
- **Student (tương lai)**: `Qwen3-VL-2B` + LoRA SFT — **chưa triển khai** trong M0/M1.
- **Hiện tại**: rule-based diagnostics offline, teacher client có thể mock, dataset JSONL
  append-only, benchmark scaffold và tích hợp admin.

## Trạng thái

| Hạng mục | Trạng thái |
| --- | --- |
| M0 — schema, parser, rule engine, CLI | Hoàn thành |
| M1 — teacher client, dataset, benchmark, admin panel | Hoàn thành |
| Generate dataset quy mô lớn | Chưa làm (ngoài phạm vi) |
| Fine-tune Student | Chưa làm (ngoài phạm vi) |

## Cài đặt

```bash
cd bloglint
python3 -m pip install -e .
# hoặc chỉ cần PYTHONPATH
PYTHONPATH=src python3 -m bloglint doctor
```

Yêu cầu: Python 3.10+, `PyYAML>=6.0`. Không cần `pytest`; test dùng `unittest`.

## CLI

```bash
# Kiểm tra môi trường, không gọi mạng
PYTHONPATH=src python3 -m bloglint doctor

# Phân tích một file hoặc cả thư mục
PYTHONPATH=src python3 -m bloglint analyze ../_posts
PYTHONPATH=src python3 -m bloglint analyze ../_posts/2026-11-04-object-writing.md --json

# In prompt teacher mà không gọi mạng
PYTHONPATH=src python3 -m bloglint annotate ../_posts/bai.md --dry-run

# Gọi teacher thật (cần API key nếu dùng Ollama Cloud)
export BLOGLINT_OLLAMA_API_KEY="..."
PYTHONPATH=src python3 -m bloglint annotate ../_posts/bai.md \
  --allow-network --append-dataset data/annotations.jsonl

# Đánh giá trên golden fixture nhỏ
PYTHONPATH=src python3 -m bloglint benchmark

# Thống kê dataset (append-only)
PYTHONPATH=src python3 -m bloglint dataset-stats --write-manifest
```

## Quy tắc an toàn

1. Mặc định **không gọi mạng**. `annotate` từ chối chạy nếu thiếu `--allow-network`.
2. API key chỉ đọc từ biến môi trường, không in ra log hay ghi vào dataset.
3. Dataset chỉ được mở ở chế độ append. Bản ghi trùng `(content_sha256, model)` bị bỏ qua.
4. Dataset và `manifest.json` sinh ra trong `bloglint/data/` và bị `.gitignore`.
5. Không có benchmark nào được bịa; metrics lấy từ lần chạy thật trên fixture.

## Cấu trúc

```text
bloglint/
├── src/bloglint/
│   ├── config.py        # đọc env, không lộ secret
│   ├── schema.py        # Span, Issue, Document, AnnotationRecord
│   ├── text.py          # front matter, đoạn, câu, mask code
│   ├── diagnostics.py   # rule tiếng Việt, deterministic
│   ├── teacher.py       # prompt + Ollama client có guard
│   ├── dataset.py       # JSONL append-only + manifest
│   ├── evaluation.py    # precision/recall/F1 trên golden fixture
│   └── cli.py           # doctor/analyze/annotate/benchmark/dataset-stats
├── tests/               # unittest
├── fixtures/            # bài mẫu + golden smoke fixture
├── docs/                # kế hoạch và quyết định
└── data/                # sinh ra khi chạy, không commit
```

## Định dạng dataset

Mỗi dòng JSONL là một `AnnotationRecord`:

```json
{
  "id": "…",
  "source_path": "../_posts/bai.md",
  "title": "Tiêu đề",
  "content_sha256": "…",
  "model": "gpt-oss:120b-cloud",
  "created_at": "2026-11-06T00:00:00+00:00",
  "issues": [
    {
      "category": "clarity",
      "severity": "warning",
      "message": "…",
      "suggestion": "…",
      "span": {"start": 10, "end": 25, "text": "…"},
      "source": "teacher",
      "paragraph": null,
      "confidence": null
    }
  ],
  "meta": {"prompt_version": "v1", "source": "teacher"}
}
```

## Benchmark

`fixtures/golden.jsonl` là **smoke fixture nhỏ do con người viết**, dùng để kiểm tra
pipeline và offset, không phải thước đo chất lượng model. Vì các nhãn được thiết kế
bám theo rule hiện tại, điểm trên fixture này thường rất cao; không được dùng để
kết luận về chất lượng teacher/Student.

Kết quả thật của lần chạy gần nhất (5 case, 6 issue):

```text
Overall: P=1.0000 R=1.0000 F1=1.0000 (TP=6, FP=0, FN=0)
```

## Giới hạn đã biết

- Rule tiếng Việt là heuristic; chưa có từ điển hình thái/thuật toán NLP. Vì vậy
  rule lặp từ có thể báo nhầm các âm tiết trong từ ghép (ví dụ “giác quan” bị tách
  thành “giác” và “quan”); admin mặc định ẩn các gợi ý mức `info`.
- `max_sentence_words` đếm theo âm tiết (`\w+`), không theo từ ghép.
- BlogLint teacher chưa chạy end-to-end. Đã xác nhận daemon Ollama local proxy được
  `gpt-oss:120b-cloud` bằng một request thử cực nhỏ, nhưng chưa annotate bài thật.
- Chưa có dataset SFT, chưa fine-tune, chưa tải checkpoint.
- GPU local 4 GB VRAM không phù hợp để train Qwen3-VL-2B; cần QLoRA/Colab/GPU đủ mạnh.
