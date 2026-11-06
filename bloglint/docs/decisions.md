# Quyết định kỹ thuật — BlogLint M0/M1

Ghi lại các lựa chọn quan trọng, lý do và hệ quả. Mọi quyết định đều có thể xem lại
khi mở rộng sang dataset/Student.

## D1. Đặt BlogLint trong `bloglint/` của repo blog

**Lý do**: brief yêu cầu thêm tính năng vào repo này; repo chưa có scaffold BlogLint
nào để tái sử dụng.

**Hệ quả**: Jekyll có thể build nhầm thư mục, nên `bloglint` được thêm vào
`exclude` của `_config.yml`. Package độc lập, không import admin.

## D2. Chỉ dùng standard library + `PyYAML`

**Lý do**: giảm dependency, dễ chạy trong container admin vốn đã có `PyYAML`.
Không cần `pydantic` cho schema nhỏ.

**Hệ quả**: validation viết tay trong `schema.py`; test dùng `unittest` vì môi trường
không có `pytest`.

## D3. Rule-based diagnostics chạy trước, teacher là tùy chọn

**Lý do**: M0 cần kết quả deterministic, offline, không tốn phí; teacher có thể lỗi
hoặc thay đổi theo phiên bản model.

**Hệ quả**: `analyze` và admin chỉ dùng rule. Teacher chỉ xuất hiện ở `annotate` với
`--allow-network`.

## D4. Offset tính trong `body`, không phải toàn file

**Lý do**: front matter thay đổi độ dài và không phải nội dung cần chấm. `mask_code`
thay ký tự bằng khoảng trắng cùng độ dài để offset không lệch.

**Hệ quả**: mọi `Span` trỏ vào `Document.body`; admin và dataset dùng cùng quy ước.

## D5. Teacher trả `quote`, hệ thống tự quy đổi thành `span`

**Lý do**: LLM đếm offset kém chính xác. Yêu cầu trích nguyên văn rồi `body.find`
an toàn hơn và kiểm chứng được.

**Hệ quả**: quote không tồn tại trong bài bị từ chối toàn bộ response
(`TeacherResponseError`), tránh dữ liệu bẩn.

## D6. Dataset JSONL append-only, khóa chống trùng `(content_sha256, model)`

**Lý do**: cùng một bài có thể được annotate bởi nhiều model; chạy lại cùng model
không nên nhân đôi dữ liệu. Brief cấm ghi đè dataset.

**Hệ quả**: `append_records` chỉ mở file ở mode `a`; manifest là file dẫn xuất được
phép ghi đè nguyên tử qua file tạm + `os.replace`.

## D7. Network guard ở cả CLI và client

**Lý do**: tránh gọi cloud ngoài ý muốn khi test hoặc khi admin tự động chạy.

**Hệ quả**: `OllamaTeacher.annotate` ném `NetworkNotAllowed` nếu không được phép;
CLI trả mã 2 và hướng dẫn dùng `--allow-network` hoặc `--dry-run`. Transport có thể
inject để test không cần mạng.

## D8. Golden fixture là smoke test, không phải benchmark chất lượng

**Lý do**: M0/M1 chưa có dữ liệu gán nhãn độc lập. Fixture được viết tay nhưng bám
theo các rule đã biết, nên điểm cao không chứng minh chất lượng thật.

**Hệ quả**: báo cáo phải ghi rõ F1=1.0 trên fixture chỉ xác nhận pipeline/offset;
muốn đánh giá thật cần golden set độc lập do người review.

## D9. Admin chỉ gọi rule offline

**Lý do**: trang sửa bài cần phản hồi nhanh, không phụ thuộc API key/cloud, và không
được gửi nội dung chưa công bố ra ngoài ngoài ý muốn.

**Hệ quả**: endpoint `/bloglint/analyze` import `bloglint` từ `/site/bloglint/src`
nếu có; nếu thiếu package thì trả 503 thay vì làm sập admin.

## D10. Chưa generate dataset, chưa fine-tune

**Lý do**: brief giới hạn M0/M1; chưa có approval rõ ràng; chưa có API key; GPU
4 GB VRAM không đủ thoải mái cho Qwen3-VL-2B.

**Hệ quả**: các bước tiếp theo cần approval riêng, cấu hình key, và phần cứng phù hợp.
