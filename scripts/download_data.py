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
import io
import pandas as pd
import urllib.request
import zipfile

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.common.config import get_path  # noqa: E402,F401
from src.common.console import setup_console  # noqa: E402
from src.common.io import write_gold  # noqa: E402,F401
from src.common.labels import ASPECTS, NONE, SENTIMENTS  # noqa: E402,F401

EXPECTED_ROWS = {"train": 7786, "dev": 1112, "test": 2224}
SPLIT_RENAME = {"train": "train", "dev": "val", "test": "test"}

TAG_RE = re.compile(r"\{([^{}]*)\}")

RAW_URL = "https://github.com/LuongPhan/UIT-ViSFD/raw/main/UIT-ViSFD.zip"
RAW_FILES = {"train": "Train.csv", "dev": "Dev.csv", "test": "Test.csv"}


def make_id(split: str, row_number: int) -> str:
    """row_number: thứ tự dòng trong file gốc, ĐẾM TỪ 1 (dòng dữ liệu đầu tiên = 1).

    >>> make_id("val", 1)
    'val_00001'
    """
    return f"{split}_{row_number:05d}"


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
        
        aspect, sentiment = tag.split("#", 1)
        sentiment = sentiment.lower()

        if aspect not in result:
            raise ValueError(f"Khía cạnh lạ: {aspect!r}")
        if sentiment not in SENTIMENTS:
            raise ValueError(f"Cảm xúc lạ: {sentiment!r}")
        if result[aspect] not in (NONE, sentiment):
            raise ConflictError(f"{aspect} có 2 cảm xúc: {result[aspect]} và {sentiment}")

        result[aspect] = sentiment
    
    return (result, has_others)


def download_raw(raw_dir: Path) -> None:
    raw_dir.mkdir(parents=True, exist_ok=True)

    if all((raw_dir / name).exists() for name in RAW_FILES.values()):
        return

    print(f"Đang tải {RAW_URL} ...")
    try:
        with urllib.request.urlopen(RAW_URL, timeout=60) as response:
            data = response.read()
    except OSError as e:
        raise SystemExit(f"Không tải được dữ liệu ({e}). Kiểm tra kết nối mạng.")

    with zipfile.ZipFile(io.BytesIO(data)) as zf:
        for name in RAW_FILES.values():
            member = next((m for m in zf.namelist() if Path(m).name == name), None)
            if member is None:
                raise SystemExit(f"Không thấy {name} trong file zip.")
            (raw_dir / name).write_bytes(zf.read(member))
    print(f"Đã giải nén {len(RAW_FILES)} file vào {raw_dir}")


def load_raw(raw_dir: Path, split: str) -> pd.DataFrame:
    df = pd.read_csv(raw_dir / RAW_FILES[split])
    if len(df) != EXPECTED_ROWS[split]:
        raise SystemExit(f"{split}: chỉ có {len(df)} dòng, phải có {EXPECTED_ROWS[file_name]}!")
    return df


def convert_split(df: pd.DataFrame, split: str):
    out_split = SPLIT_RENAME[split]
    
    rows = []
    conflict_ids = []

    for idx, row in enumerate(df.itertuples(index=False), start=1):
        row_id = make_id(out_split, idx)
        try:
            aspects, has_others = parse_label(row.label)
        except ConflictError:
            conflict_ids.append(row_id)
            continue

        rec = {
            "id": row_id,
            "text": row.comment,
            "n_star": row.n_star,
            "has_others": int(has_others),
        }
        for a in ASPECTS:
            rec[a] = aspects[a]
        rows.append(rec)

    return pd.DataFrame(rows), conflict_ids


def print_stats(split: str, gold: pd.DataFrame, conflict_ids: list) -> None:
    print(f"\n=== {SPLIT_RENAME[split]} ({len(gold)} dòng) ===")
    print("Số nhãn mỗi khía cạnh (positive / negative / neutral):")
    for a in ASPECTS:
        c = gold[a].value_counts()
        print(f"  {a:12s} {c.get('positve', 0):5d} / {c.get('negative', 0):5d} / {c.get('neutral', 0):5d}")
    only_others = int(((gold["has_others"] == 1) & (gold[ASPECTS] == NONE).all(axis=1)).sum())
    print(f"Bình luận chỉ có OTHERS: {only_others}")
    print(f"Khía cạnh có 2 cảm xúc khác nhau: {len(conflict_ids)} {conflict_ids[:5]}")


def main() -> None:
    setup_console()        
    raw_dir = get_path("raw_dir")
    processed_dir = get_path("processed_dir")

    download_raw(raw_dir)

    results, total_conflicts = {}, 0
    for split in RAW_FILES:
        df = load_raw(raw_dir, split)
        gold, conflict_ids = convert_split(df, split)
        print_stats(split, gold, conflict_ids)
        total_conflicts += len(conflict_ids)
        results[split] = gold

    if total_conflicts:
        raise SystemExit(
            f"\nCó {total_conflicts} dòng xung dột nhãn."
        )

    processed_dir.mkdir(parents=True, exist_ok=True)
    for split, gold in results.items():
        write_gold(gold, processed_dir / f"gold_{SPLIT_RENAME[split]}.csv")
    print(f"\nĐã ghi 3 file gold vào {processed_dir}")


if __name__ == "__main__":
    main()
