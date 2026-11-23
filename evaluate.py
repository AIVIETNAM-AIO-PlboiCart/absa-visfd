"""Trọng tài duy nhất: chấm mọi file dự đoán theo cùng một cách.

Cách gọi:
    python evaluate.py --gold data/processed/gold_val.csv \
                       --pred predictions/pred_tfidf_val.csv \
                       --name tfidf_val \
                       [--ids data/splits/llm_subset_val_ids.txt] \
                       [--out results/]

Mỗi bình luận là một tập cặp (khía cạnh, cảm xúc), bỏ qua ô `none`.
TP/FP/FN cộng dồn trên toàn tập rồi mới tính P/R/F1 (không trung bình theo bình luận).

  Aspect    : TP khi gold != none và pred != none (không xét cảm xúc).
  Sentiment : chỉ xét ô là TP ở mức Aspect; Accuracy + Macro-F1 trên 3 lớp.
  Joint     : đúng cả khía cạnh và cảm xúc. Đúng khía cạnh nhưng sai cảm xúc = 1 FP + 1 FN.
  Macro     : trung bình theo khía cạnh, BỎ các khía cạnh không xuất hiện trong gold.

Đặc tả đầy đủ: docs/specs/2026-11-23-thiet-ke-repo-absa.md, mục 5.7.
"""
from __future__ import annotations

import argparse
import re
import sys
from datetime import datetime
from pathlib import Path

import pandas as pd

from src.common.console import setup_console
from src.common.io import FormatError, read_gold, read_pred
from src.common.labels import ASPECTS, NONE, PRED_COLUMNS, SENTIMENTS

RESULT_ENCODING = "utf-8-sig"  # có BOM để Excel hiển thị đúng tiếng Việt

SUMMARY_COLUMNS = [
    "name", "gold_file", "pred_file", "subset", "n_reviews", "timestamp",
    "joint_micro_p", "joint_micro_r", "joint_micro_f1", "joint_macro_f1",
    "aspect_micro_p", "aspect_micro_r", "aspect_micro_f1", "aspect_macro_f1",
    "sentiment_acc", "sentiment_macro_f1",
]


# ====================================================================
# Bước 1: đọc + kiểm tra format + ghép theo id
# ====================================================================

def read_ids(path: str | Path) -> list[str]:
    with open(path, encoding="utf-8") as f:
        ids = [line.strip() for line in f if line.strip()]
    if len(ids) != len(set(ids)):
        raise FormatError(f"{path}: danh sách id bị trùng")
    return ids


def align(gold: pd.DataFrame, pred: pd.DataFrame,
          ids: list[str] | None = None) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Lọc theo ids (nếu có), kiểm tra tập id khớp nhau, sắp pred theo đúng thứ tự gold."""
    if ids is not None:
        unknown = sorted(set(ids) - set(gold["id"]))
        if unknown:
            raise FormatError(f"--ids có {len(unknown)} id không có trong gold, ví dụ {unknown[:5]}")
        gold = gold[gold["id"].isin(set(ids))]
        # pred được phép có thêm dòng ngoài tập con (vd. chạy cả test) -> lọc luôn
        pred = pred[pred["id"].isin(set(ids))]

    gold_ids, pred_ids = set(gold["id"]), set(pred["id"])
    missing = sorted(gold_ids - pred_ids)
    extra = sorted(pred_ids - gold_ids)
    if missing:
        raise FormatError(f"pred thiếu {len(missing)} id có trong gold, ví dụ {missing[:5]}")
    if extra:
        raise FormatError(f"pred thừa {len(extra)} id không có trong gold, ví dụ {extra[:5]}")
    if len(gold) == 0:
        raise FormatError("Không có bình luận nào để chấm")

    gold = gold.reset_index(drop=True)
    pred = pred.set_index("id").loc[gold["id"]].reset_index()[PRED_COLUMNS]
    return gold, pred


def load(gold_path, pred_path, ids_path=None) -> tuple[pd.DataFrame, pd.DataFrame]:
    gold = read_gold(gold_path)
    pred = read_pred(pred_path)
    ids = read_ids(ids_path) if ids_path else None
    return align(gold, pred, ids)


# ====================================================================
# Bước 2: tính metric
# ====================================================================

def _prf(tp: int, fp: int, fn: int) -> tuple[float, float, float]:
    p = tp / (tp + fp) if tp + fp else 0.0
    r = tp / (tp + fn) if tp + fn else 0.0
    f = 2 * p * r / (p + r) if p + r else 0.0
    return p, r, f


def compute_metrics(gold: pd.DataFrame, pred: pd.DataFrame) -> dict:
    """gold, pred đã được align (cùng thứ tự id). Trả về overall, per_aspect, skipped_aspects."""
    rows = []
    sent_gold, sent_pred = [], []  # các ô TP ở mức Aspect, để chấm Sentiment

    for a in ASPECTS:
        g = gold[a].to_numpy()
        p = pred[a].to_numpy()
        g_has, p_has = g != NONE, p != NONE

        a_tp = int((g_has & p_has).sum())
        a_fp = int((~g_has & p_has).sum())
        a_fn = int((g_has & ~p_has).sum())

        correct = g_has & (p == g)
        j_tp = int(correct.sum())
        j_fp = int((p_has & ~correct).sum())
        j_fn = int((g_has & ~correct).sum())

        both = g_has & p_has
        sent_gold.extend(g[both])
        sent_pred.extend(p[both])

        ap, ar, af = _prf(a_tp, a_fp, a_fn)
        jp, jr, jf = _prf(j_tp, j_fp, j_fn)
        rows.append({
            "aspect": a, "support": int(g_has.sum()),
            "aspect_tp": a_tp, "aspect_fp": a_fp, "aspect_fn": a_fn,
            "aspect_p": ap, "aspect_r": ar, "aspect_f1": af,
            "joint_tp": j_tp, "joint_fp": j_fp, "joint_fn": j_fn,
            "joint_p": jp, "joint_r": jr, "joint_f1": jf,
        })

    per_aspect = pd.DataFrame(rows)
    present = per_aspect[per_aspect["support"] > 0]
    skipped = per_aspect.loc[per_aspect["support"] == 0, "aspect"].tolist()

    a_p, a_r, a_f = _prf(*(int(per_aspect[f"aspect_{k}"].sum()) for k in ("tp", "fp", "fn")))
    j_p, j_r, j_f = _prf(*(int(per_aspect[f"joint_{k}"].sum()) for k in ("tp", "fp", "fn")))

    overall = {
        "n_reviews": len(gold),
        "joint_micro_p": j_p, "joint_micro_r": j_r, "joint_micro_f1": j_f,
        "joint_macro_f1": float(present["joint_f1"].mean()) if len(present) else 0.0,
        "aspect_micro_p": a_p, "aspect_micro_r": a_r, "aspect_micro_f1": a_f,
        "aspect_macro_f1": float(present["aspect_f1"].mean()) if len(present) else 0.0,
        **_sentiment_metrics(sent_gold, sent_pred),
    }
    return {"overall": overall, "per_aspect": per_aspect, "skipped_aspects": skipped}


def _sentiment_metrics(g: list[str], p: list[str]) -> dict:
    if not g:
        return {"sentiment_acc": 0.0, "sentiment_macro_f1": 0.0}
    acc = sum(x == y for x, y in zip(g, p)) / len(g)
    f1s = []
    for c in SENTIMENTS:
        if c not in g:  # lớp không có trong gold -> bỏ khỏi trung bình (giống macro theo khía cạnh)
            continue
        tp = sum(x == c and y == c for x, y in zip(g, p))
        fp = sum(x != c and y == c for x, y in zip(g, p))
        fn = sum(x == c and y != c for x, y in zip(g, p))
        f1s.append(_prf(tp, fp, fn)[2])
    return {"sentiment_acc": acc, "sentiment_macro_f1": sum(f1s) / len(f1s)}


# ====================================================================
# Bước 4: file lỗi
# ====================================================================

def build_errors(gold: pd.DataFrame, pred: pd.DataFrame) -> pd.DataFrame:
    """Mỗi dòng là một ô sai: MISSED / SPURIOUS / WRONG_SENTIMENT."""
    parts = []
    for a in ASPECTS:
        g, p = gold[a], pred[a]
        wrong = g != p
        if not wrong.any():
            continue
        df = pd.DataFrame({
            "id": gold.loc[wrong, "id"], "text": gold.loc[wrong, "text"],
            "aspect": a, "gold": g[wrong], "pred": p[wrong],
        })
        df["error_type"] = "WRONG_SENTIMENT"
        df.loc[df["pred"] == NONE, "error_type"] = "MISSED"
        df.loc[df["gold"] == NONE, "error_type"] = "SPURIOUS"
        parts.append(df)
    cols = ["id", "text", "aspect", "gold", "pred", "error_type"]
    if not parts:
        return pd.DataFrame(columns=cols)
    return pd.concat(parts).sort_values(["id", "aspect"]).reset_index(drop=True)[cols]


# ====================================================================
# Bước 3: ghi kết quả + in bảng
# ====================================================================

def write_results(res: dict, errors: pd.DataFrame, out: Path, name: str,
                  gold_file: str, pred_file: str, subset: str) -> None:
    out.mkdir(parents=True, exist_ok=True)

    row = {"name": name, "gold_file": gold_file, "pred_file": pred_file, "subset": subset,
           "timestamp": datetime.now().isoformat(timespec="seconds"), **res["overall"]}
    new = pd.DataFrame([row])[SUMMARY_COLUMNS]
    summary_path = out / "summary.csv"
    if summary_path.exists():
        new = pd.concat([pd.read_csv(summary_path, encoding=RESULT_ENCODING), new],
                        ignore_index=True)
    csv_opts = {"index": False, "encoding": RESULT_ENCODING, "lineterminator": "\n"}
    new.round(4).to_csv(summary_path, **csv_opts)
    res["per_aspect"].round(4).to_csv(out / f"per_aspect_{name}.csv", **csv_opts)
    errors.to_csv(out / f"errors_{name}.csv", **csv_opts)


def print_report(res: dict, name: str, subset: str, n_errors: int, out: Path) -> None:
    o = res["overall"]
    print(f"\n=== {name}  |  subset: {subset}  |  {o['n_reviews']} bình luận ===\n")
    print(f"{'Metric':<12}{'Micro-P':>9}{'Micro-R':>9}{'Micro-F1':>10}{'Macro-F1':>10}")
    for k, label in [("joint", "Joint *"), ("aspect", "Aspect")]:
        print(f"{label:<12}{o[k + '_micro_p']:>9.4f}{o[k + '_micro_r']:>9.4f}"
              f"{o[k + '_micro_f1']:>10.4f}{o[k + '_macro_f1']:>10.4f}")
    print(f"{'Sentiment':<12}  accuracy = {o['sentiment_acc']:.4f}   "
          f"macro-F1 = {o['sentiment_macro_f1']:.4f}")
    print("(* metric chính)\n")

    pa = res["per_aspect"]
    print(f"{'Aspect':<13}{'Support':>8}{'Aspect-F1':>11}{'Joint-F1':>10}")
    for r in pa.itertuples():
        print(f"{r.aspect:<13}{r.support:>8}{r.aspect_f1:>11.4f}{r.joint_f1:>10.4f}")

    if res["skipped_aspects"]:
        print(f"\nGhi chú: khía cạnh không có trong gold, đã loại khỏi Macro: "
              f"{', '.join(res['skipped_aspects'])}")
    print(f"\n{n_errors} ô sai -> {out / f'errors_{name}.csv'}")
    print(f"Đã nối kết quả vào {out / 'summary.csv'}\n")


# ====================================================================
# CLI
# ====================================================================

def parse_args(argv=None) -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Chấm điểm file dự đoán ABSA (UIT-ViSFD)")
    p.add_argument("--gold", required=True, help="data/processed/gold_{val,test}.csv")
    p.add_argument("--pred", required=True, help="predictions/pred_<method>.csv")
    p.add_argument("--name", required=True, help="tên phương pháp, vd. tfidf (chữ, số, _ , -)")
    p.add_argument("--ids", default=None, help="file danh sách id để lọc (vd. tập con LLM)")
    p.add_argument("--out", default="results/", help="thư mục ghi kết quả")
    return p.parse_args(argv)


def main(argv=None) -> None:
    setup_console()  # tránh lỗi in tiếng Việt trên console Windows
    args = parse_args(argv)
    if not re.fullmatch(r"[A-Za-z0-9_\-]+", args.name):
        sys.exit("LỖI: --name chỉ được chứa chữ, số, '_' và '-'")
    if "test" in Path(args.gold).name:
        print("NHẮC: đang chấm trên tập TEST. Chỉ làm một lần vào cuối dự án, "
              "không dùng kết quả này để tuning.", file=sys.stderr)

    try:
        gold, pred = load(args.gold, args.pred, args.ids)
    except (FormatError, FileNotFoundError) as e:
        sys.exit(f"LỖI FORMAT: {e}")

    subset = Path(args.ids).stem if args.ids else "all"
    res = compute_metrics(gold, pred)
    errors = build_errors(gold, pred)
    out = Path(args.out)
    write_results(res, errors, out, args.name, Path(args.gold).name, Path(args.pred).name, subset)
    print_report(res, args.name, subset, len(errors), out)


if __name__ == "__main__":
    main()
