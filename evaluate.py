"""Trọng tài duy nhất: chấm mọi file dự đoán theo cùng một cách.

Cách gọi:
    python evaluate.py --gold data/processed/gold_val.csv \
                       --pred predictions/pred_tfidf.csv \
                       --name tfidf \
                       [--ids data/splits/llm_subset_ids.txt] \
                       [--out results/]

Đặc tả đầy đủ: docs/specs/2026-11-23-thiet-ke-repo-absa.md, mục 5.7.
TODO (Leader):
  1. Kiểm tra format (src.common.io) + ghép theo id, lọc theo --ids.
  2. Tính Aspect / Sentiment / Joint (micro + macro, cộng dồn TP/FP/FN trên toàn tập).
  3. Nối dòng vào results/summary.csv, ghi results/per_aspect_<name>.csv, in bảng.
  4. Ghi results/errors_<name>.csv (MISSED / SPURIOUS / WRONG_SENTIMENT).
"""
import argparse


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Chấm điểm file dự đoán ABSA (UIT-ViSFD)")
    p.add_argument("--gold", required=True, help="data/processed/gold_{val,test}.csv")
    p.add_argument("--pred", required=True, help="predictions/pred_<method>.csv")
    p.add_argument("--name", required=True, help="tên phương pháp, vd. tfidf")
    p.add_argument("--ids", default=None, help="file danh sách id để lọc (vd. tập con LLM)")
    p.add_argument("--out", default="results/", help="thư mục ghi kết quả")
    return p.parse_args()


def main() -> None:
    args = parse_args()
    raise NotImplementedError("evaluate.py chưa được viết — xem TODO ở đầu file.")


if __name__ == "__main__":
    main()
