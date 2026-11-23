# Fine-tune PhoBERT / ViSoBERT

**Chủ thư mục:** C

Multi-task: 10 head, mỗi head phân loại 4 lớp. Class model đặt ở `model.py`, kế thừa `PyTorchModelHubMixin` (D import lại cho demo). Checkpoint push lên HF Hub, ghim theo tag. Output: `predictions/pred_phobert_val.csv`, `pred_phobert_test.csv`.

Đẩy/tải model, token, tag: xem [`docs/huggingface.md`](../../docs/huggingface.md).

Muốn sửa thư mục này mà không phải chủ: mở PR và cần chủ thư mục đồng ý.
