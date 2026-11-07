from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

DEFAULT_MODEL = "nemotron-3-ultra:cloud"
DEFAULT_BASE_URL = "http://localhost:11434"
CLOUD_BASE_URL = "https://ollama.com"


def _env_bool(name: str, default: bool = False) -> bool:
    value = os.environ.get(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


@dataclass(frozen=True)
class Settings:
    """Cấu hình BlogLint. Không chứa/hiển thị giá trị API key."""

    repo_root: Path
    posts_dir: Path
    data_dir: Path
    ollama_base_url: str = DEFAULT_BASE_URL
    ollama_model: str = DEFAULT_MODEL
    ollama_api_key: str | None = None
    request_timeout: float = 120.0
    allow_network: bool = False

    @classmethod
    def from_env(cls, repo_root: str | Path | None = None) -> "Settings":
        if repo_root is not None:
            root = Path(repo_root).expanduser().resolve()
        elif os.environ.get("BLOGLINT_REPO_ROOT"):
            root = Path(os.environ["BLOGLINT_REPO_ROOT"]).expanduser().resolve()
        else:
            # bloglint/src/bloglint/config.py -> repo root
            root = Path(__file__).resolve().parents[3]

        api_key = os.environ.get("BLOGLINT_OLLAMA_API_KEY") or os.environ.get(
            "OLLAMA_API_KEY"
        )
        site_bloglint: dict = {}
        site_file = root / "_data" / "site.yml"
        if site_file.exists():
            try:
                import yaml

                loaded = yaml.safe_load(site_file.read_text(encoding="utf-8")) or {}
                if isinstance(loaded, dict) and isinstance(loaded.get("bloglint"), dict):
                    site_bloglint = loaded["bloglint"]
            except Exception:  # pragma: no cover
                site_bloglint = {}

        base_url = os.environ.get("BLOGLINT_OLLAMA_BASE_URL")
        if not base_url:
            base_url = site_bloglint.get("ollama_base_url")
        if not base_url:
            base_url = CLOUD_BASE_URL if api_key else DEFAULT_BASE_URL

        model = os.environ.get("BLOGLINT_OLLAMA_MODEL")
        if not model:
            model = site_bloglint.get("ollama_model", DEFAULT_MODEL)

        data_dir = os.environ.get("BLOGLINT_DATA_DIR")
        data_path = Path(data_dir).expanduser() if data_dir else root / "bloglint" / "data"

        return cls(
            repo_root=root,
            posts_dir=root / "_posts",
            data_dir=data_path,
            ollama_base_url=base_url.rstrip("/"),
            ollama_model=model,
            ollama_api_key=api_key,
            request_timeout=float(os.environ.get("BLOGLINT_TIMEOUT", "120")),
            allow_network=_env_bool("BLOGLINT_ALLOW_NETWORK"),
        )

    def public_dict(self) -> dict:
        """Thông tin an toàn để in ra CLI/log, không có API key."""
        return {
            "repo_root": str(self.repo_root),
            "posts_dir": str(self.posts_dir),
            "data_dir": str(self.data_dir),
            "ollama_base_url": self.ollama_base_url,
            "ollama_model": self.ollama_model,
            "api_key_set": bool(self.ollama_api_key),
            "request_timeout": self.request_timeout,
            "allow_network": self.allow_network,
        }
