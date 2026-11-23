# Quy ước format và nhãn

> Tài liệu chính thức. Danh sách nhãn trong code: `src/common/labels.py` (nguồn duy nhất).
> Đọc/ghi file: dùng `src/common/io.py` (`read_gold`, `read_pred`, `write_pred`).

## 1. Nhãn

| Khía cạnh (cột) | Tiếng Việt |
|---|---|
| SCREEN | Màn hình |
| CAMERA | Camera |
| FEATURES | Tính năng |
| BATTERY | Pin |
| PERFORMANCE | Hiệu năng |
| STORAGE | Bộ nhớ |
| DESIGN | Thiết kế |
| PRICE | Giá |
| GENERAL | Đánh giá chung |
| SER&ACC | Dịch vụ & phụ kiện |

Giá trị mỗi ô: `positive`, `negative`, `neutral`, hoặc `none` (khía cạnh không được nhắc đến).

## 2. Chuyển nhãn gốc `{ASPECT#Polarity};...`

- `Positive` / `Negative` / `Neutral` → chữ thường.
- Khía cạnh không xuất hiện → `none`.
- **Bỏ tag `{OTHERS}`** (đã chốt). Bình luận chỉ có OTHERS → 10 ô `none`, cột phụ `has_others = 1`. Cột này không dùng để chấm.
- Một khía cạnh có 2 cảm xúc khác nhau trong cùng bình luận: **CHƯA CHỐT**, chờ số liệu EDA của A.
- Tag lạ (khía cạnh ngoài danh sách) → script **báo lỗi**, không bỏ qua.

## 3. File gold: `data/processed/gold_{train,val,test}.csv`

```
id,text,n_star,has_others,SCREEN,CAMERA,FEATURES,BATTERY,PERFORMANCE,STORAGE,DESIGN,PRICE,GENERAL,SER&ACC
```

`text` là văn bản **gốc**, chưa tiền xử lý.

## 4. File dự đoán: `predictions/pred_<method>[_<cấu hình>]_<split>.csv`

```
id,SCREEN,CAMERA,FEATURES,BATTERY,PERFORMANCE,STORAGE,DESIGN,PRICE,GENERAL,SER&ACC
```

`<split>` là `val` hoặc `test`, ví dụ `pred_tfidf_val.csv`, `pred_phobert_test.csv`. Xem thêm `predictions/README.md`.

Ví dụ với bình luận "Máy chạy mượt, pin trâu nhưng camera chụp đêm tệ, giá hơi chát":

```
id,SCREEN,CAMERA,FEATURES,BATTERY,PERFORMANCE,STORAGE,DESIGN,PRICE,GENERAL,SER&ACC
test_00001,none,negative,none,positive,positive,none,none,negative,none,none
```

## 5. Quy tắc chung

- UTF-8, dấu phẩy, header đúng thứ tự như trên.
- Gold và pred được ghép **theo `id`**, không theo thứ tự dòng.
- `id` = `<split>_<số thứ tự dòng trong file gốc, ĐẾM TỪ 1, 5 chữ số>`, ví dụ `train_00001`, `val_00001`, `test_00001`. Split `dev` của dataset gốc được đổi tên thành `val`. Id sinh một lần trong `scripts/download_data.py`, không bao giờ đổi.
- **Ô trống hoặc NaN là lỗi format.** Không có khía cạnh thì ghi `none`.

## 6. Quyết định chờ chốt

| # | Vấn đề | Ai cung cấp số liệu / đề xuất | Ai chốt | Trạng thái |
|---|---|---|---|---|
| 1 | Một khía cạnh có 2 cảm xúc khác nhau trong cùng bình luận | A đếm số trường hợp (in ra khi chạy `download_data.py`) | Leader | Chờ số liệu |
| 2 | Bộ tách từ cho PhoBERT (`py_vncorenlp`/VnCoreNLP hay `underthesea`) | A và C cùng thử | A + C, báo Leader | Chờ A và C |
| 3 | Quy tắc chuẩn hóa teencode và dấu | A | A, báo C | Chờ A |

Khi chốt xong: sửa bảng này, ghi quy tắc vào mục tương ứng, rồi cập nhật `requirements.txt` nếu có thêm thư viện.
