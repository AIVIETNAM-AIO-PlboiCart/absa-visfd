"""Test cho scripts/download_data.py (A). Tự bỏ qua cho tới khi parse_label được viết.

A có thể thêm test, nhưng KHÔNG sửa test có sẵn mà chưa hỏi Leader (đây là đặc tả format).
"""
import pytest

from scripts.download_data import make_id, parse_label
from src.common.labels import ASPECTS, NONE


def _implemented():
    try:
        parse_label("{SCREEN#Positive};")
        return True
    except NotImplementedError:
        return False


needs_impl = pytest.mark.skipif(not _implemented(), reason="parse_label chưa được viết (việc của A)")


def test_make_id():
    assert make_id("val", 1) == "val_00001"
    assert make_id("train", 7786) == "train_07786"


@needs_impl
def test_basic_conversion():
    labels, has_others = parse_label("{SCREEN#Positive};{CAMERA#Negative};{BATTERY#Neutral};")
    assert labels["SCREEN"] == "positive"
    assert labels["CAMERA"] == "negative"
    assert labels["BATTERY"] == "neutral"
    assert set(labels) == set(ASPECTS)
    assert all(labels[a] == NONE for a in ASPECTS if a not in {"SCREEN", "CAMERA", "BATTERY"})
    assert has_others is False


@needs_impl
def test_ser_acc_aspect():
    labels, _ = parse_label("{SER&ACC#Positive};")
    assert labels["SER&ACC"] == "positive"


@needs_impl
def test_others_dropped_and_flagged():
    labels, has_others = parse_label("{OTHERS};")
    assert all(v == NONE for v in labels.values())
    assert has_others is True


@needs_impl
def test_unknown_aspect_raises():
    with pytest.raises(ValueError):
        parse_label("{WIFI#Positive};")


@needs_impl
def test_unknown_sentiment_raises():
    with pytest.raises(ValueError):
        parse_label("{SCREEN#Great};")
