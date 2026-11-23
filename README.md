# ABSA cho bình luận điện thoại tiếng Việt (UIT-ViSFD)

**Aspect-Based Sentiment Analysis for Vietnamese Smartphone Reviews using Fine-tuned Pre-trained Language Models**

Input: một bình luận tiếng Việt. Output: các cặp *(khía cạnh, cảm xúc)* trên 10 khía cạnh của UIT-ViSFD.

```
"Máy chạy mượt, pin trâu nhưng camera chụp đêm tệ, giá hơi chát"
→ {Hiệu năng: tích cực, Pin: tích cực, Camera: tiêu cực, Giá: tiêu cực}
```

So sánh 4 phương pháp, chấm bằng cùng một script `evaluate.py`:

| Phương pháp | Thư mục | File dự đoán |
|---|---|---|
| Rule-based (từ khóa + lexicon) | `src/rule_based/` | `predictions/pred_rule.csv` |
| TF-IDF + LR/SVM | `src/tfidf/` | `predictions/pred_tfidf.csv` |
| PhoBERT/ViSoBERT multi-task | `src/phobert/` | `predictions/pred_phobert.csv` |
| LLM zero/few-shot | `src/llm/` | `predictions/pred_llm.csv` |

## Cài đặt

Yêu cầu Python 3.10+.

**Windows (PowerShell):**
```powershell
git clone <url-repo>; cd absa-visfd
python -m venv .venv
.venv\Scripts\Activate.ps1          # lỗi "running scripts is disabled": chạy một lần
                                    # Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
pip install -r requirements.txt
Copy-Item .env.example .env         # rồi mở .env, điền HF_TOKEN, LLM_API_KEY
```

**Mac / Linux / Colab:**
```bash
git clone <url-repo> && cd absa-visfd
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Mỗi lần mở terminal mới phải **kích hoạt lại venv** (đầu dòng lệnh hiện `(.venv)`).
`requirements.txt` chỉ được chứa ký tự ASCII (pip trên Windows không đọc được tiếng Việt có dấu).

## Chạy

```bash
# 1. Tải dữ liệu, sinh data/processed/gold_{train,val,test}.csv
python scripts/download_data.py

# 2. Chấm một file dự đoán (tuning chỉ dùng VAL)
python evaluate.py --gold data/processed/gold_val.csv --pred predictions/pred_tfidf.csv --name tfidf

# 3. Chạy test
pytest
```

Chạy trên Colab: đặt biến môi trường `ABSA_DATA_DIR=/content/drive/...` để ghi đè đường dẫn trong `configs/paths.yaml`.

## Chấm điểm với `evaluate.py`

`evaluate.py` là **trọng tài duy nhất**: so file dự đoán với nhãn thật (gold), ghép theo `id`. Không ai tự tính F1 theo cách riêng.

```bash
python evaluate.py --gold data/processed/gold_val.csv \
                   --pred predictions/pred_llm.csv \
                   --name llm_zeroshot \
                   --ids data/splits/llm_subset_ids.txt   # tùy chọn: chỉ chấm trên tập con
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

**Bước 3–4: ghi kết quả** vào `results/` (UTF-8 có BOM, mở bằng Excel không lỗi font):

| File | Nội dung |
|---|---|
| `summary.csv` | Mỗi lần chạy **nối thêm** một dòng: tên, file, tập con, số bình luận, thời điểm, các metric chính |
| `per_aspect_<name>.csv` | Support, TP/FP/FN, P/R/F1 Aspect và Joint cho từng khía cạnh |
| `errors_<name>.csv` | Mỗi ô sai một dòng: `id,text,aspect,gold,pred,error_type` với `MISSED` (bỏ sót), `SPURIOUS` (đoán thừa), `WRONG_SENTIMENT` (sai cảm xúc), dùng cho error analysis |

Độ trễ và chi phí **không** nằm trong `evaluate.py` (C và D đo riêng).

### Ghi file dự đoán đúng format

```python
from src.common.labels import ASPECTS
from src.common.io import write_pred   # kiểm tra format trước khi ghi

# df có cột: id + 10 khía cạnh, giá trị positive/negative/neutral/none
write_pred(df, "predictions/pred_tfidf.csv")
```

## Cấu trúc thư mục

```
absa-visfd/
├── configs/paths.yaml        # mọi đường dẫn; ghi đè bằng biến ABSA_<KHÓA>
├── docs/                     # format_spec.md, đề tài, specs/ (thiết kế)
├── scripts/download_data.py  # tải UIT-ViSFD → gold_*.csv
├── data/                     # KHÔNG commit (trừ data/splits/)
├── src/
│   ├── common/               # labels.py (nguồn nhãn duy nhất), io.py, config.py
│   ├── preprocessing/        # A
│   ├── rule_based/           # A
│   ├── tfidf/                # B
│   ├── phobert/              # C
│   ├── llm/                  # D
│   └── api/                  # D
├── demo/                     # D
├── notebooks/
├── predictions/              # pred_*.csv
├── results/                  # output của evaluate.py
├── models/                   # cache cục bộ, KHÔNG commit (model ở HF Hub)
├── tests/                    # pytest (17 test cho evaluate.py)
└── evaluate.py               # chấm điểm, xem mục bên trên
```

## Quy tắc quan trọng

- **Không dùng tập test để tuning.** Chỉ chấm test một lần vào cuối dự án (Leader chạy).
- Nhãn import từ `src/common/labels.py`, không tự gõ lại. Format: [`docs/format_spec.md`](docs/format_spec.md).
- Không commit dữ liệu, model, `.env`. Model lưu trên Hugging Face Hub, ghim theo tag.
- Quy trình Git: xem [`CONTRIBUTING.md`](CONTRIBUTING.md).

## Nhóm

| Thành viên | Phần việc |
|---|---|
| Leader | Điều phối, `evaluate.py`, tích hợp, báo cáo |
| A | Dữ liệu, EDA, tiền xử lý, rule-based |
| B | TF-IDF + LR/SVM, phân tích insight |
| C | Fine-tune PhoBERT/ViSoBERT |
| D | LLM, API + demo |
