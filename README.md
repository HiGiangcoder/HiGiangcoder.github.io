# Ghi chép của Giang

Blog cá nhân của **Nguyễn Trường Giang** về triết học, tâm lý học, xã hội và những chuyện khác.

Trang được xây bằng **Jekyll** và được **GitHub Pages tự động build** mỗi khi bạn push lên nhánh `master`. Bạn chỉ cần viết Markdown — không cần build, không cần deploy thủ công.

- Trang chủ: <https://higiangcoder.github.io/>
- Nguồn blog: <https://github.com/HiGiangcoder/HiGiangcoder.github.io>
- RSS: <https://higiangcoder.github.io/feed.xml>
- Tài liệu cá nhân (MyDocs): <https://higiangcoder.github.io/MyDocs/>
- Tài liệu tạm (TempDocs): <https://higiangcoder.github.io/TempDocs/>

---

## Viết một bài mới trong 3 bước

### 1. Tạo file trong `_posts/`

Tên file phải theo đúng định dạng:

```text
_posts/YYYY-MM-DD-ten-bai-viet.md
```

Ví dụ:

```text
_posts/2026-11-15-vi-sao-ta-can-su-khiem-ton.md
```

Quy ước cho `ten-bai-viet`:

- Viết thường, không dấu, dùng dấu gạch ngang giữa các từ.
- Không đổi tên file sau khi đã đăng, vì đường dẫn bài viết dựa vào tên file.
- Ngày trong tên file phải khớp với ngày trong phần front matter.

### 2. Dán phần front matter vào đầu file

Có thể copy file mẫu `_templates/bai-viet.md` rồi đổi tên, hoặc dán trực tiếp:

```yaml
---
title: "Tiêu đề bài viết"
date: 2026-11-15 09:00:00 +0700
topic: triet-hoc
description: "Một hai câu tóm tắt hiện ra ở trang chủ và khi chia sẻ lên mạng xã hội."
tags: [tự do, ý nghĩa, triết học]
---

Nội dung bài viết bắt đầu từ đây.
```

Các trường quan trọng:

| Trường | Bắt buộc | Ý nghĩa |
|---|---|---|
| `title` | Có | Tiêu đề bài viết |
| `date` | Có | Ngày đăng, định dạng `YYYY-MM-DD HH:MM:SS +0700` |
| `topic` | Có | Một trong bốn slug: `triet-hoc`, `tam-ly-hoc`, `xa-hoi`, `khac` |
| `description` | Nên có | Tóm tắt 1–2 câu, dùng cho trang chủ, SEO và RSS |
| `tags` | Không | Danh sách thẻ, viết trong ngoặc vuông |

> **Quan trọng:** `topic` phải viết đúng slug. Xem danh sách slug trong `_data/topics.yml`.

### 3. Viết nội dung bằng Markdown

Lưu file, rồi chạy local để xem trước (xem bên dưới), hoặc push thẳng lên GitHub — trang sẽ tự cập nhật sau khoảng 1–2 phút.

---

## Thêm hoặc bớt chủ đề

Chủ đề được định nghĩa ở hai nơi:

1. `_data/topics.yml` — tên, slug, màu và mô tả.
2. `chu-de/<slug>.md` — trang hiển thị bài viết của chủ đề.

### Thêm chủ đề mới

**Bước 1.** Thêm entry vào `_data/topics.yml`:

```yaml
- slug: ten-chu-de
  name: Tên chủ đề
  color: "#8a5a44"
  description: >-
    Mô tả ngắn về chủ đề.
```

**Bước 2.** Tạo file `chu-de/ten-chu-de.md` (hoặc copy `_templates/chu-de.md`):

```yaml
---
layout: topic
title: Tên chủ đề
topic: ten-chu-de
permalink: /chu-de/ten-chu-de/
---
```

**Bước 3.** Viết bài với `topic: ten-chu-de`.

Slug nên viết thường, không dấu, dùng dấu gạch ngang. Không đổi slug sau khi đã có bài vì đường dẫn chủ đề sẽ hỏng.

### Bớt chủ đề

1. Xóa entry tương ứng trong `_data/topics.yml`.
2. Xóa file `chu-de/<slug>.md`.
3. Đổi `topic` của các bài viết thuộc chủ đề đó sang chủ đề khác, hoặc xóa bài.

Sau đó chạy `bundle exec jekyll build` để kiểm tra không còn tham chiếu tới chủ đề cũ.

---

## Chạy thử trên máy (không bắt buộc)

Bạn có thể bỏ qua phần này và push thẳng lên GitHub; GitHub Pages sẽ build hộ. Chạy local chỉ hữu ích khi muốn xem trước khi đăng.

Lần đầu tiên, cài Ruby gems:

```bash
bundle install
```

Sau đó chạy server local:

```bash
bundle exec jekyll serve --livereload
```

Mở <http://localhost:4000>. Mỗi khi lưu file, trang tự tải lại.

Nếu chưa cài Bundler:

```bash
gem install bundler
```

Nếu muốn xem cả bài nháp trong `_drafts/`:

```bash
bundle exec jekyll serve --drafts
```

---

## App quản trị riêng

Giao diện viết/điều khiển blog nằm ở **project riêng**, không nằm trong repo này:

```text
../blog-admin/
```

App đó dùng Docker + FastAPI, đọc/ghi trực tiếp vào repo blog qua biến `BLOG_REPO_PATH` (mặc định trỏ về `../HiGiangcoder.github.io`). Repo blog chỉ chứa nội dung Jekyll, không chứa code quản trị.

App hỗ trợ sửa bài, sửa trang/chủ đề, chỉnh số bài ở trang chủ, upload/xóa tài nguyên cho từng bài (ảnh, PDF, video...), copy path/Markdown, dán ảnh trực tiếp từ clipboard, tự động lưu, xem trước bài viết và thanh chèn nhanh Markdown/HTML.

Cách chạy:

```bash
cd ../blog-admin
docker compose up --build
```

Sau đó mở:

- Quản trị: <http://localhost:8000>
- Xem trước blog: <http://localhost:4000>

Xem hướng dẫn chi tiết trong `../blog-admin/README.md`.

---

## Cấu trúc thư mục

```text
.
├── _config.yml          # Tên blog, mô tả, thông tin tác giả, cấu hình chung
├── _data/
│   ├── topics.yml       # Bốn chủ đề: tên, slug, màu, mô tả
│   └── site.yml         # Cấu hình hiển thị, ví dụ số bài ở trang chủ
├── _includes/           # Các mảnh HTML dùng lại (header, footer, thẻ bài viết)
├── _layouts/            # Giao diện trang chủ, bài viết, chủ đề, lưu trữ
├── _posts/              # ★ NƠI BẠN VIẾT BÀI
├── _templates/
│   └── bai-viet.md      # Mẫu front matter để copy nhanh
├── _drafts/             # Bài nháp (tạo thư mục này nếu cần)
├── assets/
│   ├── css/style.css    # Toàn bộ giao diện
│   ├── js/main.js       # Đổi sáng/tối, tìm kiếm, thanh tiến độ đọc
│   └── images/
│       └── bai-viet/    # Tài nguyên riêng của từng bài (ảnh, PDF, video...)
├── chu-de/              # Trang cho từng chủ đề
├── bai-viet.md          # Trang danh sách tất cả bài viết
├── gioi-thieu.md        # Trang giới thiệu
├── index.md             # Trang chủ
├── 404.html
├── robots.txt
├── Gemfile
└── README.md
```

---

## Mẹo Markdown

### Định dạng cơ bản

```markdown
**In đậm**, *in nghiêng*, ~~gạch ngang~~, `code ngắn`.

## Tiêu đề cấp 2
### Tiêu đề cấp 3

- Gạch đầu dòng
- Mục thứ hai

1. Danh sách đánh số
2. Mục thứ hai

> Trích dẫn dài hoặc một câu tâm đắc.

[Liên kết](https://example.com)
```

### Ảnh

Đặt ảnh vào `assets/images/bai-viet/`, ví dụ:

```text
assets/images/bai-viet/2026-11-15-anh-minh-hoa/anh-minh-hoa.jpg
```

Rồi chèn trong bài:

```markdown
![Mô tả ảnh]({{ '/assets/images/bai-viet/2026-11-15-anh-minh-hoa/anh-minh-hoa.jpg' | relative_url }})
```

Mỗi bài có một thư mục riêng, đặt theo tên file bài viết. App quản trị tự tạo thư mục này khi bạn tải tài nguyên lên.

### Bảng

```markdown
| Cột 1 | Cột 2 |
|---|---|
| Nội dung | Nội dung |
```

### Footnote

```markdown
Một nhận định cần dẫn nguồn.[^1]

[^1]: Tên tác giả, *Tên sách*, Nhà xuất bản, năm.
```

### Công thức toán (MathJax)

Blog đã bật **MathJax**. Viết công thức bằng `$$ ... $$`:

- Inline: `$$P = O + D + S + I$$` → $$P = O + D + S + I$$
- Hiển thị riêng dòng:

```markdown
$$
P = O + D + S + I
$$
```

Lưu ý: không dùng `\\(` `\\)` trực tiếp vì Markdown sẽ bỏ dấu gạch ngược. Dùng `$$...$$` cho cả hai trường hợp.

Dùng HTML nhỏ này để làm nổi bật một ý:

```html
<div class="callout">
  <p><strong>Một câu hỏi để suy nghĩ:</strong> Điều gì khiến mình tin vào điều này?</p>
</div>
```

### Trích dẫn có nguồn

```markdown
> “Câu trích dẫn.”
>
> — Tên tác giả, *Tên tác phẩm*
```

---

## Tùy chỉnh blog

### Đổi tên, mô tả, thông tin cá nhân

Sửa `_config.yml`:

```yaml
title: "Ghi chép của Giang"
tagline: "Triết học, tâm lý học, xã hội và chuyện khác"
description: "..."
author:
  name: "Nguyễn Trường Giang"
  email: "..."
  github: "..."
  facebook: "..."
```

### Đổi màu và phông chữ

Mở `assets/css/style.css`, sửa các biến ở đầu file:

```css
:root {
  --bg: #f8f4ec;        /* nền */
  --ink: #221e18;       /* chữ chính */
  --accent: #9b3d2b;    /* màu nhấn */
  --serif: "Lora", Georgia, serif;
  --sans: "Be Vietnam Pro", sans-serif;
}
```

### Thêm hoặc đổi chủ đề

Sửa `_data/topics.yml`:

```yaml
- slug: ten-chu-de
  name: Tên chủ đề
  color: "#8a5a44"
  description: "Mô tả ngắn."
```

Sau đó tạo trang trong `chu-de/ten-chu-de.md`:

```yaml
---
layout: topic
title: Tên chủ đề
topic: ten-chu-de
permalink: /chu-de/ten-chu-de/
---
```

Và cập nhật danh sách slug trong hướng dẫn này.

> Không đổi `slug` của chủ đề đã có bài viết, vì sẽ làm hỏng liên kết.

### Đổi ảnh đại diện

Thay file `assets/images/avatar.jpg` bằng ảnh mới (giữ nguyên tên file).

---

## Đăng bài lên GitHub Pages

### Quy trình 3 lệnh

```bash
git add .
git commit -m "Viết bài: Tên bài viết"
git push origin master
```

GitHub Pages sẽ tự build và cập nhật trang sau khoảng 1–2 phút. Không cần chạy `npm`, `gh-pages` hay build thủ công.

Nếu push bị từ chối vì remote có commit mới:

```bash
git pull --rebase origin master
git push origin master
```

### Repo này hoạt động thế nào?

Repo tên `HiGiangcoder.github.io` là **user site** của GitHub Pages:

- URL gốc: `https://higiangcoder.github.io/`
- Nguồn: nhánh `master`, thư mục gốc.
- GitHub tự chạy Jekyll khi thấy `_config.yml`.

Vì vậy:

- Bài viết trong `_posts/` tự động thành trang.
- Blog build bằng GitHub Actions (workflow `.github/workflows/pages.yml`) để hỗ trợ plugin `jekyll-toc`.
- Không cần tạo nhánh `gh-pages` cho blog này.
- Nhánh `gh-pages` cũ (nếu còn trên remote) là di sản từ site MkDocs trước đây, không ảnh hưởng tới blog. Chỉ xóa khi chắc chắn không dùng:

```bash
git push origin --delete gh-pages
```

### Kiểm tra Settings → Pages

Vào **Settings → Pages** của repo:

- **Source:** GitHub Actions

Workflow `.github/workflows/pages.yml` sẽ tự build Jekyll (kèm plugin `jekyll-toc`) mỗi khi push lên `master`. Sau khi push, theo dõi tiến trình build ở tab **Actions**.

> Vì blog dùng plugin `jekyll-toc`, **không** dùng chế độ "Deploy from a branch" (chế độ đó chạy Jekyll ở safe mode, không load plugin).

---

## Dùng kèm MyDocs / TempDocs

`MyDocs` và `TempDocs` là **hai repo riêng**, không nằm trong repo blog này. Blog chỉ đặt liên kết ở footer và trang giới thiệu; push blog không làm thay đổi hai trang tài liệu.

| Trang | Repo | Công nghệ | Ghi chú |
|---|---|---|---|
| [MyDocs](https://higiangcoder.github.io/MyDocs/) | [HiGiangcoder/MyDocs](https://github.com/HiGiangcoder/MyDocs) | MkDocs Material | Repo hiện chủ yếu chứa bản build trong `site/` |
| [TempDocs](https://higiangcoder.github.io/TempDocs/) | [HiGiangcoder/TempDocs](https://github.com/HiGiangcoder/TempDocs) | MkDocs Material | Source Markdown nằm trong `docs/` |

### Cách dùng TempDocs (có source rõ ràng)

```bash
git clone git@github.com:HiGiangcoder/TempDocs.git
cd TempDocs

python3 -m venv .venv
source .venv/bin/activate

pip install mkdocs-material mkdocs-awesome-pages-plugin \
  mkdocs-include-markdown-plugin mkdocs-minify-plugin mkdocs-glightbox

mkdocs serve
```

Mở <http://127.0.0.1:8000>. Sửa file trong `docs/`, thêm mục vào `nav:` trong `mkdocs.yml` (hoặc để plugin `awesome-pages` tự sắp xếp). Khi xong, deploy:

```bash
mkdocs gh-deploy --force
```

Lệnh này build site và đẩy lên nhánh `gh-pages` của repo TempDocs. Trong **Settings → Pages** của repo TempDocs, chọn:

- **Source:** Deploy from a branch
- **Branch:** `gh-pages` / `(root)`

### MyDocs

MyDocs dùng cùng công nghệ MkDocs Material, nhưng hiện nhánh `master` chủ yếu chứa thư mục `site/` (bản đã build) và `mkdocs.yml`; không thấy thư mục `docs/` chứa Markdown nguồn. Vì vậy:

- Nếu source gốc vẫn còn trên máy: sửa ở đó rồi chạy `mkdocs gh-deploy --force`.
- Nếu muốn làm lại từ đầu: tạo thư mục `docs/`, chuyển các file Markdown vào, thêm `docs_dir: docs` vào `mkdocs.yml` nếu cần, rồi `mkdocs serve` / `mkdocs gh-deploy --force`.
- Không nên sửa trực tiếp HTML trong `site/` trừ khi chỉ muốn vá tạm, vì lần build sau sẽ ghi đè.

### Thêm hoặc đổi link tài liệu trong blog

Sửa hai chỗ:

- `_includes/footer.html` — link ở footer.
- `gioi-thieu.md` — các nút ở trang giới thiệu.

### Khối mở rộng (đóng/mở)

Dùng HTML `<details markdown="1">` (có `markdown="1"`) để nội dung bên trong vẫn được xử lý Markdown:

```markdown
<details markdown="1">
  <summary>Bấm để xem thêm</summary>

  Nội dung ẩn **Markdown**.

  - Mục 1
  - Mục 2

</details>
```

Thiếu `markdown="1"` sẽ làm nội dung hiển thị thô (không in đậm, không danh sách). Nếu không muốn dùng Markdown bên trong, có thể bỏ `markdown="1"` và viết văn bản/HTML thường.

**Cách an toàn (khuyến nghị nếu dùng nhiều Markdown):**

```markdown
{% capture noi_dung %}
Nội dung ẩn **Markdown**.

- Mục 1
- Mục 2
{% endcapture %}

{% include details.html summary="Bấm để xem thêm" content=noi_dung %}
```

---

## Bình luận (Giscus)

Blog dùng **Giscus** (GitHub Discussions) cho bình luận ở cuối mỗi bài viết.

### Đã cấu hình

- Repo: `HiGiangcoder/HiGiangcoder.github.io`
- Category: `General`
- Mapping: `pathname` (mỗi bài viết = 1 discussion)

### Bật/tắt hoặc đổi category

Sửa các giá trị `data-*` trong `_layouts/post.html` (phần `<script src="https://giscus.app/client.js" ...>`).

### Yêu cầu trên GitHub

1. Vào **Settings → Features → Discussions** và bật.
2. Cài Giscus app: <https://github.com/apps/giscus>.
3. Tạo category trong Discussions (ví dụ `General`).

### Đồng bộ sáng/tối

Script trong `_layouts/post.html` tự gửi message tới iframe Giscus khi bạn bấm nút đổi theme.

---

## Những lỗi thường gặp

**Bài viết không xuất hiện**

- Kiểm tra tên file có đúng `YYYY-MM-DD-ten-bai.md` không.
- Kiểm tra `date` trong front matter có đúng định dạng không.
- Bài có ngày trong tương lai sẽ không được build (trừ khi chạy `--future`).
- Kiểm tra `topic` có khớp slug trong `_data/topics.yml` không.

**Trang trắng hoặc lỗi build**

- Chạy `bundle exec jekyll build` để xem thông báo lỗi cụ thể.
- Kiểm tra YAML: dấu hai chấm, dấu ngoặc kép và thụt lề rất dễ gây lỗi.
- Nếu vừa sửa `_config.yml`, cần khởi động lại server local.

**Ảnh không hiện**

- Đảm bảo đường dẫn bắt đầu bằng `/assets/...`.
- Kiểm tra tên file có dấu cách hoặc ký tự đặc biệt — nên đổi sang chữ thường, không dấu.

**Tìm kiếm không bỏ dấu**

Trang `/bai-viet/` đã hỗ trợ tìm không dấu. Nếu thêm bài mới mà tìm không ra, kiểm tra `description` và `title` có nằm trong front matter không.

---

## Ghi chú kỹ thuật

- Blog dùng Jekyll 3.x đi kèm GitHub Pages, theme tự viết, không phụ thuộc theme ngoài.
- Các plugin: `jekyll-feed` (RSS), `jekyll-seo-tag` (meta SEO), `jekyll-sitemap` (sitemap).
- Trang chủ, trang chủ đề và trang lưu trữ tự động lấy bài từ `_posts/`.
- Dark mode được lưu trong `localStorage`; nếu chưa chọn, blog theo cài đặt hệ điều hành.
- Không commit thư mục `_site/` — đã có trong `.gitignore`.

---

## Giấy phép

Nội dung bài viết thuộc về tác giả. Mã nguồn giao diện có thể dùng lại cho mục đích cá nhân.
