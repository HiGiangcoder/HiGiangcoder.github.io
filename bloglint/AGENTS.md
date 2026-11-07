# BlogLint — Quy ước làm việc

Tài liệu này dành cho người và AI agent làm việc trong `bloglint/`.

## Mục tiêu

BlogLint là trợ lý chẩn đoán bài viết tiếng Việt cho blog Jekyll trong repo này.

- **Teacher**: `nemotron-3-ultra:cloud` qua Ollama (mặc định; có thể đổi trong Admin → Cài đặt).
- **Student** (tương lai): `Qwen3-VL-2B` + LoRA SFT.
- **M0/M1 hiện tại**: nền tảng, schema, rule-based diagnostics, teacher client có thể mock,
  dataset JSONL append-only, benchmark scaffold, CLI và tích hợp admin.

## Giới hạn bắt buộc

- Không tự động gọi Ollama Cloud khi chưa có `--allow-network` hoặc chưa được duyệt.
- Không tạo dataset tổng hợp quy mô lớn trong M0/M1.
- Không fine-tune Student trong M0/M1.
- Không tải checkpoint lớn.
- Không ghi đè dataset đã có; chỉ append.
- Không đưa API key vào code, log, fixture hay commit.
- Không bịa kết quả benchmark. Mọi số liệu trong báo cáo phải lấy từ lần chạy thật.

## Cấu trúc

```text
bloglint/
├── src/bloglint/       # package
├── tests/              # unittest, không cần pytest
├── fixtures/           # dữ liệu nhỏ, tự tạo, dùng cho test/benchmark
├── docs/               # kế hoạch và quyết định
└── scripts/            # script có guard, không tự chạy
```

## Quy ước code

- Python 3.10+; ưu tiên standard library.
- `PyYAML` chỉ dùng để đọc front matter; không thêm dependency nặng.
- Mọi chức năng gọi mạng phải injectable để test bằng fake transport.
- Issue phải có `category`, `severity`, `message`; `span` là offset ký tự trong `body`.
- Rule-based diagnostics phải deterministic: cùng input → cùng output, cùng thứ tự.
- Test bằng `python3 -m unittest discover -s tests`.
- Không sửa code blog/admin ngoài phạm vi tích hợp cần thiết.

## Acceptance criteria M0/M1

Xem `docs/implementation_plan.md`.
