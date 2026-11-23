# ABSA cho bình luận điện thoại tiếng Việt (UIT-ViSFD)

**Aspect-Based Sentiment Analysis for Vietnamese Smartphone Reviews using Fine-tuned Pre-trained Language Models**

Input: một bình luận tiếng Việt. Output: các cặp *(khía cạnh, cảm xúc)* trên 10 khía cạnh của UIT-ViSFD.

```
"Máy chạy mượt, pin trâu nhưng camera chụp đêm tệ, giá hơi chát"
→ {Hiệu năng: tích cực, Pin: tích cực, Camera: tiêu cực, Giá: tiêu cực}
```

So sánh 4 phương pháp, chấm bằng cùng một script `evaluate.py`:

| Phương pháp | Thư mục | File dự đoán (val / test) |
|---|---|---|
| Rule-based (từ khóa + lexicon) | `src/rule_based/` | `pred_rule_val.csv` / `pred_rule_test.csv` |
| TF-IDF + LR/SVM | `src/tfidf/` | `pred_tfidf_val.csv` / `pred_tfidf_test.csv` |
| PhoBERT/ViSoBERT multi-task | `src/phobert/` | `pred_phobert_val.csv` / `pred_phobert_test.csv` |
| LLM zero/few-shot | `src/llm/` | `pred_llm_<kiểu>_val.csv` / `pred_llm_<kiểu>_test.csv` |

## Trạng thái dự án

| Phần | Trạng thái | Ai |
|---|---|---|
| Cấu trúc repo, quy ước format, `src/common/` | ✅ Xong | Leader |
| `evaluate.py` + test | ✅ Xong | Leader |
| `scripts/make_llm_subset.py` | ✅ Xong, chạy khi đã có gold | Leader |
| **`scripts/download_data.py` → `gold_*.csv`** | ⏳ **Đang làm, ưu tiên số 1** | **A** |
| EDA, tiền xử lý, rule-based | Chờ dữ liệu | A |
| TF-IDF, PhoBERT, LLM | Chờ dữ liệu | B, C, D |

**Trong lúc chờ A**, mọi người có thể:
- cài môi trường (mục bên dưới) và chạy `pytest` để chắc chắn máy mình chạy được;
- đọc [`docs/format_spec.md`](docs/format_spec.md) và [`CONTRIBUTING.md`](CONTRIBUTING.md);
- C và D: tạo token Hugging Face theo [`docs/huggingface.md`](docs/huggingface.md);
- C và A: thống nhất bộ tách từ (`format_spec.md` mục 6);
- viết khung code cho phần của mình, dùng `src.common.io.read_gold` / `write_pred`.

## Cài đặt

Yêu cầu Python 3.10+.

**Windows (PowerShell):**
```powershell
git clone https://github.com/AIVIETNAM-AIO-PlboiCart/absa-visfd.git; cd absa-visfd
python -m venv .venv
.venv\Scripts\Activate.ps1          # lỗi "running scripts is disabled": chạy một lần
                                    # Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
pip install -r requirements.txt
Copy-Item .env.example .env         # rồi mở .env, điền HF_TOKEN, LLM_API_KEY
pytest                              # kiểm tra: phải thấy "passed", không có "failed"
```

**Mac / Linux / Colab:**
```bash
git clone https://github.com/AIVIETNAM-AIO-PlboiCart/absa-visfd.git && cd absa-visfd
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
pytest
```

- Mỗi lần mở terminal mới phải **kích hoạt lại venv** (đầu dòng lệnh hiện `(.venv)`).
- Mọi lệnh chạy từ **thư mục gốc repo**.
- `requirements.txt` chỉ được chứa ký tự ASCII (pip trên Windows không đọc được tiếng Việt có dấu).
- Chạy trên Colab: đặt biến môi trường `ABSA_DATA_DIR=/content/drive/...` để ghi đè đường dẫn trong `configs/paths.yaml`.

## Quy trình chạy

```bash
# 1. (A) Tải dữ liệu, sinh data/processed/gold_{train,val,test}.csv
python scripts/download_data.py

# 2. (Leader) Chọn tập con cho LLM, sinh data/splits/llm_subset_{,val_}ids.txt
python scripts/make_llm_subset.py

# 3. (Mọi người) Chấm file dự đoán trên VAL trong lúc tuning
python evaluate.py --gold data/processed/gold_val.csv --pred predictions/pred_tfidf_val.csv --name tfidf_val

# 4. (Leader, cuối dự án, một lần) Chấm trên TEST
python evaluate.py --gold data/processed/gold_test.csv --pred predictions/pred_tfidf_test.csv --name tfidf_test
```

## Chấm điểm với `evaluate.py`

`evaluate.py` là **trọng tài duy nhất**: so file dự đoán với nhãn thật (gold), ghép theo `id`. Không ai tự tính F1 theo cách riêng.

```bash
python evaluate.py --gold data/processed/gold_val.csv \
                   --pred predictions/pred_llm_zeroshot_val.csv \
                   --name llm_zeroshot_val \
                   --ids data/splits/llm_subset_val_ids.txt   # tùy chọn: chỉ chấm trên tập con
```

**Bước 1: kiểm tra format.** Script dừng với `LỖI FORMAT: ...` (exit code 1) nếu: sai/thiếu/thừa cột, id trùng, pred thiếu hoặc thừa id so với gold, ô có giá trị ngoài `positive/negative/neutral/none` (kể cả ô trống).

**Bước 2: tính metric.** Mỗi bình luận là một tập cặp (khía cạnh, cảm xúc), bỏ qua ô `none`; TP/FP/FN cộng dồn trên toàn tập rồi mới tính P/R/F1.

| Metric | Câu hỏi | Ví dụ bên dưới |
|---|---|---|
| **Joint F1** (metric chính) | Đúng cả khía cạnh lẫn cảm xúc? Đúng khía cạnh, sai cảm xúc = 1 FP + 1 FN | 0.50 |
| Aspect F1 | Tìm đúng khía cạnh (chưa xét cảm xúc)? | 0.75 |
| Sentiment accuracy / macro-F1 | Trong các khía cạnh tìm đúng, cảm xúc đúng không? | 2/3 |

```
Gold: PERFORMANCE+, BATTERY+, CAMERA−, PRICE−
Pred: PERFORMANCE+, BATTERY−, CAMERA−, DESIGN+
```

Micro = cộng dồn trên mọi khía cạnh; Macro = trung bình theo khía cạnh, **bỏ các khía cạnh không có trong gold** (có in ghi chú).

**Bước 3–4: ghi kết quả** vào `results/` (UTF-8 có BOM, mở bằng Excel không lỗi font). Thư mục này **không commit**: dán bảng in ra màn hình vào mô tả PR.

| File | Nội dung |
|---|---|
| `summary.csv` | Mỗi lần chạy **nối thêm** một dòng: tên, file, tập con, số bình luận, thời điểm, các metric chính |
| `per_aspect_<name>.csv` | Support, TP/FP/FN, P/R/F1 Aspect và Joint cho từng khía cạnh |
| `errors_<name>.csv` | Mỗi ô sai một dòng: `id,text,aspect,gold,pred,error_type` với `MISSED` (bỏ sót), `SPURIOUS` (đoán thừa), `WRONG_SENTIMENT` (sai cảm xúc), dùng cho error analysis |

Độ trễ và chi phí **không** nằm trong `evaluate.py` (C và D đo riêng).

### Đọc và ghi dữ liệu đúng format

```python
from src.common.config import get_path
from src.common.io import read_gold, write_pred   # tự kiểm tra format
from src.common.labels import ASPECTS

gold_val = read_gold(get_path("processed_dir") / "gold_val.csv")   # KHÔNG dùng pd.read_csv trơn
# ... dự đoán ... df có cột: id + 10 khía cạnh, giá trị positive/negative/neutral/none
write_pred(df, get_path("predictions_dir") / "pred_tfidf_val.csv")
```

## Cấu trúc thư mục

```
absa-visfd/
├── configs/paths.yaml         # mọi đường dẫn; ghi đè bằng biến ABSA_<KHÓA>
├── docs/
│   ├── format_spec.md         # quy ước nhãn, format, quyết định chờ chốt
│   ├── huggingface.md         # token, đẩy/tải model
│   └── specs/                 # tài liệu thiết kế repo
├── scripts/
│   ├── download_data.py       # (A) tải UIT-ViSFD → gold_*.csv
│   └── make_llm_subset.py     # (Leader) chọn id tập con cho LLM
├── data/                      # raw/, processed/ KHÔNG commit; splits/ có commit
├── src/
│   ├── common/                # labels.py (nguồn nhãn duy nhất), io.py, config.py, console.py
│   ├── preprocessing/         # A
│   ├── rule_based/            # A
│   ├── tfidf/                 # B
│   ├── phobert/               # C
│   ├── llm/                   # D
│   └── api/                   # D
├── demo/                      # D
├── notebooks/                 # xem notebooks/README.md: ô import đầu tiên
├── predictions/               # pred_<method>[_<cấu hình>]_<split>.csv (có commit)
├── results/                   # output của evaluate.py (KHÔNG commit)
├── models/                    # cache cục bộ, KHÔNG commit (model ở HF Hub)
├── tests/                     # pytest
└── evaluate.py                # chấm điểm
```

Mỗi thư mục trong `src/` có README ghi **chủ thư mục**. Muốn sửa thư mục của người khác thì phải mở PR và được chủ thư mục đồng ý.

## Quy tắc quan trọng

- **Không dùng tập test để tuning.** Chỉ chấm test một lần vào cuối dự án (Leader chạy).
- Nhãn import từ `src/common/labels.py`, không tự gõ lại. Format: [`docs/format_spec.md`](docs/format_spec.md).
- Không commit dữ liệu, model, `.env`, `results/`. Model lưu trên Hugging Face Hub, ghim theo tag ([`docs/huggingface.md`](docs/huggingface.md)).
- Script in tiếng Việt thì gọi `src.common.console.setup_console()` ở đầu `main()` (tránh lỗi console Windows).
- Quy trình Git: xem [`CONTRIBUTING.md`](CONTRIBUTING.md).

## Nhóm

| Thành viên | Phần việc |
|---|---|
| Leader | Điều phối, `evaluate.py`, tích hợp, báo cáo |
| A | Dữ liệu, EDA, tiền xử lý, rule-based |
| B | TF-IDF + LR/SVM, phân tích insight |
| C | Fine-tune PhoBERT/ViSoBERT |
| D | LLM, API + demo |
