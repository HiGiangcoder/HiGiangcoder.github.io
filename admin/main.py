"""Giao diện quản trị riêng cho blog Jekyll.

Chạy trong Docker (xem docker-compose.yml) hoặc local:

    pip install -r requirements.txt
    uvicorn main:app --reload --port 8000

Biến môi trường:
    REPO_DIR      Thư mục repo blog (mặc định: ../HiGiangcoder.github.io)
    PREVIEW_URL   URL của Jekyll preview (mặc định: http://localhost:4000)
"""

from __future__ import annotations

import os
import re
import shutil
import subprocess
import unicodedata
from datetime import date, datetime
from pathlib import Path

import frontmatter
import yaml
from fastapi import FastAPI, File, Form, HTTPException, Request, UploadFile
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

BASE_DIR = Path(__file__).resolve().parent
# admin/ nằm trong repo blog, nên repo blog là thư mục cha.
DEFAULT_REPO = BASE_DIR.parent
REPO_DIR = Path(os.environ.get("REPO_DIR", DEFAULT_REPO)).resolve()
POSTS_DIR = REPO_DIR / "_posts"
TOPICS_FILE = REPO_DIR / "_data" / "topics.yml"
SITE_DATA_FILE = REPO_DIR / "_data" / "site.yml"
TOPIC_PAGES_DIR = REPO_DIR / "chu-de"
PREVIEW_URL = os.environ.get("PREVIEW_URL", "http://localhost:4000")

EDITABLE_PAGES = {
    "gioi-thieu.md": "Trang giới thiệu",
    "index.md": "Trang chủ",
    "bai-viet.md": "Danh sách bài viết",
    "chu-de/index.md": "Danh sách chủ đề",
}

ASSETS_DIR = REPO_DIR / "assets"
MEDIA_ROOT = ASSETS_DIR / "images" / "bai-viet"
ALLOWED_ASSET_EXT = {
    ".jpg", ".jpeg", ".png", ".gif", ".webp", ".svg", ".avif",
    ".pdf", ".mp4", ".webm", ".mp3", ".txt", ".zip",
}
IMAGE_ASSET_EXT = {".jpg", ".jpeg", ".png", ".gif", ".webp", ".svg", ".avif"}
MAX_ASSET_SIZE = 25 * 1024 * 1024
MAX_ASSETS_PER_UPLOAD = 20

app = FastAPI(title="Blog Admin")
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")
if ASSETS_DIR.exists():
    app.mount("/blog-assets", StaticFiles(directory=ASSETS_DIR), name="blog-assets")
templates = Jinja2Templates(directory=BASE_DIR / "templates")


def slugify(value: str) -> str:
    value = unicodedata.normalize("NFD", value)
    value = "".join(ch for ch in value if unicodedata.category(ch) != "Mn")
    value = value.replace("đ", "d").replace("Đ", "D")
    value = value.lower()
    value = re.sub(r"[^a-z0-9]+", "-", value)
    return value.strip("-") or "bai-viet"


def load_topics() -> list[dict]:
    if not TOPICS_FILE.exists():
        return []
    data = yaml.safe_load(TOPICS_FILE.read_text(encoding="utf-8")) or []
    return data if isinstance(data, list) else []


def save_topics(topics: list[dict]) -> None:
    TOPICS_FILE.parent.mkdir(parents=True, exist_ok=True)
    TOPICS_FILE.write_text(
        yaml.safe_dump(topics, allow_unicode=True, sort_keys=False),
        encoding="utf-8",
    )


def post_files() -> list[Path]:
    if not POSTS_DIR.exists():
        return []
    return sorted(POSTS_DIR.glob("*.md"), reverse=True)


def load_meta_content(path: Path) -> tuple[dict, str]:
    post = frontmatter.load(path)
    return dict(post.metadata), post.content


def write_meta_content(path: Path, metadata: dict, content: str) -> None:
    post = frontmatter.Post(content.strip() + "\n", **metadata)
    path.write_text(frontmatter.dumps(post), encoding="utf-8")


PREVIEW_RATIO_OPTIONS = [
    "1:4", "1:3", "1:2", "2:3", "1:1",
    "3:2", "2:1", "3:1", "4:1",
]


def default_site_data() -> dict:
    return {
        "home_posts": 6,
        "preview_ratio": "1:2",
        "admin": {
            "editor_height": 560,
            "preview_height": 900,
        },
        "page": {
            "home_posts": 6,
            "post_grid_columns": 3,
            "post_card_min_height": 220,
            "post_content_width": 760,
        },
    }


def normalize_site_data(data: dict) -> dict:
    if not isinstance(data, dict):
        data = {}
    base = default_site_data()
    base.update({k: v for k, v in data.items() if k not in ("admin", "page")})
    admin = base["admin"].copy()
    admin.update(data.get("admin", {}) if isinstance(data.get("admin"), dict) else {})
    raw_page = data.get("page", {}) if isinstance(data.get("page"), dict) else {}
    page = base["page"].copy()
    page.update(raw_page)
    if "home_posts" in data and "home_posts" not in raw_page:
        page["home_posts"] = data["home_posts"]
    base["admin"] = admin
    base["page"] = page

    if base.get("preview_ratio") not in PREVIEW_RATIO_OPTIONS:
        base["preview_ratio"] = "1:2"
    try:
        home_posts = max(1, min(50, int(page.get("home_posts", base.get("home_posts", 6)))))
    except (TypeError, ValueError):
        home_posts = 6
    base["home_posts"] = home_posts
    page["home_posts"] = home_posts
    try:
        base["admin"]["editor_height"] = max(300, min(1200, int(base["admin"].get("editor_height", 560))))
    except (TypeError, ValueError):
        base["admin"]["editor_height"] = 560
    try:
        base["admin"]["preview_height"] = max(400, min(1400, int(base["admin"].get("preview_height", 900))))
    except (TypeError, ValueError):
        base["admin"]["preview_height"] = 900
    try:
        base["page"]["post_grid_columns"] = max(2, min(4, int(base["page"].get("post_grid_columns", 3))))
    except (TypeError, ValueError):
        base["page"]["post_grid_columns"] = 3
    try:
        base["page"]["post_card_min_height"] = max(120, min(420, int(base["page"].get("post_card_min_height", 220))))
    except (TypeError, ValueError):
        base["page"]["post_card_min_height"] = 220
    try:
        base["page"]["post_content_width"] = max(600, min(960, int(base["page"].get("post_content_width", 760))))
    except (TypeError, ValueError):
        base["page"]["post_content_width"] = 760
    return base


def load_site_data() -> dict:
    if not SITE_DATA_FILE.exists():
        return default_site_data()
    data = yaml.safe_load(SITE_DATA_FILE.read_text(encoding="utf-8")) or {}
    return normalize_site_data(data)


def save_site_data(data: dict) -> None:
    SITE_DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
    SITE_DATA_FILE.write_text(
        yaml.safe_dump(data, allow_unicode=True, sort_keys=False),
        encoding="utf-8",
    )


def changed_files() -> list[dict]:
    result = subprocess.run(
        ["git", "status", "--porcelain"],
        cwd=REPO_DIR,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        return []
    items = []
    for line in result.stdout.splitlines():
        if not line.strip():
            continue
        status = line[:2].strip() or "?"
        path = line[3:].strip()
        if " -> " in path:
            path = path.split(" -> ", 1)[1]
        items.append({"status": status, "path": path})
    return items


def safe_repo_path(rel_path: str) -> Path:
    candidate = (REPO_DIR / rel_path).resolve()
    if candidate != REPO_DIR and REPO_DIR not in candidate.parents:
        raise HTTPException(400, "Đường dẫn không hợp lệ.")
    git_dir = (REPO_DIR / ".git").resolve()
    if candidate == git_dir or git_dir in candidate.parents:
        raise HTTPException(400, "Không được thao tác trên thư mục .git.")
    return candidate


def asset_dir_for(filename: str) -> Path:
    stem = Path(filename).stem
    if not re.fullmatch(r"[A-Za-z0-9._-]+", stem):
        raise HTTPException(400, "Tên file bài viết không hợp lệ.")
    return MEDIA_ROOT / stem


def human_size(size: int) -> str:
    if size < 1024:
        return f"{size} B"
    if size < 1024 * 1024:
        return f"{size / 1024:.1f} KB"
    return f"{size / (1024 * 1024):.1f} MB"


def serialize_asset(path: Path) -> dict:
    rel = path.relative_to(REPO_DIR).as_posix()
    url_expr = f"{{{{ '/{rel}' | relative_url }}}}"
    suffix = path.suffix.lower()
    size = path.stat().st_size
    return {
        "name": path.name,
        "size": size,
        "size_label": human_size(size),
        "path": rel,
        "url_expr": url_expr,
        "markdown": f"![{path.stem}]({url_expr})",
        "is_image": suffix in IMAGE_ASSET_EXT,
        "preview_url": f"/blog-assets/{rel.removeprefix('assets/')}",
    }


def list_assets(filename: str) -> list[dict]:
    folder = asset_dir_for(filename)
    if not folder.exists():
        return []
    return [
        serialize_asset(path)
        for path in sorted(folder.iterdir())
        if path.is_file()
    ]


def safe_asset_name(name: str) -> str:
    name = unicodedata.normalize("NFD", name)
    name = "".join(ch for ch in name if unicodedata.category(ch) != "Mn")
    name = name.replace("đ", "d").replace("Đ", "D")
    name = re.sub(r"[^A-Za-z0-9._-]+", "-", name).strip("-")
    return name or "file"


def unique_asset_path(folder: Path, name: str) -> Path:
    stem = Path(name).stem
    suffix = Path(name).suffix
    candidate = folder / f"{stem}{suffix}"
    counter = 1
    while candidate.exists():
        candidate = folder / f"{stem}-{counter}{suffix}"
        counter += 1
    return candidate


def load_post(path: Path) -> tuple[dict, str]:
    post = frontmatter.load(path)
    meta = dict(post.metadata)
    return meta, post.content


def list_posts() -> list[dict]:
    items = []
    for path in post_files():
        try:
            meta, _ = load_post(path)
        except Exception:
            continue
        items.append(
            {
                "filename": path.name,
                "title": meta.get("title", path.stem),
                "date": meta.get("date", ""),
                "topic": meta.get("topic", ""),
                "description": meta.get("description", ""),
            }
        )
    return items


def parse_post_time(post_time: str) -> datetime.time:
    value = (post_time or "").strip()
    if not value:
        return datetime.min.time()
    try:
        return datetime.strptime(value, "%H:%M").time()
    except ValueError:
        raise HTTPException(400, "Giờ không hợp lệ (HH:MM).")


def write_post(
    filename: str,
    title: str,
    post_date: date,
    post_time: str,
    topic: str,
    description: str,
    tags: str,
    content: str,
) -> Path:
    tag_list = [t.strip() for t in tags.split(",") if t.strip()]
    parsed_time = parse_post_time(post_time)
    metadata = {
        "title": title.strip(),
        "date": datetime.combine(post_date, parsed_time).strftime(
            "%Y-%m-%d %H:%M:%S +0700"
        ),
        "topic": topic.strip(),
        "description": description.strip(),
        "tags": tag_list,
    }
    text = "---\n"
    text += yaml.safe_dump(metadata, allow_unicode=True, sort_keys=False)
    text += "---\n\n"
    text += content.strip() + "\n"
    path = POSTS_DIR / filename
    path.write_text(text, encoding="utf-8")
    return path


def save_post_values(
    filename: str,
    title: str,
    post_date: str,
    post_time: str,
    topic: str,
    description: str,
    tags: str,
    content: str,
) -> tuple[str, Path]:
    path = POSTS_DIR / filename
    if not path.exists():
        raise HTTPException(404, "Không tìm thấy bài viết.")
    if not title.strip():
        raise HTTPException(400, "Tiêu đề không được để trống.")
    if not topic.strip():
        raise HTTPException(400, "Chưa chọn chủ đề.")
    try:
        parsed_date = date.fromisoformat(post_date)
    except ValueError:
        raise HTTPException(400, "Ngày không hợp lệ (YYYY-MM-DD).")

    new_filename = f"{parsed_date.isoformat()}-{slugify(title)}.md"
    if new_filename != filename:
        target_path = POSTS_DIR / new_filename
        if target_path.exists():
            stem = target_path.stem
            counter = 2
            while (POSTS_DIR / f"{stem}-{counter}.md").exists():
                counter += 1
            new_filename = f"{stem}-{counter}.md"
            target_path = POSTS_DIR / new_filename

        if path.exists():
            shutil.move(str(path), str(target_path))

        old_asset = (MEDIA_ROOT / Path(filename).stem).resolve()
        new_asset = (MEDIA_ROOT / Path(new_filename).stem).resolve()
        if old_asset.exists() and old_asset != new_asset:
            if not new_asset.exists():
                old_asset.rename(new_asset)
            else:
                new_asset.mkdir(parents=True, exist_ok=True)
                for child in old_asset.iterdir():
                    destination = new_asset / child.name
                    if not destination.exists():
                        child.rename(destination)
                if not any(old_asset.iterdir()):
                    old_asset.rmdir()

        filename = new_filename

    saved_path = write_post(
        filename,
        title,
        parsed_date,
        post_time,
        topic,
        description,
        tags,
        content,
    )
    return filename, saved_path


def post_preview_url(filename: str, post_date: str) -> str:
    stem = Path(filename).stem
    slug = re.sub(r"^\d{4}-\d{2}-\d{2}-", "", stem)
    try:
        parsed = date.fromisoformat(str(post_date)[:10])
    except ValueError:
        parsed = date.today()
    return (
        f"{PREVIEW_URL}/bai-viet/"
        f"{parsed.year:04d}/{parsed.month:02d}/{parsed.day:02d}/{slug}/"
    )


@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "posts": list_posts(),
            "topics": load_topics(),
            "changed_files": changed_files(),
            "files": changed_files(),
            "preview_url": PREVIEW_URL,
            "repo_dir": str(REPO_DIR),
        },
    )


@app.get("/posts/new", response_class=HTMLResponse)
def new_post(request: Request):
    return templates.TemplateResponse(
        "edit.html",
        {
            "request": request,
            "mode": "new",
            "filename": "",
            "meta": {
                "title": "",
                "date": date.today().isoformat(),
                "time": datetime.now().strftime("%H:%M"),
                "topic": "",
                "description": "",
                "tags": [],
            },
            "content": "",
            "topics": load_topics(),
            "assets": [],
            "admin_settings": load_site_data().get("admin", {}),
            "preview_ratio": load_site_data().get("preview_ratio", "1:2"),
            "preview_url": PREVIEW_URL,
        },
    )


@app.post("/posts/new")
def create_post(
    title: str = Form(...),
    post_date: str = Form(...),
    post_time: str = Form("00:00"),
    topic: str = Form(...),
    description: str = Form(""),
    tags: str = Form(""),
    content: str = Form(""),
):
    try:
        parsed_date = date.fromisoformat(post_date)
    except ValueError:
        raise HTTPException(400, "Ngày không hợp lệ (YYYY-MM-DD).")

    filename = f"{parsed_date.isoformat()}-{slugify(title)}.md"
    path = POSTS_DIR / filename
    if path.exists():
        raise HTTPException(400, f"Bài viết đã tồn tại: {filename}")

    write_post(filename, title, parsed_date, post_time, topic, description, tags, content)
    return RedirectResponse(f"/posts/{filename}/edit", status_code=303)


@app.get("/posts/{filename}/edit", response_class=HTMLResponse)
def edit_post(request: Request, filename: str):
    path = POSTS_DIR / filename
    if not path.exists():
        raise HTTPException(404, "Không tìm thấy bài viết.")
    meta, content = load_post(path)
    post_date = meta.get("date")
    if isinstance(post_date, datetime):
        meta["time"] = post_date.strftime("%H:%M")
        post_date = post_date.date().isoformat()
    elif isinstance(post_date, date):
        meta["time"] = "00:00"
        post_date = post_date.isoformat()
    else:
        raw = str(post_date or "")
        meta["time"] = raw[11:16] if len(raw) >= 16 else "00:00"
        post_date = raw[:10]
    meta["date"] = post_date
    if not meta.get("time"):
        meta["time"] = "00:00"
    return templates.TemplateResponse(
        "edit.html",
        {
            "request": request,
            "mode": "edit",
            "filename": filename,
            "meta": meta,
            "content": content,
            "topics": load_topics(),
            "assets": list_assets(filename),
            "post_url": post_preview_url(filename, meta["date"]),
            "preview_ratio": load_site_data().get("preview_ratio", "1:2"),
            "admin_settings": load_site_data().get("admin", {}),
            "preview_url": PREVIEW_URL,
        },
    )


@app.post("/posts/{filename}/edit")
def update_post(
    filename: str,
    title: str = Form(...),
    post_date: str = Form(...),
    post_time: str = Form("00:00"),
    topic: str = Form(...),
    description: str = Form(""),
    tags: str = Form(""),
    content: str = Form(""),
):
    new_filename, _ = save_post_values(
        filename, title, post_date, post_time, topic, description, tags, content
    )
    return RedirectResponse(f"/posts/{new_filename}/edit", status_code=303)


@app.post("/posts/{filename}/autosave")
def autosave_post(
    filename: str,
    title: str = Form(...),
    post_date: str = Form(...),
    post_time: str = Form("00:00"),
    topic: str = Form(...),
    description: str = Form(""),
    tags: str = Form(""),
    content: str = Form(""),
):
    new_filename, _ = save_post_values(
        filename, title, post_date, post_time, topic, description, tags, content
    )
    return {
        "ok": True,
        "saved_at": datetime.now().strftime("%H:%M:%S"),
        "filename": new_filename,
        "preview_url": post_preview_url(new_filename, post_date),
    }


async def save_uploaded_assets(
    filename: str,
    uploads: list[UploadFile],
) -> list[dict]:
    path = POSTS_DIR / filename
    if not path.exists():
        raise HTTPException(404, "Không tìm thấy bài viết.")

    if len(uploads) > MAX_ASSETS_PER_UPLOAD:
        raise HTTPException(
            400,
            f"Chỉ được tải lên tối đa {MAX_ASSETS_PER_UPLOAD} file mỗi lần.",
        )

    prepared = []
    for upload in uploads:
        original = safe_asset_name(upload.filename or "file")
        suffix = Path(original).suffix.lower()
        if suffix not in ALLOWED_ASSET_EXT:
            raise HTTPException(
                400,
                f"Định dạng file không được hỗ trợ: {upload.filename}",
            )
        prepared.append(upload)

    folder = asset_dir_for(filename)
    folder_existed = folder.exists()
    folder.mkdir(parents=True, exist_ok=True)
    saved: list[Path] = []

    for upload in prepared:
        destination = unique_asset_path(
            folder,
            safe_asset_name(upload.filename or "file"),
        )
        size = 0
        try:
            with destination.open("wb") as out:
                while True:
                    chunk = await upload.read(1024 * 1024)
                    if not chunk:
                        break
                    size += len(chunk)
                    if size > MAX_ASSET_SIZE:
                        raise HTTPException(
                            413,
                            f"File vượt quá {human_size(MAX_ASSET_SIZE)}: {upload.filename}",
                        )
                    out.write(chunk)
            saved.append(destination)
        except Exception:
            if destination.exists():
                destination.unlink()
            for path_item in saved:
                if path_item.exists():
                    path_item.unlink()
            if not folder_existed and folder.exists() and not any(folder.iterdir()):
                folder.rmdir()
            raise
        finally:
            await upload.close()

    return [serialize_asset(path_item) for path_item in saved]


@app.post("/posts/{filename}/assets")
async def upload_assets(
    filename: str,
    files: list[UploadFile] = File(...),
):
    await save_uploaded_assets(filename, files)
    return RedirectResponse(f"/posts/{filename}/edit", status_code=303)


@app.post("/posts/{filename}/assets/paste")
async def paste_asset(
    filename: str,
    file: UploadFile = File(...),
):
    saved = await save_uploaded_assets(filename, [file])
    return {"asset": saved[0]}


@app.post("/posts/{filename}/assets/{asset_name}/delete")
def delete_asset(filename: str, asset_name: str):
    path = POSTS_DIR / filename
    if not path.exists():
        raise HTTPException(404, "Không tìm thấy bài viết.")

    folder = asset_dir_for(filename).resolve()
    candidate = (folder / asset_name).resolve()
    if candidate.parent != folder or not candidate.is_file():
        raise HTTPException(404, "Không tìm thấy tài nguyên.")

    candidate.unlink()
    if not any(folder.iterdir()):
        folder.rmdir()
    return RedirectResponse(f"/posts/{filename}/edit", status_code=303)


@app.post("/posts/{filename}/delete")
def delete_post(filename: str):
    path = POSTS_DIR / filename
    if path.exists():
        path.unlink()
    return RedirectResponse("/", status_code=303)


@app.get("/topics", response_class=HTMLResponse)
def topics_page(request: Request):
    return templates.TemplateResponse(
        "topics.html",
        {
            "request": request,
            "topics": load_topics(),
            "preview_url": PREVIEW_URL,
        },
    )


@app.post("/topics")
def add_topic(
    slug: str = Form(...),
    name: str = Form(...),
    color: str = Form("#6f6a5f"),
    description: str = Form(""),
):
    topics = load_topics()
    slug = slugify(slug)
    if any(t.get("slug") == slug for t in topics):
        raise HTTPException(400, "Slug chủ đề đã tồn tại.")
    topics.append(
        {
            "slug": slug,
            "name": name.strip(),
            "color": color.strip(),
            "description": description.strip(),
        }
    )
    save_topics(topics)

    page = TOPIC_PAGES_DIR / f"{slug}.md"
    if not page.exists():
        page.write_text(
            "---\n"
            "layout: topic\n"
            f"title: {name.strip()}\n"
            f"topic: {slug}\n"
            f"permalink: /chu-de/{slug}/\n"
            "---\n",
            encoding="utf-8",
        )
    return RedirectResponse("/topics", status_code=303)


@app.post("/topics/{slug}/delete")
def delete_topic(slug: str):
    topics = [t for t in load_topics() if t.get("slug") != slug]
    save_topics(topics)
    page = TOPIC_PAGES_DIR / f"{slug}.md"
    if page.exists():
        page.unlink()
    return RedirectResponse("/topics", status_code=303)


@app.get("/pages", response_class=HTMLResponse)
def pages_page(request: Request):
    pages = [
        {"name": name, "label": label, "exists": (REPO_DIR / name).exists()}
        for name, label in EDITABLE_PAGES.items()
    ]
    return templates.TemplateResponse(
        "pages.html",
        {
            "request": request,
            "pages": pages,
            "preview_url": PREVIEW_URL,
        },
    )


@app.get("/pages/{name:path}/edit", response_class=HTMLResponse)
def edit_page(request: Request, name: str):
    if name not in EDITABLE_PAGES:
        raise HTTPException(404, "Trang không được phép chỉnh sửa.")
    path = safe_repo_path(name)
    if not path.exists():
        raise HTTPException(404, "Không tìm thấy file.")
    meta, content = load_meta_content(path)
    return templates.TemplateResponse(
        "page_edit.html",
        {
            "request": request,
            "name": name,
            "label": EDITABLE_PAGES[name],
            "meta_yaml": yaml.safe_dump(meta, allow_unicode=True, sort_keys=False),
            "content": content,
            "preview_url": PREVIEW_URL,
        },
    )


@app.post("/pages/{name:path}/edit")
def update_page(
    name: str,
    meta_yaml: str = Form(...),
    content: str = Form(""),
):
    if name not in EDITABLE_PAGES:
        raise HTTPException(404, "Trang không được phép chỉnh sửa.")
    path = safe_repo_path(name)
    try:
        meta = yaml.safe_load(meta_yaml) or {}
    except yaml.YAMLError as exc:
        raise HTTPException(400, f"YAML không hợp lệ: {exc}")
    if not isinstance(meta, dict):
        raise HTTPException(400, "Front matter phải là một object YAML.")
    write_meta_content(path, meta, content)
    return RedirectResponse("/pages", status_code=303)


@app.get("/topics/{slug}/edit", response_class=HTMLResponse)
def edit_topic(request: Request, slug: str):
    topics = load_topics()
    topic = next((t for t in topics if t.get("slug") == slug), None)
    if not topic:
        raise HTTPException(404, "Không tìm thấy chủ đề.")
    page_path = TOPIC_PAGES_DIR / f"{slug}.md"
    content = ""
    if page_path.exists():
        _, content = load_meta_content(page_path)
    return templates.TemplateResponse(
        "topic_edit.html",
        {
            "request": request,
            "topic": topic,
            "content": content,
            "preview_url": PREVIEW_URL,
        },
    )


@app.post("/topics/{slug}/edit")
def update_topic(
    slug: str,
    name: str = Form(...),
    color: str = Form("#6f6a5f"),
    description: str = Form(""),
    content: str = Form(""),
):
    topics = load_topics()
    topic = next((t for t in topics if t.get("slug") == slug), None)
    if not topic:
        raise HTTPException(404, "Không tìm thấy chủ đề.")

    topic["name"] = name.strip()
    topic["color"] = color.strip()
    topic["description"] = description.strip()
    save_topics(topics)

    page_path = TOPIC_PAGES_DIR / f"{slug}.md"
    meta = {
        "layout": "topic",
        "title": name.strip(),
        "topic": slug,
        "permalink": f"/chu-de/{slug}/",
    }
    write_meta_content(page_path, meta, content)
    return RedirectResponse("/topics", status_code=303)


@app.get("/settings", response_class=HTMLResponse)
def settings_page(request: Request):
    return templates.TemplateResponse(
        "settings.html",
        {
            "request": request,
            "site_data": load_site_data(),
            "preview_url": PREVIEW_URL,
        },
    )


@app.post("/settings")
def update_settings(
    home_posts: int = Form(6),
    preview_ratio: str = Form("1:2"),
    admin_editor_height: int = Form(560),
    admin_preview_height: int = Form(900),
    page_post_grid_columns: int = Form(3),
    page_post_card_min_height: int = Form(220),
    page_post_content_width: int = Form(760),
):
    if home_posts < 1 or home_posts > 50:
        raise HTTPException(400, "Số bài viết phải từ 1 đến 50.")
    if preview_ratio not in PREVIEW_RATIO_OPTIONS:
        raise HTTPException(400, "Tỷ lệ cột xem trước không hợp lệ.")
    data = load_site_data()
    data["preview_ratio"] = preview_ratio
    data.setdefault("admin", {})
    data["admin"]["editor_height"] = admin_editor_height
    data["admin"]["preview_height"] = admin_preview_height
    data.setdefault("page", {})
    data["page"]["home_posts"] = home_posts
    data["page"]["post_grid_columns"] = page_post_grid_columns
    data["page"]["post_card_min_height"] = page_post_card_min_height
    data["page"]["post_content_width"] = page_post_content_width
    data = normalize_site_data(data)
    save_site_data(data)
    return RedirectResponse("/settings", status_code=303)


@app.get("/publish", response_class=HTMLResponse)
def publish_page(request: Request):
    return templates.TemplateResponse(
        "publish_changes.html",
        {
            "request": request,
            "files": changed_files(),
            "preview_url": PREVIEW_URL,
        },
    )


@app.post("/publish", response_class=HTMLResponse)
def publish(
    request: Request,
    message: str = Form("Cập nhật blog"),
    commit_all: str = Form(""),
    files: list[str] = Form([]),
):
    author_name = os.environ.get("GIT_AUTHOR_NAME", "Blog Admin")
    author_email = os.environ.get("GIT_AUTHOR_EMAIL", "blog-admin@example.com")
    commands = []

    if commit_all:
        commands.append(["git", "add", "-A"])
    else:
        if not files:
            raise HTTPException(400, "Chưa chọn file nào để commit.")
        for rel in files:
            safe_repo_path(rel)
        commands.append(["git", "add", "-A", "--", *files])

    commands.extend(
        [
            [
                "git",
                "-c",
                f"user.name={author_name}",
                "-c",
                f"user.email={author_email}",
                "commit",
                "-m",
                message or "Cập nhật blog",
            ],
            ["git", "push", "origin", "master"],
        ]
    )

    outputs = []
    for cmd in commands:
        result = subprocess.run(
            cmd, cwd=REPO_DIR, capture_output=True, text=True
        )
        outputs.append(
            f"$ {' '.join(cmd)}\n{result.stdout}{result.stderr}".strip()
        )
        if result.returncode != 0:
            break
    return templates.TemplateResponse(
        "publish.html",
        {
            "request": request,
            "outputs": "\n\n".join(outputs),
            "preview_url": PREVIEW_URL,
        },
    )
