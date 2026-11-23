"""Chọn tập con id cho LLM (spec mục 5.8). Người chạy: Leader, sau khi A đã sinh gold_*.csv.

Sinh 2 file (đều được commit):
  data/splits/llm_subset_ids.txt      300 id từ TEST: chấm cuối cùng, so sánh công bằng 4 phương pháp
  data/splits/llm_subset_val_ids.txt  100 id từ VAL : để D thiết kế/thử prompt (KHÔNG thử trên test)

Cách chọn: seed cố định; trước hết đảm bảo mỗi khía cạnh có ít nhất --min-per-aspect
bình luận (STORAGE rất hiếm), phần còn lại chọn ngẫu nhiên.

    python scripts/make_llm_subset.py
    python scripts/make_llm_subset.py --n-test 300 --n-val 100 --seed 42
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.common.config import get_path  # noqa: E402
from src.common.console import setup_console  # noqa: E402
from src.common.io import read_gold  # noqa: E402
from src.common.labels import ASPECTS, NONE  # noqa: E402


def stratified_ids(gold: pd.DataFrame, n: int, seed: int, min_per_aspect: int) -> list[str]:
    if n > len(gold):
        raise ValueError(f"Muốn chọn {n} id nhưng gold chỉ có {len(gold)} dòng")
    shuffled = gold.sample(frac=1, random_state=seed).reset_index(drop=True)
    chosen: list[str] = []
    chosen_set: set[str] = set()

    # 1. Đảm bảo khía cạnh hiếm có mặt: duyệt từ khía cạnh ít nhất đến nhiều nhất
    counts = {a: int((gold[a] != NONE).sum()) for a in ASPECTS}
    for a in sorted(ASPECTS, key=counts.get):
        have = sum((gold.set_index("id").loc[chosen, a] != NONE)) if chosen else 0
        for rid in shuffled.loc[shuffled[a] != NONE, "id"]:
            if have >= min_per_aspect or len(chosen) >= n:
                break
            if rid not in chosen_set:
                chosen.append(rid)
                chosen_set.add(rid)
                have += 1

    # 2. Phần còn lại: ngẫu nhiên
    for rid in shuffled["id"]:
        if len(chosen) >= n:
            break
        if rid not in chosen_set:
            chosen.append(rid)
            chosen_set.add(rid)
    return sorted(chosen)


def report(gold: pd.DataFrame, ids: list[str], label: str) -> None:
    sub = gold[gold["id"].isin(ids)]
    per = ", ".join(f"{a}={int((sub[a] != NONE).sum())}" for a in ASPECTS)
    print(f"{label}: {len(ids)} id | số bình luận có từng khía cạnh: {per}")


def main(argv=None) -> None:
    setup_console()
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--n-test", type=int, default=300)
    p.add_argument("--n-val", type=int, default=100)
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--min-per-aspect", type=int, default=10)
    args = p.parse_args(argv)

    processed, splits = get_path("processed_dir"), get_path("splits_dir")
    splits.mkdir(parents=True, exist_ok=True)
    for split, n, fname in [("test", args.n_test, "llm_subset_ids.txt"),
                            ("val", args.n_val, "llm_subset_val_ids.txt")]:
        gold = read_gold(processed / f"gold_{split}.csv")
        ids = stratified_ids(gold, n, args.seed, args.min_per_aspect)
        out = splits / fname
        if out.exists() and out.read_text(encoding="utf-8").split() != ids:
            sys.exit(f"LỖI: {out} đã tồn tại và khác kết quả mới. Tập con không được đổi sau khi "
                     f"đã chốt; xóa file thủ công nếu thật sự muốn tạo lại.")
        out.write_text("\n".join(ids) + "\n", encoding="utf-8", newline="\n")
        report(gold, ids, str(out))


if __name__ == "__main__":
    main()
