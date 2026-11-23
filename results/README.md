# Kết quả chấm

**Chủ:** Leader. Thư mục này **không được commit** (đã có trong `.gitignore`), chỉ có file README này.

`evaluate.py` ghi vào đây:

| File | Nội dung |
|---|---|
| `summary.csv` | Mỗi lần chạy nối thêm một dòng metric |
| `per_aspect_<name>.csv` | Metric theo từng khía cạnh |
| `errors_<name>.csv` | Các ô sai, dùng cho error analysis |

**Vì sao không commit?**
- Ai chạy `evaluate.py` cũng sửa `summary.csv`, nên nếu commit thì PR nào cũng bị conflict.
- `errors_*.csv` chứa nguyên văn bình luận của dataset (license chưa rõ).

**Cách báo kết quả:** dán bảng mà `evaluate.py` in ra vào mô tả PR (PR template có sẵn mục này).
Leader chạy lại `evaluate.py` trên mọi file `predictions/pred_*.csv` để tổng hợp bảng cuối.
