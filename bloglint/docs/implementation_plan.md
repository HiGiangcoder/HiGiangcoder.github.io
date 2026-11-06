# BlogLint — Kế hoạch triển khai M0 & M1

## 1. Bối cảnh

Repo gốc là blog Jekyll + admin FastAPI. Khi bắt đầu M0, repo **không có**
`AGENTS.md`, `docs/implementation_plan.md`, source BlogLint, test hay benchmark
scaffold nào. Vì vậy tài liệu này được tạo mới từ brief và ghi rõ giả định.

Mục tiêu M0/M1 là dựng nền tảng chẩn đoán bài viết tiếng Việt, chưa huấn luyện
Student và chưa tạo dataset quy mô lớn.

## 2. Kiến trúc

```text
Bài viết Markdown
      │
      ▼
text.py: front matter + paragraph/sentence + offset
      │
      ├── diagnostics.py (rule-based, offline, deterministic) ──► Issue[]
      │
      └── teacher.py (Ollama, chỉ khi được phép) ──► Issue[]
                                                        │
                                                        ▼
                                              dataset.py (JSONL append-only)
                                                        │
                                                        ▼
                                              evaluation.py (golden fixture)
```

### Thành phần

| Module | Trách nhiệm |
| --- | --- |
| `config.py` | Đọc cấu hình từ biến môi trường, không log secret |
| `schema.py` | `Span`, `Issue`, `Paragraph`, `Document`, `AnnotationRecord` |
| `text.py` | Parse front matter, mask code block, chia đoạn/câu, giữ offset |
| `diagnostics.py` | Rule-based diagnostics tiếng Việt |
| `teacher.py` | Prompt, Ollama client, parse/validate JSON của teacher |
| `dataset.py` | Ghi JSONL append-only, chống trùng, manifest |
| `evaluation.py` | Metrics precision/recall/F1 trên golden fixture |
| `cli.py` | `doctor`, `analyze`, `annotate`, `benchmark`, `dataset-stats` |
| admin | Endpoint `/bloglint/analyze` + panel trong trang sửa bài (offline) |

## 3. M0 — Foundation

### Phạm vi

- Tạo package `bloglint` độc lập trong repo.
- Schema dữ liệu và validation cơ bản.
- Parse bài viết Markdown: front matter, đoạn, câu, offset.
- Rule engine offline với các nhóm lỗi:
  - câu quá dài
  - đoạn quá dài
  - từ đệm
  - sáo ngữ
  - lặp từ
  - lỗi dấu câu/khoảng trắng
  - lạm dụng “bị”
  - thiếu tiêu đề mục ở bài dài
- CLI `doctor` và `analyze`.
- Unit test cho schema, text, diagnostics.
- Không gọi mạng.

### Acceptance criteria

- [x] `python3 -m bloglint doctor` chạy được, không gọi mạng.
- [x] `python3 -m bloglint analyze <file>` trả issue deterministic.
- [x] Test M0 chạy pass bằng `unittest`.
- [x] Không có secret trong repo/log.

## 4. M1 — Annotation & benchmark scaffold

### Phạm vi

- Prompt teacher yêu cầu JSON có cấu trúc.
- Ollama client hỗ trợ local và cloud API key, có transport injectable.
- Guard: chỉ gọi mạng khi `--allow-network`; mặc định từ chối.
- Parse/validate JSON teacher, map `quote` → `span`.
- Dataset JSONL append-only, chống ghi đè, chống trùng `content_sha256 + model`.
- Manifest thống kê dataset.
- Golden fixture nhỏ do người viết tự tạo, không phải kết quả model.
- Benchmark tính precision/recall/F1 thật trên fixture.
- Tích hợp admin: panel BlogLint trong trang sửa bài, chỉ dùng rule offline.

### Acceptance criteria

- [x] `annotate --dry-run` in prompt, không gọi mạng.
- [x] `annotate --allow-network` là điều kiện bắt buộc để gọi Ollama.
- [x] Kernel parse được response JSON có/không có code fence; response lỗi bị từ chối.
- [x] Dataset append không overwrite; ghi trùng bị bỏ qua.
- [x] `benchmark` in metrics thật từ golden fixture.
- [x] Unit test teacher/dataset/evaluation/CLI đều pass.
- [x] Admin hiển thị diagnostics offline, không gọi cloud.

### Kết quả kiểm thử thực tế (2026-11-06)

- `PYTHONPATH=src python3 -m unittest discover -s tests -v` → **100 test, OK**.
- `python3 -m bloglint doctor` → chạy được, báo network tắt mặc định, API key chưa cấu hình.
- `python3 -m bloglint analyze fixtures/sample_post.md` → 2 issue (cliche, filler_word),
  offset trỏ đúng vào body.
- `python3 -m bloglint benchmark` → 5 case, TP=6, FP=0, FN=0,
  P=1.0000 / R=1.0000 / F1=1.0000.
  Đây là **smoke fixture do con người viết, bám theo rule**, không phải benchmark
  chất lượng model.
- Admin `POST /bloglint/analyze` → trả 4 issue cho nội dung thử; trang sửa bài render
  panel BlogLint; không gọi mạng.
- Teacher `gpt-oss:120b-cloud` đã annotate end-to-end 9 bài trong `_posts/` qua Ollama
  local proxy. Dataset pilot: **10 record, 65 issue, 0 trùng, mọi span khớp body**.
  Phân bố: clarity 14, coherence 4, factual 9, grammar 14, spelling 2, style 22.
- `backfill-documents` → **10 document**, mỗi hash khớp annotation.
- `export-sft` → **8 train / 2 val**, hash train và val rời nhau.
- Chưa chạy fine-tune; chưa có checkpoint hay metrics train nào.

## 5. Khoảng trống trước khi train

- Cần review thủ công 65 issue pilot; một số issue có thể sai hoặc trùng ý.
- Dataset còn nhỏ (10 bài); cần thêm bài và/hoặc nhiều model annotate.
- Chưa cài `transformers`, `peft`, `trl`; chưa tải `Qwen3-VL-2B`.
- GPU 4 GB VRAM không đủ; cần QLoRA trên GPU ≥ 12 GB hoặc Colab.
- Chưa chạy fine-tune. Mọi số liệu train chỉ được báo sau khi chạy thật.

## 6. Ngoài phạm vi M0/M1

- Không generate dataset lớn.
- Không chạy teacher trên toàn bộ blog.
- Không fine-tune `Qwen3-VL-2B`.
- Không tải checkpoint.
- Không đánh giá chất lượng model thật khi chưa có dữ liệu và approval.

## 7. Rủi ro & giảm thiểu

| Rủi ro | Giảm thiểu |
| --- | --- |
| Gọi cloud ngoài ý muốn | Mặc định `allow_network=False`, CLI cần cờ rõ ràng |
| Ghi đè dataset | Mở file ở mode append, từ chối overwrite |
| Lộ API key | Chỉ đọc từ env, không in giá trị |
| Rule tiếng Việt sai | Test theo fixture, ngưỡng cấu hình được |
| Offset lệch do front matter | Lưu offset trong `body`, không phải toàn file |
| GPU 4 GB không đủ train | Ghi rõ là future work; đề xuất QLoRA/Colab |

## 8. Kế hoạch kiểm thử

```bash
cd bloglint
PYTHONPATH=src python3 -m unittest discover -s tests -v
```

Các nhóm test:

- `test_schema.py`
- `test_text.py`
- `test_diagnostics.py`
- `test_teacher.py`
- `test_dataset.py`
- `test_sft.py`
- `test_evaluation.py`
- `test_cli.py`
- `test_integration.py`

## 9. Việc tiếp theo (ngoài M1)

1. Review thủ công 65 issue pilot; sửa/xoá issue sai trước khi dùng làm target SFT.
2. Bổ sung thêm bài viết hoặc chạy thêm model để tăng độ phủ dữ liệu.
3. Kiểm tra `data/sft/train.jsonl` / `val.jsonl` bằng mắt và bằng script.
4. Dựng môi trường train (`transformers`, `peft`, `trl`, bitsandbytes) trên GPU ≥ 12 GB
   hoặc Colab; dùng QLoRA cho Qwen3-VL-2B.
5. Chỉ train sau khi có approval rõ ràng; báo metrics thật, không suy đoán.
