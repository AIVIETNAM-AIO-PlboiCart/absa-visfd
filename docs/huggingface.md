# Hugging Face Hub: lưu và tải model

Nguyên tắc: **code lên GitHub, model lên Hugging Face Hub.** Không commit checkpoint vào Git.

- Organization của nhóm: `absa-visfd-team`
- Repo model PhoBERT: `absa-visfd-team/phobert-absa-visfd` (private), cấu hình ở `configs/paths.yaml`

## 1. Quyền (Leader đã cài)

| Người | Quyền trong organization | Dùng để |
|---|---|---|
| Leader | admin | quản lý organization |
| C | write | đẩy checkpoint, gắn tag |
| D | read | tải model về làm API/demo |
| A, B | read (B được nâng lên write nếu cần đẩy model TF-IDF) | — |

## 2. Mỗi người tự tạo token (làm một lần)

1. Đăng nhập https://huggingface.co, bấm avatar → **Settings → Access Tokens → Create new token**.
2. Chọn loại token: **Write** nếu bạn là C, **Read** với những người còn lại.
3. Copy token vào file `.env` ở gốc repo (file này đã bị ignore, không bao giờ commit):
   ```
   HF_TOKEN=hf_xxxxxxxxxxxxxxxx
   ```
4. **Không** gửi token qua chat. Mỗi người dùng token của riêng mình. Lỡ để lộ token thì vào lại trang đó, bấm **Invalidate**, rồi tạo token mới.

## 3. Kiểm tra truy cập

Kích hoạt venv rồi chạy:
```bash
python -c "from src.common.config import get_secret, get_setting; from huggingface_hub import HfApi; print(HfApi(token=get_secret('HF_TOKEN')).model_info(get_setting('hf_model_repo')).id)"
```

| Kết quả | Ý nghĩa |
|---|---|
| In ra `absa-visfd-team/phobert-absa-visfd` | Thành công |
| `RuntimeError: Thiếu biến HF_TOKEN` | Chưa có `.env` hoặc chưa điền token |
| `RepositoryNotFoundError` / 404 | Chưa được mời vào organization, hoặc chưa chấp nhận lời mời |
| `401 Unauthorized` | Token sai hoặc đã bị vô hiệu |

## 4. Đẩy model lên (C)

- Class model đặt ở `src/phobert/model.py`, kế thừa `huggingface_hub.PyTorchModelHubMixin` để lưu và tải được cả 10 head.
- **Không** dùng `AutoModel.from_pretrained` trơn, vì cách này nạp head ngẫu nhiên mà không báo lỗi.
- Tokenizer đẩy lên cùng repo.
- Mỗi bản dùng được thì gắn tag, và ghi trong message mã commit Git của code đã train:

```python
from huggingface_hub import HfApi
from src.common.config import get_secret, get_setting

repo = get_setting("hf_model_repo")
model.push_to_hub(repo, token=get_secret("HF_TOKEN"))
tokenizer.push_to_hub(repo, token=get_secret("HF_TOKEN"))
HfApi(token=get_secret("HF_TOKEN")).create_tag(repo, tag="v0.1", tag_message="code: <git commit hash>")
```

Sau đó mở PR, cập nhật `hf_model_revision: "v0.1"` trong `configs/paths.yaml`.

## 5. Tải model về (D, Leader)

**Luôn ghim theo tag**, không đọc bản mới nhất:
```python
from src.common.config import get_secret, get_setting
from src.phobert.model import <TenClassModel>

model = <TenClassModel>.from_pretrained(
    get_setting("hf_model_repo"),
    revision=get_setting("hf_model_revision"),
    token=get_secret("HF_TOKEN"),
)
```
Bước tiền xử lý và tách từ lúc suy luận phải gọi đúng module `src/preprocessing/` như lúc train.
