"""Đọc/ghi file gold & pred đúng format (docs/format_spec.md).

Luôn đọc mọi cột dạng chuỗi và KHÔNG để pandas tự đổi "none"/ô trống thành NaN.
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd

from .labels import ASPECTS, GOLD_COLUMNS, PRED_COLUMNS, VALID_VALUES


class FormatError(ValueError):
    """File không đúng format chung."""


def _read(path: str | Path) -> pd.DataFrame:
    return pd.read_csv(path, dtype=str, keep_default_na=False, encoding="utf-8")


def check_columns(df: pd.DataFrame, expected: list[str], path: str | Path) -> None:
    if list(df.columns) != expected:
        missing = [c for c in expected if c not in df.columns]
        extra = [c for c in df.columns if c not in expected]
        raise FormatError(
            f"{path}: sai cột. Thiếu={missing} Thừa={extra}. "
            f"Header phải đúng thứ tự: {','.join(expected)}"
        )


def check_values(df: pd.DataFrame, path: str | Path) -> None:
    if df["id"].duplicated().any():
        dups = df.loc[df["id"].duplicated(), "id"].tolist()[:5]
        raise FormatError(f"{path}: id bị trùng, ví dụ {dups}")
    for col in ASPECTS:
        bad = df.loc[~df[col].isin(VALID_VALUES), ["id", col]]
        if len(bad):
            ex = bad.head(3).to_dict("records")
            raise FormatError(
                f"{path}: cột {col} có {len(bad)} ô ngoài {VALID_VALUES} (kể cả ô trống). Ví dụ: {ex}"
            )


def read_gold(path: str | Path) -> pd.DataFrame:
    df = _read(path)
    check_columns(df, GOLD_COLUMNS, path)
    check_values(df, path)
    return df


def read_pred(path: str | Path) -> pd.DataFrame:
    df = _read(path)
    check_columns(df, PRED_COLUMNS, path)
    check_values(df, path)
    return df


def write_pred(df: pd.DataFrame, path: str | Path) -> None:
    """Ghi file dự đoán: kiểm tra format trước khi ghi, đúng thứ tự cột."""
    df = df[PRED_COLUMNS].astype(str)
    check_values(df, path)
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False, encoding="utf-8")
