# File dự đoán

**Chủ:** mỗi người ghi file của phương pháp mình.

## Tên file

```
pred_<method>[_<cấu hình>]_<split>.csv
```

| Ví dụ | Ý nghĩa |
|---|---|
| `pred_tfidf_val.csv` | TF-IDF, cấu hình mặc định, trên val (dùng khi tuning) |
| `pred_tfidf_bigram_val.csv` | TF-IDF, cấu hình `bigram`, trên val |
| `pred_phobert_test.csv` | PhoBERT, trên test (chỉ sinh **một lần**, vào cuối dự án) |
| `pred_llm_zeroshot_test.csv` | LLM zero-shot, trên tập con test (`llm_subset_ids.txt`) |

`<split>` là `val` hoặc `test`. Thiếu phần split thì không biết phải chấm với gold nào.

## Format

Xem `docs/format_spec.md` mục 4. Ghi bằng `src.common.io.write_pred` để được kiểm tra format trước khi lưu.

## Commit

File `pred_*.csv` **được commit** (nhẹ, là sản phẩm bàn giao). Kết quả chấm trong `results/` thì **không** commit.
