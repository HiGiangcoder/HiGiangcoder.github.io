# Kế hoạch sản phẩm cuối — BlogLint Student

## 1. Sản phẩm cuối là gì

**BlogLint Student v1** là một adapter LoRA cho `Qwen3-VL-2B`, chạy local, nhận một bài
blog tiếng Việt và trả về JSON gồm các issue:

```json
{
  "issues": [
    {
      "category": "clarity | coherence | grammar | spelling | style",
      "severity": "info | warning | error",
      "message": "mô tả ngắn gọn",
      "suggestion": "cách sửa cụ thể",
      "quote": "trích nguyên văn trong bài"
    }
  ]
}
```

Sản phẩm hoàn chỉnh gồm:

1. Dataset SFT đã review, có train/validation/held-out test tách theo bài.
2. Adapter LoRA + config train tái lập được.
3. Script evaluation độc lập, báo metrics thật.
4. Tích hợp admin: nút "AI review" chạy local, tắt mặc định; rule offline vẫn là fallback.
5. Tài liệu cài đặt, giới hạn, và quy trình cập nhật dataset.

### Trong phạm vi

- Lỗi diễn đạt, mạch lạc, ngữ pháp, chính tả, style trong bài blog cá nhân.
- Trích dẫn nguyên văn để UI highlight đúng vị trí.
- Chạy offline sau khi tải model/adapter một lần.

### Ngoài phạm vi

- Fact-check toàn diện (kiểm chứng nguồn, số liệu, trích dẫn học thuật).
- Viết lại toàn bài hoặc tự động sửa file.
- Đảm bảo chính xác tuyệt đối; mọi gợi ý vẫn cần người đọc duyệt.

> Quyết định: `factual` không dùng làm nhãn train chính. Các issue factual hiện có được
> giữ để tham khảo nhưng đánh dấu cần review thủ công, vì 2B model không đủ tin cậy để
> kiểm chứng kiến thức bên ngoài.

## 2. Tiêu chí nghiệm thu

| Mã | Tiêu chí | Cách đo |
| --- | --- | --- |
| G1 | Dataset đủ lớn và sạch | ≥ 100 bài đã review; ≥ 400 issue; 0 lỗi blocking |
| G2 | Định dạng đầu ra | ≥ 98% response parse được JSON; ≥ 95% quote khớp span |
| G3 | Chất lượng | Micro F1 ≥ 0.60 trên held-out; mỗi category chính ≥ 0.45 |
| G4 | Tích hợp | Admin gọi được adapter local; rule offline vẫn chạy khi tắt AI |
| G5 | Tái lập | Có config, seed, hash dataset, báo cáo eval và phiên bản model |

Các ngưỡng trên là **mục tiêu kỹ thuật**, không phải kết quả đã đạt. Chỉ báo số thật
sau khi chạy evaluation.

## 3. Các giai đoạn

### Giai đoạn 0 — Chốt phạm vi (đang làm)

- [x] Chốt output schema và phạm vi category.
- [x] Loại factual khỏi nhãn train chính.
- [ ] Chốt ngưỡng nghiệm thu với người dùng.

### Giai đoạn 1 — Dataset v1

- [x] Audit tự động: trùng span, span lệch, quote ngắn, thiếu suggestion, thiếu document.
- [x] Tạo review sheet để người dùng duyệt từng issue.
- [ ] Chốt issue nào giữ, sửa, xoá; lưu quyết định append-only.
- [ ] Bổ sung bài viết đến ≥ 100 bài (nguồn hợp lệ, có sự đồng ý).
- [ ] Freeze split: train / validation / held-out test theo `content_sha256`.
- [x] Export SFT pilot chỉ từ category trong phạm vi.
- [ ] Export SFT cuối cùng chỉ từ issue đã accept.

### Giai đoạn 2 — Scaffolding train & eval

- [ ] Viết script QLoRA có guard, không tự tải model, không tự chạy.
- [ ] Viết evaluation harness cho Student, dùng cùng matcher với Teacher.
- [ ] Dry-run trên dữ liệu giả để kiểm tra pipeline, không cần GPU.
- [ ] Ghi rõ phiên bản thư viện và yêu cầu VRAM.

### Giai đoạn 3 — Train pilot

- [x] Được duyệt ngân sách/hardware.
- [x] Train pilot trên GPU 8 GB (RTX 4060) bằng QLoRA 4-bit; không train trên máy 4 GB.
- [x] Lưu adapter, config, log, dataset hash.
- [x] Không tải/không train trên máy 4 GB VRAM.

> Pilot train đã chạy trên `master.iec`, GPU 1 (RTX 4060 8 GB), 1 epoch, 8 example,
> 4-bit QLoRA. Adapter lưu tại `data/train-runs/pilot-001`.
> Kết quả eval trên 2 bài held-out: **0/4 prediction parse được JSON, F1 = 0.0000**.
> Nguyên nhân chính: model sinh JSON không hoàn chỉnh và category không hợp lệ;
> dữ liệu quá ít (8 example) và chỉ 1 epoch. Chưa đạt G2/G3.

### Giai đoạn 4 — Đánh giá & lặp

- [ ] Chạy evaluation trên held-out.
- [ ] So sánh với rule baseline và Teacher.
- [ ] Phân tích lỗi theo category; bổ sung dữ liệu đúng chỗ.
- [ ] Chỉ công bố khi đạt G2/G3.

### Giai đoạn 5 — Tích hợp admin

- [ ] Inference local có timeout và fallback rule.
- [ ] Nút AI review trong trang sửa bài, mặc định tắt.
- [ ] Hiển thị quote/span, severity, suggestion.
- [ ] Không gửi nội dung ra cloud.

### Giai đoạn 6 — Đóng gói

- [ ] README cài đặt adapter, cách chạy eval.
- [ ] Ghi giới hạn và quy trình cập nhật dataset.
- [ ] Commit code; không commit dataset/model nặng.

## 4. Trạng thái hiện tại

- Dataset: 101 record từ 9 bài blog + 92 bài Vietnamese news, 787 issue.
- Audit: 2 blocking (duplicate issue cùng span), 134 warning.
- SFT v5: 82 train / 20 val example, 102 chunk, 100 document, 749 issue trong phạm vi.
- Train pilot v1: 1 epoch, 8 example, QLoRA 4-bit, F1 = 0.0000 (chưa usable).
- Training v5 chưa chạy vì SSH `master.iec` hiện không kết nối được.
- Đang annotate thêm 200 bài trong background.

## 5. Việc làm ngay

1. Review thủ công `data/review.md`; accept/reject/sửa từng issue.
2. Bổ sung dữ liệu đến ≥ 100 bài trước khi train tiếp.
3. Chạy train 3-5 epoch trên dataset đã review, sau đó eval lại.
4. Nếu vẫn F1 thấp: rút gọn prompt, giảm số issue/example, hoặc tăng model size.
5. Sau khi đạt G2/G3 mới tích hợp admin.

## 6. Rủi ro chính

| Rủi ro | Giảm thiểu |
| --- | --- |
| Teacher tạo issue sai | Review thủ công + audit trùng/lệch span |
| Dataset quá nhỏ | Bổ sung bài có kiểm soát; không train vội |
| Model 2B bịa lỗi | Yêu cầu quote khớp body; reject response sai |
| Factual không kiểm chứng được | Loại khỏi nhãn train chính |
| Train không tái lập | Lưu config, seed, hash, phiên bản thư viện |
| GPU yếu | QLoRA trên Colab/GPU thuê, không train local 4 GB |
