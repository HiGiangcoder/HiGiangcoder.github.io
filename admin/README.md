# Blog Admin

Web app quản trị cho blog Jekyll trong cùng repo.

App nằm trong thư mục `admin/` của repo `HiGiangcoder.github.io`.  
Blog Jekyll nằm ở thư mục gốc repo (thư mục cha của `admin/`).

## Chạy bằng Docker (khuyến nghị)

Từ thư mục gốc repo:

```bash
GIT_AUTHOR_NAME="Nguyễn Trường Giang" \
GIT_AUTHOR_EMAIL="HiGiangcoder@users.noreply.github.com" \
docker compose up --build
```

Mở:

- Giao diện quản trị: <http://localhost:8000>
- Xem trước blog: <http://localhost:4000>

## Chạy local (không Docker)

```bash
cd admin
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

REPO_DIR=".." uvicorn main:app --reload --port 8000
```

## Cấu trúc

```text
admin/
├── main.py              # FastAPI app
├── Dockerfile
├── entrypoint.sh        # Sao chép SSH key với quyền đúng
├── requirements.txt
├── templates/           # Jinja2 templates
└── static/              # admin.css, git-actions.js
```

## Chức năng

- Danh sách, tạo, sửa, xóa bài viết.
- Tách danh sách bài thành **Đang quản lý** (đã đăng GitHub) và **Lưu trữ** (đã gỡ), kèm tìm kiếm.
- Chỉnh sửa trang chính và Markdown chủ đề.
- Thêm/sửa/xóa chủ đề và đổi thứ tự hiển thị bằng nút ↑ ↓.
- Upload/xóa tài nguyên cho từng bài.
- Dán ảnh trực tiếp từ clipboard.
- Chèn nhanh Markdown/HTML.
- Tự động lưu, hoàn tác/làm lại.
- Xem trước bài viết trong iframe.
- Cài đặt admin và page.
- Chọn file cần commit hoặc commit toàn bộ, sau đó push GitHub.
- Gỡ bài khỏi GitHub nhưng vẫn giữ file local, và đăng lại khi cần — thao tác chạy nền, không tải lại trang.
- Lịch sử publish và log chi tiết trong trang **Publish**.
- Liên kết nhanh tới GitHub Pages và bản xem trước local.

## Biến môi trường

- `REPO_DIR`: thư mục repo blog. Mặc định: thư mục cha của `admin/`.
- `PREVIEW_URL`: URL Jekyll preview. Mặc định: `http://localhost:4000`.
- `SITE_URL`: URL GitHub Pages. Mặc định: `https://higiangcoder.github.io`.

## Publish

- SSH key được mount từ `~/.ssh` vào `/host-ssh` (read-only), sau đó entrypoint sao chép sang `/root/.ssh`.
- Nếu dùng HTTPS/PAT, cấu hình credential trong container hoặc đổi remote.

## Bảo mật

Các cổng bind vào `127.0.0.1`, chỉ truy cập từ máy local. Không đổi thành `0.0.0.0` nếu chưa có xác thực.