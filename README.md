# Ghi chép của Giang

Blog cá nhân viết bằng **Jekyll**, deploy bằng **GitHub Actions**.  
Repo này là **monorepo** gồm hai thành phần tách biệt:

1. **Blog (Jekyll site)** — nằm ở thư mục gốc `/`.
2. **Admin app (FastAPI)** — nằm trong thư mục `admin/`.

Hai thành phần cùng repo nhưng không trộn code: blog là site tĩnh, admin là ứng dụng quản trị chạy Docker và thao tác trực tiếp vào repo.

---

## 1. Tổng quan kiến trúc

```text
HiGiangcoder.github.io/
├── (Blog Jekyll ở thư mục gốc)
├── admin/                  # Web app quản trị
├── docker-compose.yml      # Chạy Jekyll + Admin
├── README.md
└── ...
```

### Blog

- Framework: Jekyll 4
- Markdown: Kramdown (GFM)
- Syntax highlight: Rouge
- Math: MathJax
- Comments: Giscus
- TOC: jekyll-toc
- Deploy: GitHub Actions → GitHub Pages

### Admin

- Framework: FastAPI + Jinja2
- Chạy trong Docker, cổng host `8000`
- Jekyll preview chạy cổng `4000`
- Đọc/ghi trực tiếp vào repo blog qua `REPO_DIR`
- Publish bằng Git (SSH/HTTPS)

---

## 2. Cấu trúc thư mục chi tiết

```text
.
├── _config.yml                 # Cấu hình Jekyll
├── _data/
│   ├── topics.yml              # Chủ đề: tên, slug, màu, mô tả
│   └── site.yml                # Cài đặt hiển thị blog + admin
├── _includes/                  # Partial HTML
│   ├── head.html
│   ├── header.html
│   ├── footer.html
│   └── post-card.html
├── _layouts/                   # Layout: default, home, post, topic, page
├── _posts/                     # Bài viết Markdown
├── assets/
│   ├── css/style.css           # Giao diện blog
│   ├── js/main.js              # JS blog
│   └── images/
│       ├── avatar.jpg
│       ├── favicon.svg
│       └── bai-viet/           # Tài nguyên riêng của từng bài
├── chu-de/                     # Trang cho từng chủ đề
├── _templates/
│   └── bai-viet.md             # Mẫu front matter
├── admin/                      # Web app quản trị
│   ├── main.py
│   ├── Dockerfile
│   ├── entrypoint.sh
│   ├── requirements.txt
│   ├── templates/
│   └── static/admin.css
├── docker-compose.yml
├── Gemfile
├── Gemfile.lock
├── .github/workflows/pages.yml # Build/deploy GitHub Pages
└── README.md
```

---

## 3. Thành phần Blog (Jekyll)

### 3.1. Chạy local

```bash
bundle install
bundle exec jekyll serve --livereload
```

Mở: <http://localhost:4000>

### 3.2. Build tĩnh

```bash
bundle exec jekyll build
```

Output: `_site/`.

### 3.3. Cấu hình chính

File `_config.yml`:

- `title`, `tagline`, `description`
- `url`, `baseurl`
- `permalink: /bai-viet/:year/:month/:day/:title/`
- plugins: `jekyll-feed`, `jekyll-seo-tag`, `jekyll-sitemap`, `jekyll-toc`
- MathJax: `math_engine: mathjax`
- exclude: `admin/`, `Dockerfile`, `docker-compose.yml`, `.github`, v.v.

### 3.4. Chủ đề

File `_data/topics.yml` chứa 4 chủ đề:

- `triet-hoc`
- `tam-ly-hoc`
- `xa-hoi`
- `khac`

Mỗi chủ đề có:

- `slug`
- `name`
- `color`
- `description`

Trang chủ đề nằm trong `chu-de/<slug>.md`.

### 3.5. Cài đặt hiển thị blog

File `_data/site.yml`:

```yaml
home_posts: 6
preview_ratio: '1:2'
admin:
  editor_height: 560
  preview_height: 900
page:
  home_posts: 6
  post_grid_columns: 3
  post_card_min_height: 220
  post_content_width: 760
```

Các giá trị này được admin chỉnh và Jekyll đọc khi build.

### 3.6. Bình luận (Giscus)

File `_layouts/post.html` dùng Giscus với repo:

- Repo: `HiGiangcoder/HiGiangcoder.github.io`
- Category: `General`
- Mapping: `pathname`

### 3.7. Công thức toán

Blog dùng MathJax. Trong Markdown:

```markdown
Inline: $E=mc^2$

Block:
$$
\int_0^1 x^2 \, dx
$$
```

---

## 4. Thành phần Admin (FastAPI)

Thư mục `admin/` là web app quản trị.

### 4.1. Chức năng

- Danh sách, tạo, sửa, xóa bài viết.
- Chỉnh sửa trang chính: giới thiệu, trang chủ, danh sách bài viết, danh sách chủ đề.
- Thêm/sửa/xóa chủ đề và Markdown chủ đề.
- Upload/xóa tài nguyên cho từng bài.
- Dán ảnh trực tiếp từ clipboard.
- Chèn nhanh Markdown/HTML.
- Tự động lưu, hoàn tác/làm lại.
- Xem trước bài viết trong iframe.
- Cài đặt admin và page.
- Chọn file cần commit hoặc commit toàn bộ, sau đó push GitHub.

### 4.2. Chạy bằng Docker (khuyến nghị)

Từ thư mục gốc repo:

```bash
GIT_AUTHOR_NAME="Nguyễn Trường Giang" \
GIT_AUTHOR_EMAIL="giangnt.2006.it@gmail.com" \
docker compose up --build
```

Mở:

- Quản trị: <http://localhost:8000>
- Blog preview: <http://localhost:4000>

### 4.3. Chạy admin không dùng Docker

```bash
cd admin
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

REPO_DIR=".." uvicorn main:app --reload --port 8000
```

### 4.4. Biến môi trường

- `REPO_DIR`: thư mục repo blog. Mặc định: thư mục cha của `admin/`.
- `PREVIEW_URL`: URL Jekyll preview. Mặc định: `http://localhost:4000`.
- `GIT_AUTHOR_NAME`: tên commit.
- `GIT_AUTHOR_EMAIL`: email commit.

### 4.5. Cấu trúc admin

```text
admin/
├── main.py              # FastAPI app
├── Dockerfile
├── entrypoint.sh        # Sao chép SSH key với quyền đúng
├── requirements.txt
├── templates/           # Jinja2 templates
└── static/admin.css     # CSS admin
```

---

## 5. Docker Compose

File `docker-compose.yml` chạy 2 service:

### `jekyll`

- Image: `ruby:3.2`
- Port: `4000`
- Mount: repo gốc vào `/site`
- Cài gems và chạy `jekyll serve --livereload`

### `admin`

- Build từ `./admin`
- Port: `8000`
- Mount repo vào `/site`
- Mount SSH key read-only vào `/host-ssh`
- Entrypoint sao chép SSH sang `/root/.ssh`

### Dừng

```bash
docker compose down
```

---

## 6. Tài nguyên của bài viết

Mỗi bài có thư mục riêng:

```text
assets/images/bai-viet/<ten-file-bai-viet>/
```

Ví dụ:

```text
assets/images/bai-viet/2026-10-18-hai-y-niem-ve-tu-do/
```

Trong admin:

- Upload nhiều file.
- Copy path (biểu thức Jekyll).
- Copy Markdown.
- Chèn ảnh.
- Xóa file.
- Dán ảnh trực tiếp từ clipboard.

Trong Markdown:

```markdown
![Mô tả ảnh]({{ '/assets/images/bai-viet/2026-10-18-hai-y-niem-ve-tu-do/anh.png' | relative_url }})
```

---

## 7. Quy trình publish

1. Sửa nội dung bằng admin.
2. Chọn file cần commit hoặc commit toàn bộ trong ô **Đăng lên GitHub**.
3. Admin chạy `git add`, `git commit`, `git push origin master`.
4. GitHub Actions build Jekyll và deploy Pages.

### SSH trong Docker

Lỗi thường gặp:

```text
Bad owner or permissions on /root/.ssh/config
```

Đã xử lý bằng `entrypoint.sh`: sao chép SSH từ `/host-ssh` sang `/root/.ssh` và `chown root:root`, `chmod 600`.

---

## 8. GitHub Pages

Trong repo GitHub:

- Settings → Pages
- Source: **GitHub Actions**

Workflow: `.github/workflows/pages.yml`

---

## 9. Bảo mật

- Các cổng bind vào `127.0.0.1`.
- Chỉ truy cập từ máy local.
- Không đổi thành `0.0.0.0` nếu chưa có xác thực.

---

## 10. Ghi chú

- `.obsidian/` bị ignore.
- `admin/.venv/`, `__pycache__/` bị ignore.
- Jekyll loại trừ `admin/` khỏi build.
- Cài đặt admin được lưu trong `_data/site.yml`, nên có thể commit cùng blog.