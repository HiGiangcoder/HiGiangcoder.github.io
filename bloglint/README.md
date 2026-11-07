# BlogLint

Trợ lý chẩn đoán bài viết tiếng Việt cho blog Jekyll trong repo này.

- **Teacher (M1)**: `nemotron-3-ultra:cloud` qua Ollama (mặc định), chỉ gọi khi có `--allow-network`.
- **Student (tương lai)**: `Qwen3-VL-2B` + LoRA SFT — **chưa triển khai** trong M0/M1.
- **Hiện tại**: rule-based diagnostics offline, teacher client có thể mock, dataset JSONL
  append-only, benchmark scaffold và tích hợp admin.

## Trạng thái

| Hạng mục | Trạng thái |
| --- | --- |
| M0 — schema, parser, rule engine, CLI | Hoàn thành |
| M1 — teacher client, dataset, benchmark, admin panel | Hoàn thành |
| Pilot annotation 9 bài blog | Hoàn thành: 10 record, 65 issue |
| Audit dataset | Hoàn thành: 0 blocking, 14 warning |
| Export SFT train/val | Hoàn thành pilot: 8 train / 2 val, 56 issue trong phạm vi |
| Generate dataset quy mô lớn | Chưa làm (ngoài phạm vi) |
| Fine-tune Student | Chưa làm; chưa có checkpoint hay kết quả train |

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

# Sao lưu body bài đã annotate vào documents.jsonl (append-only)
PYTHONPATH=src python3 -m bloglint backfill-documents

# Audit span/trùng/quote; ghi review sheet vào data/review.md
PYTHONPATH=src python3 -m bloglint audit-dataset --write-review

# Export SFT train/val (mặc định chỉ category train, loại factual)
PYTHONPATH=src python3 -m bloglint export-sft --output-dir data/sft-v2

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
│   ├── dataset.py       # JSONL append-only + document corpus + manifest
│   ├── audit.py         # audit dataset + review sheet
│   ├── sft.py           # export train/val SFT, chưa train
│   ├── evaluation.py    # precision/recall/F1 trên golden fixture
│   └── cli.py           # doctor/analyze/annotate/audit/export-sft/benchmark
├── tests/               # unittest
├── fixtures/            # bài mẫu + golden smoke fixture
├── docs/                # kế hoạch và quyết định
└── data/                # sinh ra khi chạy, không commit
```

## Định dạng dataset

`data/annotations.jsonl` (append-only, mỗi dòng một `AnnotationRecord`):

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

`data/documents.jsonl` (append-only, mỗi dòng một `DocumentRecord`) lưu body bài viết
theo `content_sha256`:

```json
{
  "content_sha256": "…",
  "title": "Tiêu đề",
  "source_path": "../_posts/bai.md",
  "body": "Nội dung bài…",
  "created_at": "2026-11-06T00:00:00+00:00",
  "meta": {"front_matter_keys": ["title"]}
}
```

`export-sft` join hai file trên và ghi `train.jsonl`, `val.jsonl`, `dataset_info.json`.
Mỗi example có `messages` (user = prompt teacher, assistant = JSON `issues` với
`quote`), split theo `content_sha256` để train/val không rò rỉ bài.

**Phạm vi SFT**: `clarity`, `coherence`, `grammar`, `spelling`, `style`. Category
`factual` bị loại khỏi target train vì model 2B không đủ tin cậy để kiểm chứng kiến
thức bên ngoài; các issue factual vẫn được giữ trong dataset gốc để tham khảo.
Kế hoạch chi tiết ở [`docs/final_product_plan.md`](docs/final_product_plan.md).

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
- Teacher đã chạy end-to-end trên 9 bài blog thật qua Ollama local proxy
  (`gpt-oss:120b-cloud`), tạo 10 record / 65 issue. Chất lượng issue **chưa được
  review thủ công đầy đủ**.
- Matcher quote đi qua 3 lớp: khớp chính xác → gộp khoảng trắng → bỏ markdown/dấu câu/
  hoa thường; có fuzzy match thận trọng cho paraphrase gần đúng. Quote lệch quá xa
  vẫn bị từ chối.
- Dataset pilot còn nhỏ (10 bài); chưa đủ để train có ý nghĩa.
- Đã train pilot 1 epoch trên 8 example (QLoRA 4-bit, RTX 4060 8 GB). Adapter lưu tại
  `data/train-runs/pilot-001`, nhưng eval trên 2 bài held-out cho **0/4 JSON hợp lệ,
  F1 = 0.0000**. Model chưa usable; chưa tích hợp admin.
- GPU local 4 GB VRAM không phù hợp để train Qwen3-VL-2B; cần QLoRA/Colab/GPU đủ mạnh.
