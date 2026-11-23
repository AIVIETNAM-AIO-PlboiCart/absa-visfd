"""Test cho src/common/io.py và scripts/make_llm_subset.py."""
import pandas as pd
import pytest

from scripts.make_llm_subset import stratified_ids
from src.common.io import FormatError, read_gold, write_gold
from src.common.labels import ASPECTS, GOLD_COLUMNS, NONE


def _gold(n, storage_every=None):
    rows = []
    for i in range(n):
        r = {"id": f"test_{i + 1:05d}", "text": "Pin trâu, máy mượt", "n_star": "5",
             "has_others": "0", **{a: NONE for a in ASPECTS}}
        r["BATTERY"] = "positive"
        if storage_every and i % storage_every == 0:
            r["STORAGE"] = "negative"
        rows.append(r)
    return pd.DataFrame(rows, columns=GOLD_COLUMNS)


def test_write_gold_roundtrip(tmp_path):
    g = _gold(3)
    write_gold(g, tmp_path / "gold.csv")
    back = read_gold(tmp_path / "gold.csv")
    assert back.equals(g)
    assert b"\r\n" not in (tmp_path / "gold.csv").read_bytes()


def test_write_gold_rejects_bad_has_others(tmp_path):
    g = _gold(2)
    g.loc[0, "has_others"] = "yes"
    with pytest.raises(FormatError, match="has_others"):
        write_gold(g, tmp_path / "gold.csv")


def test_write_gold_rejects_missing_column(tmp_path):
    with pytest.raises(FormatError, match="thiếu cột"):
        write_gold(_gold(2).drop(columns=["n_star"]), tmp_path / "gold.csv")


def test_subset_is_deterministic_and_covers_rare_aspect():
    g = _gold(1000, storage_every=100)  # chỉ 10 bình luận có STORAGE
    a = stratified_ids(g, 50, seed=42, min_per_aspect=5)
    b = stratified_ids(g, 50, seed=42, min_per_aspect=5)
    assert a == b and len(a) == 50 and len(set(a)) == 50
    sub = g[g["id"].isin(a)]
    assert (sub["STORAGE"] != NONE).sum() >= 5


def test_subset_too_large_raises():
    with pytest.raises(ValueError):
        stratified_ids(_gold(5), 10, seed=0, min_per_aspect=1)
