# Ghi chép của Giang

[![Tiếng Việt](https://img.shields.io/badge/lang-Tiếng%20Việt-red)](README.md)
[![English](https://img.shields.io/badge/lang-English-blue)](README.en.md)

A personal blog built with **Jekyll**, deployed with **GitHub Actions**.  
This repository is a **monorepo** containing two separate components:

1. **Blog (Jekyll site)** — in the repository root `/`.
2. **Admin app (FastAPI)** — in the `admin/` directory.

Both components share one repository but their code is not mixed: the blog is a static site, while the admin app is a Dockerized management application that operates directly on the repository.

---

## 1. Architecture overview

```text
HiGiangcoder.github.io/
├── (Jekyll blog in repository root)
├── admin/                  # Management web app
├── docker-compose.yml      # Runs Jekyll + Admin
├── README.md
└── ...
```

### Blog

- Framework: Jekyll 4
- Markdown: Kramdown (GFM)
- Syntax highlighting: Rouge
- Math: MathJax
- Comments: Giscus
- TOC: jekyll-toc
- Deployment: GitHub Actions → GitHub Pages

### Admin

- Framework: FastAPI + Jinja2
- Runs in Docker, host port `8000`
- Jekyll preview runs on port `4000`
- Reads/writes the blog repository through `REPO_DIR`
- Publishes with Git (SSH/HTTPS)

---

## 2. Detailed directory structure

```text
.
├── _config.yml                 # Jekyll configuration
├── _data/
│   ├── topics.yml              # Topics: name, slug, color, description
│   └── site.yml                # Blog and admin display settings
├── _includes/                  # HTML partials
├── _layouts/                   # Layouts: default, home, post, topic, page
├── _posts/                     # Markdown posts
├── assets/
│   ├── css/style.css           # Blog styles
│   ├── js/main.js              # Blog JavaScript
│   └── images/
│       ├── avatar.jpg
│       ├── favicon.svg
│       └── bai-viet/           # Per-post resources
├── chu-de/                     # Topic pages
├── _templates/
│   └── bai-viet.md             # Front matter template
├── admin/                      # Management web app
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
├── README.md
└── README.en.md
```

---

## 3. Blog component (Jekyll)

### 3.1. Run locally

```bash
bundle install
bundle exec jekyll serve --livereload
```

Open: <http://localhost:4000>

### 3.2. Static build

```bash
bundle exec jekyll build
```

Output: `_site/`.

### 3.3. Main configuration

`_config.yml` contains:

- `title`, `tagline`, `description`
- `url`, `baseurl`
- `permalink: /bai-viet/:year/:month/:day/:title/`
- plugins: `jekyll-feed`, `jekyll-seo-tag`, `jekyll-sitemap`, `jekyll-toc`
- MathJax: `math_engine: mathjax`
- excluded: `admin/`, `Dockerfile`, `docker-compose.yml`, `.github`, etc.

### 3.4. Topics

`_data/topics.yml` contains 4 topics:

- `triet-hoc`
- `tam-ly-hoc`
- `xa-hoi`
- `khac`

Each topic has:

- `slug`
- `name`
- `color`
- `description`

Topic pages are stored in `chu-de/<slug>.md`.

### 3.5. Display settings

`_data/site.yml`:

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

These values are edited by the admin app and read by Jekyll during build.

### 3.6. Comments (Giscus)

`_layouts/post.html` uses Giscus with:

- Repo: `HiGiangcoder/HiGiangcoder.github.io`
- Category: `General`
- Mapping: `pathname`

### 3.7. Math

The blog uses MathJax. In Markdown:

```markdown
Inline: $E=mc^2$

Block:
$$
\int_0^1 x^2 \, dx
$$
```

---

## 4. Admin component (FastAPI)

The `admin/` directory is a separate management web app.

### 4.1. Features

- List, create, edit, delete posts.
- Edit main pages and topic Markdown.
- Add/edit/delete topics.
- Upload/delete resources for each post.
- Paste images directly from clipboard.
- Quick insert Markdown/HTML.
- Autosave, undo/redo.
- Live post preview in an iframe.
- Admin and page settings.
- Select files to commit or commit all, then push to GitHub.
- Unpublish a post from GitHub while keeping it locally, and republish it later.

### 4.2. Run with Docker (recommended)

From the repository root:

```bash
GIT_AUTHOR_NAME="Nguyễn Trường Giang" \
GIT_AUTHOR_EMAIL="giangnt.2006.it@gmail.com" \
docker compose up --build
```

Open:

- Admin: <http://localhost:8000>
- Blog preview: <http://localhost:4000>

### 4.3. Run admin without Docker

```bash
cd admin
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

REPO_DIR=".." uvicorn main:app --reload --port 8000
```

### 4.4. Environment variables

- `REPO_DIR`: blog repository directory. Default: parent of `admin/`.
- `PREVIEW_URL`: Jekyll preview URL. Default: `http://localhost:4000`.
- `GIT_AUTHOR_NAME`: commit author name.
- `GIT_AUTHOR_EMAIL`: commit author email.

### 4.5. Admin structure

```text
admin/
├── main.py              # FastAPI app
├── Dockerfile
├── entrypoint.sh        # Copy SSH keys with correct permissions
├── requirements.txt
├── templates/           # Jinja2 templates
└── static/admin.css     # Admin CSS
```

---

## 5. Docker Compose

`docker-compose.yml` runs two services:

### `jekyll`

- Image: `ruby:3.2`
- Port: `4000`
- Mounts repository root to `/site`
- Installs gems and runs `jekyll serve --livereload`

### `admin`

- Builds from `./admin`
- Port: `8000`
- Mounts repository root to `/site`
- Mounts SSH key read-only to `/host-ssh`
- Entrypoint copies SSH keys to `/root/.ssh`

### Stop

```bash
docker compose down
```

---

## 6. Per-post resources

Each post has its own directory:

```text
assets/images/bai-viet/<post-file-name>/
```

Example:

```text
assets/images/bai-viet/2026-10-18-hai-y-niem-ve-tu-do/
```

In the admin app:

- Upload multiple files.
- Copy path (Jekyll expression).
- Copy Markdown.
- Insert image.
- Delete file.
- Paste images directly from clipboard.

In Markdown:

```markdown
![Image description]({{ '/assets/images/bai-viet/2026-10-18-hai-y-niem-ve-tu-do/image.png' | relative_url }})
```

---

## 7. Publishing workflow

1. Edit content with the admin app.
2. Select files to commit or commit all in the **Publish to GitHub** section.
3. The admin app runs `git add`, `git commit`, and `git push origin master`.
4. GitHub Actions builds Jekyll and deploys Pages.

### SSH in Docker

Common error:

```text
Bad owner or permissions on /root/.ssh/config
```

This is handled by `entrypoint.sh`: SSH files are copied from `/host-ssh` to `/root/.ssh` with `chown root:root` and `chmod 600`.

---

## 8. GitHub Pages

In the GitHub repository:

- Settings → Pages
- Source: **GitHub Actions**

Workflow: `.github/workflows/pages.yml`

---

## 9. Security

- Ports are bound to `127.0.0.1`.
- Accessible only from the local machine.
- Do not change to `0.0.0.0` without authentication.

---

## 10. Notes

- `.obsidian/` is ignored.
- `admin/.venv/` and `__pycache__/` are ignored.
- Jekyll excludes `admin/` from the build.
- Admin settings are stored in `_data/site.yml`, so they can be committed together with the blog.

---

## License

This project is licensed under the **MIT License**.  
See the [LICENSE](LICENSE) file for details.

© 2026 Nguyễn Trường Giang.