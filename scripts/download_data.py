"""Tải UIT-ViSFD và sinh data/processed/gold_{train,val,test}.csv.

Đặc tả: docs/specs/2026-11-23-thiet-ke-repo-absa.md mục 5.3–5.4, docs/format_spec.md.
Người viết: (chốt khi giao việc — Leader hoặc A)

TODO:
  1. Tải từ github.com/LuongPhan/UIT-ViSFD; nếu lỗi dùng HF `visolex/ViSFD` (tách split theo cột `type`).
  2. Kiểm tra số dòng: train 7786, dev 1112, test 2224 — sai thì dừng.
  3. Chuyển nhãn {ASPECT#Polarity} sang format rộng; bỏ OTHERS (cột has_others); tag lạ -> báo lỗi.
  4. Sinh id `<split>_<5 chữ số>` (dev -> val), ghi 3 file gold bằng text GỐC.
  5. In thống kê: số nhãn mỗi khía cạnh, số bình luận chỉ có OTHERS.
"""


def main() -> None:
    raise NotImplementedError("download_data.py chưa được viết — xem TODO ở đầu file.")


if __name__ == "__main__":
    main()
