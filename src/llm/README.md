# LLM zero-shot / few-shot

**Chủ thư mục:** D

Prompt đặt ở `prompts/`. API key đọc từ `.env`.

- **Thiết kế và thử prompt:** chỉ dùng `data/splits/llm_subset_val_ids.txt` (100 id từ val). Output: `pred_llm_<kiểu prompt>_val.csv`.
- **Chấm cuối:** chạy một lần trên `data/splits/llm_subset_ids.txt` (300 id từ test). Output: `pred_llm_<kiểu prompt>_test.csv`.
- **Không chỉnh prompt dựa trên kết quả test.**

Leader sinh 2 file id bằng `scripts/make_llm_subset.py` sau khi A có dữ liệu gold.
Chấm: `python evaluate.py --gold data/processed/gold_val.csv --pred predictions/pred_llm_zeroshot_val.csv --name llm_zeroshot_val --ids data/splits/llm_subset_val_ids.txt`

Muốn sửa thư mục này mà không phải chủ: mở PR và cần chủ thư mục đồng ý.
