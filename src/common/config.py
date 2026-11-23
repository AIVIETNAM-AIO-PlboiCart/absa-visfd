"""Đọc configs/paths.yaml + .env. Biến môi trường ABSA_<KHÓA> ghi đè giá trị trong YAML.

Ví dụ:
    from src.common.config import get_path, get_setting
    gold_val = get_path("processed_dir") / "gold_val.csv"
"""
from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path

import yaml
from dotenv import load_dotenv

REPO_ROOT = Path(__file__).resolve().parents[2]
CONFIG_FILE = REPO_ROOT / "configs" / "paths.yaml"

load_dotenv(REPO_ROOT / ".env")


@lru_cache(maxsize=1)
def _load_yaml() -> dict:
    with open(CONFIG_FILE, encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def get_setting(key: str, default: str | None = None) -> str | None:
    """Giá trị cấu hình: ưu tiên biến môi trường ABSA_<KEY>, sau đó paths.yaml."""
    env_val = os.environ.get(f"ABSA_{key.upper()}")
    if env_val:
        return env_val
    val = _load_yaml().get(key, default)
    return val if val != "" else default


def get_path(key: str) -> Path:
    """Đường dẫn tuyệt đối; đường dẫn tương đối được tính từ gốc repo."""
    val = get_setting(key)
    if val is None:
        raise KeyError(f"Không có khóa '{key}' trong {CONFIG_FILE} hoặc biến ABSA_{key.upper()}")
    p = Path(val)
    return p if p.is_absolute() else REPO_ROOT / p


def get_secret(name: str) -> str:
    """Đọc token/API key từ .env (vd. HF_TOKEN, LLM_API_KEY). Báo lỗi nếu thiếu."""
    val = os.environ.get(name)
    if not val:
        raise RuntimeError(f"Thiếu biến {name}. Sao chép .env.example thành .env và điền giá trị.")
    return val
