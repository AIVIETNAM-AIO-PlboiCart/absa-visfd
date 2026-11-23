# Hướng dẫn đóng góp (cho người mới dùng Git)

## 1. Cài đặt lần đầu

1. Cài Git: https://git-scm.com/downloads. Kiểm tra bằng `git --version`.
2. Khai báo tên và email (chỉ làm một lần):
   ```bash
   git config --global user.name "Tên của bạn"
   git config --global user.email "email-github-cua-ban@example.com"
   ```
3. Chấp nhận lời mời collaborator trên GitHub (kiểm tra email), rồi clone:
   ```bash
   git clone <url-repo>
   cd absa-visfd
   ```
4. Cài môi trường theo `README.md`.

## 2. Quy tắc

- **Không ai push thẳng vào `main`.** Mọi thay đổi đi qua Pull Request (PR) và cần 1 approve.
- Tên nhánh: `<loại>/<người>-<việc>`, ví dụ `feat/a-preprocessing`, `feat/c-phobert-multitask`, `fix/b-tfidf-ngram`, `docs/leader-format-spec`.
- Commit message: `<loại>(<phần>): <mô tả ngắn>`. Loại: `feat`, `fix`, `docs`, `refactor`, `test`.
  Ví dụ: `feat(preprocessing): chuẩn hóa teencode`.
- Chỉ sửa trong thư mục của mình (xem README trong từng thư mục). Muốn sửa thư mục của người khác thì hỏi chủ thư mục trước.

## 3. Vòng làm việc hằng ngày

```bash
git checkout main && git pull                 # 1. lấy bản mới nhất
git checkout -b feat/a-preprocessing          # 2. tạo nhánh mới cho việc này
# ... sửa code ...
git status                                    #    xem mình đã sửa những file nào
git add src/preprocessing/                    # 3. chỉ add đúng thư mục của mình (KHÔNG dùng `git add .`)
git commit -m "feat(preprocessing): chuẩn hóa teencode"
git pull origin main                          # 4. cập nhật main vào nhánh, xử lý conflict nếu có
git push -u origin feat/a-preprocessing       # 5. đẩy lên
```

Sau đó lên GitHub, bấm **Compare & pull request**, điền mô tả, tick checklist rồi chờ review.

- Khi được yêu cầu sửa: sửa tiếp trên cùng nhánh rồi `add`, `commit`, `push`. PR sẽ tự cập nhật.
- Sau khi PR được merge: chạy `git checkout main && git pull`, rồi tạo nhánh mới cho việc tiếp theo.

## 4. Xử lý conflict đơn giản

Khi `git pull origin main` báo `CONFLICT`:

1. Chạy `git status` để xem file nào bị conflict.
2. Mở file đó, tìm đoạn:
   ```
   <<<<<<< HEAD
   (code của bạn)
   =======
   (code trên main)
   >>>>>>> ...
   ```
3. Sửa lại thành phiên bản đúng và **xóa cả 3 dòng đánh dấu**.
4. Chạy `git add <file>` rồi `git commit` (giữ nguyên message mặc định).
5. Nếu không chắc: **dừng lại**, chạy `git merge --abort` và hỏi Leader.

## 5. Lỡ commit nhầm file

- **Mới `add`, chưa commit:** `git restore --staged <file>`.
- **Đã commit nhưng chưa push:** `git reset --soft HEAD~1` (bỏ commit cuối nhưng giữ nguyên thay đổi), rồi add lại cho đúng.
- **Đã push file dữ liệu hoặc model:** `git rm --cached <file>`, commit, push, rồi báo Leader.
- **Đã push token hoặc API key:** **thu hồi (revoke) key ngay** trên trang của nhà cung cấp, tạo key mới, rồi báo Leader. Chỉ xóa khỏi Git là chưa đủ.

## 6. Notebook

Trước khi commit notebook: chọn **Kernel → Restart & Clear Output**, lưu lại, rồi mới `git add`.
Notebook chỉ dùng để khám phá và vẽ biểu đồ; logic cần dùng lại phải nằm trong `src/`.

## 7. Bị kẹt thì hỏi ai

| Vấn đề | Hỏi |
|---|---|
| Git, format file, `evaluate.py`, cấu trúc repo | Leader |
| Dữ liệu, tiền xử lý, tách từ | A |
| TF-IDF, insight | B |
| PhoBERT, model trên HF Hub | C |
| LLM, API, demo | D |

Cặp dự phòng: A ↔ B, C ↔ D.
