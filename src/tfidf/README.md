# Baseline TF-IDF + LR/SVM

**Chủ thư mục:** B

Mỗi khía cạnh một classifier 4 lớp (positive/negative/neutral/none). Ghi lại các cấu hình đã thử. Output: `predictions/pred_tfidf[_<cấu hình>]_val.csv` (tuning), `pred_tfidf_test.csv` (cấu hình tốt nhất, cuối dự án).

Model đã train (`.joblib`) lưu vào `models/` (bị ignore), KHÔNG lưu trong `src/`. Nếu cần chia sẻ: đẩy lên HF Hub (repo riêng trong organization của nhóm), ghim theo tag.

Muốn sửa thư mục này mà không phải chủ: mở PR và cần chủ thư mục đồng ý.
