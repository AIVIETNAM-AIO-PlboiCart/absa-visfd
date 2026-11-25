"""Tải UIT-ViSFD và sinh data/processed/gold_{train,val,test}.csv.

Người viết: A.   Reviewer: Leader.
Đặc tả: docs/format_spec.md (mục 2, 3, 5) + docs/specs/2026-11-23-thiet-ke-repo-absa.md mục 5.4.

Chạy:  python scripts/download_data.py
Test:  pytest tests/test_download_data.py   (test tự bỏ qua cho tới khi parse_label được viết)

Các bước cần làm:
  1. Tải 3 file từ nguồn gốc github.com/LuongPhan/UIT-ViSFD vào data/raw/
     (get_path("raw_dir")). Nếu không tải được: dùng bản HF `visolex/ViSFD`, tách split theo cột `type`.
  2. Kiểm tra số dòng: train 7786, dev 1112, test 2224 (EXPECTED_ROWS). Sai -> dừng, báo lỗi.
  3. Chuyển nhãn từng dòng bằng parse_label(); sinh id bằng make_id(); split `dev` đổi tên thành `val`.
  4. Ghi bằng src.common.io.write_gold (tự kiểm tra format). text là văn bản GỐC, không tiền xử lý.
  5. In thống kê: số nhãn mỗi khía cạnh, số bình luận chỉ có OTHERS,
     số trường hợp một khía cạnh có 2 cảm xúc (để Leader chốt quy tắc — format_spec mục 6).
"""
from __future__ import annotations

import sys
import re
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.common.config import get_path  # noqa: E402,F401
from src.common.console import setup_console  # noqa: E402
from src.common.io import write_gold  # noqa: E402,F401
from src.common.labels import ASPECTS, NONE  # noqa: E402,F401

EXPECTED_ROWS = {"train": 7786, "dev": 1112, "test": 2224}
SPLIT_RENAME = {"train": "train", "dev": "val", "test": "test"}


def make_id(split: str, row_number: int) -> str:
    """row_number: thứ tự dòng trong file gốc, ĐẾM TỪ 1 (dòng dữ liệu đầu tiên = 1).

    >>> make_id("val", 1)
    'val_00001'
    """
    return f"{split}_{row_number:05d}"


TAG_RE = re.compile(r"\{([^{}]*)\}")
VALID_SENTIMENTS = {"positive", "negative", "neutral"}


class ConflictError(ValueError):
    "Một khía cạnh có 2 cảm xúc khác nhau trong cùng bình luận."


def parse_label(label: str) -> tuple[dict[str, str], bool]:
    """Chuyển nhãn gốc sang dict 10 khía cạnh + cờ has_others.

    >>> parse_label("{SCREEN#Positive};{CAMERA#Negative};{OTHERS};")
    ({'SCREEN': 'positive', 'CAMERA': 'negative', 'FEATURES': 'none', ...}, True)

    Quy tắc (format_spec mục 2):
      - Positive/Negative/Neutral -> chữ thường; khía cạnh không xuất hiện -> "none".
      - {OTHERS} bị bỏ, chỉ bật cờ has_others = True.
      - Khía cạnh hoặc cảm xúc lạ -> raise ValueError (KHÔNG bỏ qua âm thầm).
      - Một khía cạnh có 2 cảm xúc khác nhau: CHƯA CHỐT -> tạm thời raise ValueError
        để đếm số trường hợp; Leader chốt quy tắc sau khi có số liệu.
    """
    if not isinstance(label, str):
        raise ValueError(f"label không phải là chuỗi: {label!r}")

    result = {aspect: NONE for aspect in ASPECTS}
    has_others = False

    for tag in TAG_RE.findall(label):
        if tag == "OTHERS":
            has_others = True
            continue

        if "#" not in tag:
            raise ValueError(f"Tag sai dạng (thiếu #): {tag!r}")
        print(repr(tag))
        aspect, sentiment = tag.split("#", 1)
        sentiment = sentiment.lower()

        if aspect not in result:
            raise ValueError(f"Khía cạnh lạ: {aspect!r}")
        if sentiment not in VALID_SENTIMENTS:
            raise ValueError(f"Cảm xúc lạ: {sentiment!r}")
        if result[aspect] not in (NONE, sentiment):
            raise ConflictError(f"{aspect} có 2 cảm xúc: {result[aspect]} và {sentiment}")

        result[aspect] = sentiment
    
    return (result, has_others)


def main() -> None:
    setup_console()
    raise NotImplementedError("download_data.py chưa được viết — xem các bước ở đầu file.")


if __name__ == "__main__":
    main()
