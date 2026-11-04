# Ghi chép của Giang

Blog cá nhân viết bằng **Jekyll**, deploy bằng **GitHub Actions**.  
Repo này chứa **hai thành phần tách biệt**:

1. **Blog (Jekyll site)** — tại thư mục gốc `/`.
2. **Admin app (FastAPI)** — trong thư mục `admin/`.

Hai thành phần dùng chung một repo, nhưng không trộn code: blog là site tĩnh, admin là ứng dụng quản trị chạy Docker.

## 1. Thành phần Blog (Jekyll)

Thư mục gốc chứa toàn bộ site Jekyll:

- `_posts/` — bài viết Markdown.
- `_layouts/`, `_includes/`, `assets/` — giao diện.
- `_data/` — dữ liệu: chủ đề (`topics.yml`), cấu hình hiển thị (`site.yml`).
- `chu-de/` — trang cho từng chủ đề.
- `gioi-thieu.md`, `index.md`, `bai-viet.md`, `chu-de/index.md` — các trang chính.
- `_config.yml` — cấu hình Jekyll.
- `Gemfile`, `Gemfile.lock` — dependencies Ruby.
- `.github/workflows/pages.yml` — build/deploy GitHub Pages.

### Chạy blog local

```bash
bundle install
bundle exec jekyll serve --livereload
```

Mở: <http://localhost:4000>

### Build tĩnh

```bash
bundle exec jekyll build
```

Output: `_site/`.

## 2. Thành phần Admin (FastAPI)

Thư mục `admin/` là web app quản trị riêng:

- Viết/sửa/xóa bài viết.
- Sửa các trang chính và Markdown chủ đề.
- Thêm/sửa/xóa chủ đề.
- Upload/xóa tài nguyên cho từng bài.
- Dán ảnh trực tiếp từ clipboard.
- Tự động lưu, hoàn tác/làm lại, chèn nhanh Markdown/HTML.
- Xem trước bài viết trong iframe.
- Cài đặt: số bài trang chủ, tỷ lệ cột editor/preview, height editor/preview, số cột và kích thước thẻ bài viết.
- Chọn file cần commit hoặc commit toàn bộ, sau đó push GitHub.

### Chạy bằng Docker (khuyến nghị)

Từ thư mục gốc repo:

```bash
GIT_AUTHOR_NAME="Nguyễn Trường Giang" \
GIT_AUTHOR_EMAIL="giangnt.2006.it@gmail.com" \
docker compose up --build
```

Mở:

- Quản trị: <http://localhost:8000>
- Blog preview: <http://localhost:4000>

### Chạy admin không dùng Docker

```bash
cd admin
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
REPO_DIR=".." uvicorn main:app --reload --port 8000
```

## Cấu trúc thư mục

```text
.
├── _config.yml              # Cấu hình Jekyll
├── _data/
│   ├── topics.yml           # Chủ đề
│   └── site.yml             # Cài đặt hiển thị blog
├── _layouts/                # Layout Jekyll
├── _includes/               # Partial HTML
├── _posts/                  # Bài viết
├── assets/                  # CSS, JS, ảnh
│   └── images/bai-viet/     # Tài nguyên riêng của từng bài
├── chu-de/                  # Trang chủ đề
├── admin/                   # Web app quản trị (FastAPI)
│   ├── main.py
│   ├── Dockerfile
│   ├── entrypoint.sh
│   ├── requirements.txt
│   ├── templates/
│   └── static/
├── docker-compose.yml       # Chạy Jekyll + Admin
├── Gemfile
└── README.md
```

## Ghi chú quan trọng

- GitHub Pages build từ thư mục gốc, nên thư mục `admin/` được loại trừ trong `_config.yml`.
- Admin đọc/ghi trực tiếp vào repo qua `REPO_DIR` (mặc định `/site` trong Docker).
- Nếu push bằng SSH trong Docker, SSH key từ `~/.ssh` được mount read-only vào `/host-ssh`, sau đó entrypoint sao chép sang `/root/.ssh` với quyền đúng.
- Cài đặt admin được lưu trong `_data/site.yml`, nên có thể commit cùng blog.

## Bảo mật

Các cổng được bind vào `127.0.0.1`, chỉ truy cập từ máy local. Không đổi thành `0.0.0.0` nếu chưa có xác thực.