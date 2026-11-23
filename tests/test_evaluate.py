"""Test cho evaluate.py (chạy: pytest).

Ví dụ tính tay (spec mục 5.7):
  gold = {PERFORMANCE+, BATTERY+, CAMERA-, PRICE-}
  pred = {PERFORMANCE+, BATTERY-, CAMERA-, DESIGN+}
  -> Aspect F1 = 0.75, Joint F1 = 0.50, Sentiment accuracy = 2/3
"""
import pandas as pd
import pytest

import evaluate
from src.common.io import FormatError
from src.common.labels import ASPECTS, GOLD_COLUMNS, NONE, PRED_COLUMNS


# ---------- helpers ----------

def gold_row(rid, text="x", **labels):
    row = {"id": rid, "text": text, "n_star": "5", "has_others": "0"}
    row.update({a: NONE for a in ASPECTS})
    row.update(_fix(labels))
    return row


def pred_row(rid, **labels):
    row = {"id": rid}
    row.update({a: NONE for a in ASPECTS})
    row.update(_fix(labels))
    return row


def _fix(labels):
    # SER&ACC không viết được làm keyword argument -> dùng SER_ACC
    return {("SER&ACC" if k == "SER_ACC" else k): v for k, v in labels.items()}


def gold_df(*rows):
    return pd.DataFrame(list(rows), columns=GOLD_COLUMNS)


def pred_df(*rows):
    return pd.DataFrame(list(rows), columns=PRED_COLUMNS)


HAND_GOLD = gold_row("t1", PERFORMANCE="positive", BATTERY="positive",
                     CAMERA="negative", PRICE="negative")
HAND_PRED = pred_row("t1", PERFORMANCE="positive", BATTERY="negative",
                     CAMERA="negative", DESIGN="positive")


# ---------- metric ----------

def test_gold_vs_itself_is_perfect():
    g = gold_df(HAND_GOLD, gold_row("t2", SCREEN="neutral", GENERAL="positive"))
    p = g[PRED_COLUMNS].copy()
    m = evaluate.compute_metrics(g, p)["overall"]
    for k in ["aspect_micro_f1", "aspect_macro_f1", "joint_micro_f1",
              "joint_macro_f1", "sentiment_acc", "sentiment_macro_f1"]:
        assert m[k] == pytest.approx(1.0), k


def test_all_none_pred_scores_zero():
    g = gold_df(HAND_GOLD)
    p = pred_df(pred_row("t1"))
    m = evaluate.compute_metrics(g, p)["overall"]
    assert m["aspect_micro_f1"] == 0
    assert m["joint_micro_f1"] == 0
    assert m["aspect_macro_f1"] == 0
    assert m["joint_macro_f1"] == 0


def test_hand_computed_example():
    m = evaluate.compute_metrics(gold_df(HAND_GOLD), pred_df(HAND_PRED))["overall"]
    assert m["aspect_micro_p"] == pytest.approx(0.75)
    assert m["aspect_micro_r"] == pytest.approx(0.75)
    assert m["aspect_micro_f1"] == pytest.approx(0.75)
    assert m["joint_micro_p"] == pytest.approx(0.50)
    assert m["joint_micro_r"] == pytest.approx(0.50)
    assert m["joint_micro_f1"] == pytest.approx(0.50)
    assert m["sentiment_acc"] == pytest.approx(2 / 3)


def test_empty_gold_and_pred_do_not_change_score():
    base = evaluate.compute_metrics(gold_df(HAND_GOLD), pred_df(HAND_PRED))["overall"]
    more = evaluate.compute_metrics(
        gold_df(HAND_GOLD, gold_row("t2"), gold_row("t3")),
        pred_df(HAND_PRED, pred_row("t2"), pred_row("t3")),
    )["overall"]
    for k, v in base.items():
        if k != "n_reviews":
            assert more[k] == pytest.approx(v), k


def test_row_order_does_not_matter():
    g = gold_df(HAND_GOLD, gold_row("t2", SCREEN="positive"))
    p1 = pred_df(HAND_PRED, pred_row("t2", SCREEN="positive"))
    p2 = p1.iloc[::-1].reset_index(drop=True)
    m1 = evaluate.compute_metrics(*evaluate.align(g, p1))["overall"]
    m2 = evaluate.compute_metrics(*evaluate.align(g, p2))["overall"]
    assert m1 == m2


def test_macro_skips_aspects_absent_from_gold():
    # Gold chỉ có CAMERA; pred đúng CAMERA -> macro chỉ tính trên CAMERA = 1.0
    g = gold_df(gold_row("t1", CAMERA="positive"))
    p = pred_df(pred_row("t1", CAMERA="positive"))
    res = evaluate.compute_metrics(g, p)
    assert res["overall"]["aspect_macro_f1"] == pytest.approx(1.0)
    assert "STORAGE" in res["skipped_aspects"]


def test_errors_types():
    errs = evaluate.build_errors(gold_df(HAND_GOLD), pred_df(HAND_PRED))
    got = {(r.aspect, r.error_type) for r in errs.itertuples()}
    assert got == {("BATTERY", "WRONG_SENTIMENT"), ("PRICE", "MISSED"),
                   ("DESIGN", "SPURIOUS")}
    assert list(errs.columns) == ["id", "text", "aspect", "gold", "pred", "error_type"]


# ---------- kiểm tra format ----------

def test_missing_rows_raise():
    g = gold_df(HAND_GOLD, gold_row("t2"))
    with pytest.raises(FormatError, match="thiếu"):
        evaluate.align(g, pred_df(HAND_PRED))


def test_extra_rows_raise():
    with pytest.raises(FormatError, match="thừa"):
        evaluate.align(gold_df(HAND_GOLD), pred_df(HAND_PRED, pred_row("t9")))


def _write(tmp_path, g, p):
    gp, pp = tmp_path / "gold.csv", tmp_path / "pred.csv"
    g.to_csv(gp, index=False)
    p.to_csv(pp, index=False)
    return gp, pp


def test_duplicate_ids_raise(tmp_path):
    gp, pp = _write(tmp_path, gold_df(HAND_GOLD), pred_df(HAND_PRED, HAND_PRED))
    with pytest.raises(FormatError, match="trùng"):
        evaluate.load(gp, pp)


def test_invalid_value_raises(tmp_path):
    bad = dict(HAND_PRED, CAMERA="Negative")
    gp, pp = _write(tmp_path, gold_df(HAND_GOLD), pred_df(bad))
    with pytest.raises(FormatError):
        evaluate.load(gp, pp)


def test_empty_cell_raises(tmp_path):
    bad = dict(HAND_PRED, CAMERA="")
    gp, pp = _write(tmp_path, gold_df(HAND_GOLD), pred_df(bad))
    with pytest.raises(FormatError):
        evaluate.load(gp, pp)


def test_wrong_columns_raise(tmp_path):
    p = pred_df(HAND_PRED).drop(columns=["CAMERA"])
    gp, pp = _write(tmp_path, gold_df(HAND_GOLD), p)
    with pytest.raises(FormatError, match="sai cột"):
        evaluate.load(gp, pp)


# ---------- lọc theo --ids và chạy CLI end-to-end ----------

def test_ids_filter(tmp_path):
    g = gold_df(HAND_GOLD, gold_row("t2", SCREEN="positive"))
    p = pred_df(HAND_PRED)  # pred chỉ có t1 (giống LLM chạy trên tập con)
    gp, pp = _write(tmp_path, g, p)
    ids = tmp_path / "ids.txt"
    ids.write_text("t1\n", encoding="utf-8")
    gold, pred = evaluate.load(gp, pp, ids)
    assert list(gold["id"]) == ["t1"]
    assert evaluate.compute_metrics(gold, pred)["overall"]["joint_micro_f1"] == pytest.approx(0.5)


def test_ids_not_in_gold_raise(tmp_path):
    gp, pp = _write(tmp_path, gold_df(HAND_GOLD), pred_df(HAND_PRED))
    ids = tmp_path / "ids.txt"
    ids.write_text("t1\nkhong_ton_tai\n", encoding="utf-8")
    with pytest.raises(FormatError, match="không có trong gold"):
        evaluate.load(gp, pp, ids)


def test_cli_writes_outputs(tmp_path):
    gp, pp = _write(tmp_path, gold_df(HAND_GOLD), pred_df(HAND_PRED))
    out = tmp_path / "results"
    evaluate.main(["--gold", str(gp), "--pred", str(pp), "--name", "demo", "--out", str(out)])
    evaluate.main(["--gold", str(gp), "--pred", str(pp), "--name", "demo2", "--out", str(out)])

    summary = pd.read_csv(out / "summary.csv", encoding="utf-8-sig")
    assert list(summary["name"]) == ["demo", "demo2"]  # nối thêm, không ghi đè
    assert summary.loc[0, "joint_micro_f1"] == pytest.approx(0.5)

    per = pd.read_csv(out / "per_aspect_demo.csv", encoding="utf-8-sig")
    assert set(per["aspect"]) == set(ASPECTS)

    errs = pd.read_csv(out / "errors_demo.csv", encoding="utf-8-sig")
    assert len(errs) == 3


def test_cli_bad_format_exits_nonzero(tmp_path):
    bad = dict(HAND_PRED, CAMERA="")
    gp, pp = _write(tmp_path, gold_df(HAND_GOLD), pred_df(bad))
    with pytest.raises(SystemExit) as e:
        evaluate.main(["--gold", str(gp), "--pred", str(pp), "--name", "x",
                       "--out", str(tmp_path / "r")])
    assert e.value.code != 0
