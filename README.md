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

```bash
git clone <url-repo> && cd absa-visfd
python -m venv .venv
# Windows: .venv\Scripts\activate      Mac/Linux: source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env    # rồi điền HF_TOKEN, LLM_API_KEY
```

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
├── tests/
└── evaluate.py
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
