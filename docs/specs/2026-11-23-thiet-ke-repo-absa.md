# Thiết kế repo dự án ABSA (UIT-ViSFD)

- **Ngày:** 2026-11-23
- **Người phụ trách:** Leader
- **Phạm vi:** 3 việc đầu tiên của Leader:
  1. Tạo repo Git, quy định cấu trúc thư mục và quy trình branch/PR.
  2. Chốt format file dự đoán và danh sách nhãn chung.
  3. Viết `evaluate.py`.
- **Trạng thái:** Bản nháp, chờ Leader duyệt.

> Quy ước trong tài liệu:
> - **[Đã chốt]** là quyết định của Leader.
> - **[Đề xuất]** là đề xuất của Claude, Leader có thể sửa.
> - **[Để người xây dựng]** là chi tiết mà người viết code tự quyết, không làm thay đổi thiết kế.

---

## 1. Mục đích

Repo là **"hợp đồng chung"** của cả nhóm 5 người (Leader, A, B, C, D):

- **Cấu trúc repo** quy định code để ở đâu và ai sở hữu phần nào.
- **Format và nhãn** quy định kết quả của mọi phương pháp trông như thế nào.
- **`evaluate.py`** là trọng tài duy nhất, chấm điểm mọi phương pháp theo cùng một cách.

B, C và D đều phụ thuộc vào dữ liệu sạch (của A) và `evaluate.py` (của Leader). Vì vậy repo phải xong **trước tiên**, đủ rõ ràng để 4 người làm song song mà không phải sửa lại cho khớp nhau.

Mục đích phụ: repo đủ gọn gàng và chuyên nghiệp để đưa vào CV (vị trí AI Engineer).

## 2. Mục tiêu, không làm, phản mục tiêu

**Mục tiêu**
- Người mới dùng Git vẫn làm theo được, có hướng dẫn từng lệnh.
- Mỗi thành viên làm trong thư mục riêng, hạn chế conflict.
- Kết quả của 4 phương pháp (rule-based, TF-IDF, PhoBERT, LLM) được chấm bằng cùng một script, cùng format, cùng tập dữ liệu.
- Ai clone repo về cũng tái tạo được dữ liệu và kết quả.

**Không làm (trong giai đoạn này)**
- Không dựng CI/GitHub Actions, vì nhóm đa số mới làm quen Git. Có thể bổ sung sau.
- Không dựng hạ tầng triển khai (Docker, cloud). Demo thuộc phần việc của D, làm sau.
- Không tối ưu hiệu năng `evaluate.py`, vì tập test chỉ khoảng 2.224 dòng.

**Phản mục tiêu (repo "chạy được" nhưng vẫn coi là thất bại nếu)**
- Mỗi người tự tính F1 theo một kiểu, khiến bảng so sánh cuối không đáng tin.
- Tập test bị dùng để tuning, hoặc bị lẫn vào dữ liệu train.
- Model hoặc tiền xử lý ở demo khác với lúc train mà không ai phát hiện (lỗi im lặng).
- Token, API key hoặc file model nặng bị commit lên Git.

## 3. Ràng buộc

- **Đa số thành viên mới làm quen Git** [Đã chốt]. Quy trình phải đơn giản, có tài liệu hướng dẫn từng bước, và Leader gánh phần review.
- **Môi trường chạy code chưa xác định** (máy cá nhân hay Colab/Kaggle). Thiết kế phải chạy được ở cả hai.
- **License của UIT-ViSFD chưa rõ** (SEACrowd ghi UNKNOWN), nên không phân phối lại dữ liệu qua repo.
- **Bản UIT-ViSFD trên Hugging Face (`visolex/ViSFD`) gộp train/dev/test vào một split**, phân biệt bằng cột `type`.
- **PhoBERT cần văn bản đã tách từ.** Bước tách từ lúc suy luận phải giống hệt lúc train.
- **Checkpoint PhoBERT nặng khoảng 500MB**, không đưa được vào Git.
- **LLM chỉ chạy trên 200–300 mẫu test** vì chi phí.
- **Không ai được dùng tập test để tuning.**

## 4. Các phương án đã cân nhắc

| Vấn đề | Các phương án | Chọn | Lý do |
|---|---|---|---|
| Quy trình branch | (a) Git Flow (`main` + `dev` + feature); (b) GitHub Flow (`main` + feature); (c) mọi người push thẳng vào `main` | **(b)** [Đề xuất, đã thống nhất] | (a) quá phức tạp với nhóm 5 người mới dùng Git; (c) không kiểm soát được chất lượng. |
| Format file dự đoán | (a) dạng dài, mỗi dòng một cặp (id, aspect, sentiment); (b) dạng rộng, `id` + 10 cột khía cạnh | **(b)** [Đề xuất, đã thống nhất] | Khớp với kiến trúc (mỗi khía cạnh là một bài toán phân loại 4 lớp), số cột cố định, dễ kiểm tra lỗi. |
| Nhãn `OTHERS` | (a) giữ làm cột thứ 11; (b) bỏ tag, giữ bình luận | **(b)** [Đã chốt] | OTHERS không có cảm xúc nên không khớp format; "cả 10 ô `none`" đã biểu diễn đúng ý nghĩa của nó; output của đề tài chỉ gồm các cặp (khía cạnh, cảm xúc). |
| Nơi lưu model | (a) Git LFS; (b) Google Drive; (c) Hugging Face Hub | **(c)** [Đã chốt] | Code giống nhau dù chạy ở local hay Colab, có quản lý phiên bản bằng tag, miễn phí. |
| Dữ liệu trong repo | (a) commit dữ liệu gốc và gold; (b) commit script tải và sinh dữ liệu | **(b)** [Đề xuất] | Tránh phân phối lại dữ liệu chưa rõ license nếu sau này repo chuyển public; ai chạy script cũng ra cùng kết quả. |
| Kiểm tra tự động khi mở PR | (a) GitHub Actions; (b) kiểm tra thủ công kèm checklist trong PR | **(b)** [Đã chốt: nhóm mới làm quen Git] | Giảm độ phức tạp ban đầu; có thể nâng lên (a) sau. |

## 5. Thiết kế

### 5.1 Cấu trúc thư mục [Đề xuất]

```
absa-visfd/
├── README.md                    # giới thiệu, cài đặt, cách chạy từng phần
├── CONTRIBUTING.md              # hướng dẫn Git từng lệnh cho người mới
├── requirements.txt
├── .gitignore
├── .env.example                 # mẫu biến môi trường (HF_TOKEN, LLM_API_KEY, ...)
├── .github/
│   └── pull_request_template.md # checklist khi mở PR
├── configs/
│   └── paths.yaml               # mọi đường dẫn dữ liệu/model, ghi đè được bằng biến môi trường
├── docs/
│   ├── format_spec.md           # quy ước format và nhãn (mục 5.3)
│   └── specs/                   # tài liệu thiết kế (file này)
├── scripts/
│   └── download_data.py         # tải UIT-ViSFD → sinh data/processed/gold_*.csv
├── data/                        # KHÔNG commit (trừ data/splits/)
│   ├── raw/
│   ├── processed/               # gold_train.csv, gold_val.csv, gold_test.csv
│   └── splits/
│       └── llm_subset_ids.txt   # CÓ commit: danh sách id cho LLM
├── src/
│   ├── common/
│   │   ├── labels.py            # danh sách nhãn chung — nguồn duy nhất
│   │   ├── io.py                # đọc/ghi gold & pred đúng format
│   │   └── config.py            # đọc configs/paths.yaml + .env
│   ├── preprocessing/           # A (dùng chung cho C và D)
│   ├── rule_based/              # A
│   ├── tfidf/                   # B
│   ├── phobert/                 # C (model.py chứa class model, D import lại)
│   ├── llm/                     # D (prompts/ nằm trong đây)
│   └── api/                     # D (FastAPI)
├── demo/                        # D (Streamlit/Gradio)
├── notebooks/                   # eda.ipynb (A), insight.ipynb (B), colab_*.ipynb (notebook mỏng)
├── predictions/                 # pred_rule.csv, pred_tfidf.csv, pred_phobert.csv, pred_llm.csv
├── results/                     # output của evaluate.py
├── models/                      # cache cục bộ, KHÔNG commit
├── tests/
│   └── test_evaluate.py
└── evaluate.py
```

**Quyền sở hữu thư mục:** mỗi thư mục trong `src/` có một chủ (ghi ở bảng dưới). Muốn sửa thư mục của người khác thì phải mở PR và được chủ thư mục đồng ý.

| Thư mục | Chủ |
|---|---|
| `src/common/`, `evaluate.py`, `configs/`, `docs/`, `scripts/`, `tests/` | Leader |
| `src/preprocessing/`, `src/rule_based/`, `notebooks/eda.ipynb` | A |
| `src/tfidf/`, `notebooks/insight.ipynb` | B |
| `src/phobert/` | C |
| `src/llm/`, `src/api/`, `demo/` | D |

**`.gitignore` phải chặn:** `data/raw/`, `data/processed/`, `models/`, `.env`, `__pycache__/`, `.ipynb_checkpoints/`, các file `*.bin`, `*.safetensors`, `*.pt`.

**Được commit:** code, `predictions/pred_*.csv`, `results/`, `data/splits/llm_subset_ids.txt`, tài liệu.

**Notebook:** xóa output trước khi commit (Kernel → Restart & Clear Output). Hướng dẫn cách làm này nằm trong `CONTRIBUTING.md`.

### 5.2 Quy trình branch/PR cho người mới [Đề xuất]

**Cài đặt trên GitHub (Leader làm một lần):**
- Repo để **private** trong lúc làm đồ án. Khi nào chuyển public để đưa vào CV thì Leader quyết sau.
- Bật **branch protection** cho `main`:
  - bắt buộc qua PR;
  - cần ít nhất 1 approve;
  - cấm force push và cấm xóa nhánh `main`.
- Chế độ merge: **chỉ cho phép squash merge**, và tự động xóa nhánh sau khi merge.
- Thêm cả 4 thành viên làm collaborator.

**Quy tắc đặt tên nhánh:** `<loại>/<người>-<việc>`. Ví dụ:
- `feat/a-preprocessing`
- `feat/c-phobert-multitask`
- `fix/b-tfidf-ngram`
- `docs/leader-format-spec`

**Vòng làm việc (ghi trong `CONTRIBUTING.md` kèm lệnh cụ thể):**

```bash
git checkout main && git pull                 # 1. lấy bản mới nhất
git checkout -b feat/a-preprocessing          # 2. tạo nhánh mới
# ... sửa code ...
git add src/preprocessing/                    # 3. chỉ add đúng thư mục của mình
git commit -m "feat(preprocessing): chuẩn hóa teencode"
git pull origin main                          # 4. cập nhật main, tự xử lý conflict nếu có
git push -u origin feat/a-preprocessing       # 5. đẩy lên rồi mở PR trên GitHub
```

**Quy ước commit message:** `<loại>(<phần>): <mô tả ngắn>`. Các loại: `feat`, `fix`, `docs`, `refactor`, `test`.

**PR template** (`.github/pull_request_template.md`) có checklist:
- [ ] Code chạy được trên máy mình.
- [ ] Nếu có file `pred_*.csv`: đã chạy `evaluate.py` trên **val** và qua bước kiểm tra format.
- [ ] Không commit file dữ liệu, model, `.env` hay API key.
- [ ] Không dùng tập test để tuning.
- [ ] Notebook đã xóa output.

**CONTRIBUTING.md** cần có thêm: cách cài Git và clone repo, cách xử lý conflict đơn giản, cách lỡ commit nhầm file thì gỡ ra, và nên hỏi ai khi bị kẹt.

### 5.3 Nhãn và format [Đề xuất; riêng OTHERS là Đã chốt]

**Danh sách nhãn** nằm trong `src/common/labels.py`. Đây là nguồn duy nhất: mọi người import từ đây, không ai tự gõ lại.

```python
ASPECTS = ["SCREEN", "CAMERA", "FEATURES", "BATTERY", "PERFORMANCE",
           "STORAGE", "DESIGN", "PRICE", "GENERAL", "SER&ACC"]
SENTIMENTS = ["positive", "negative", "neutral"]
NONE = "none"
VALID_VALUES = SENTIMENTS + [NONE]
ASPECT_VI = {"SCREEN": "Màn hình", "CAMERA": "Camera", "FEATURES": "Tính năng",
             "BATTERY": "Pin", "PERFORMANCE": "Hiệu năng", "STORAGE": "Bộ nhớ",
             "DESIGN": "Thiết kế", "PRICE": "Giá", "GENERAL": "Đánh giá chung",
             "SER&ACC": "Dịch vụ & phụ kiện"}  # chỉ dùng khi hiển thị
```

**Quy tắc chuyển nhãn gốc** (`{ASPECT#Polarity};...`) sang format rộng:
- `Positive`, `Negative`, `Neutral` được chuyển thành chữ thường.
- Khía cạnh không xuất hiện trong nhãn gốc thì điền `none`.
- **Bỏ tag `{OTHERS}`** [Đã chốt]. Bình luận chỉ có OTHERS sẽ thành 10 ô `none`. Thêm cột phụ `has_others` (0/1), cột này **không dùng để chấm điểm**.
- Một khía cạnh có 2 cảm xúc khác nhau trong cùng bình luận: **chưa chốt quy tắc**. A đếm số trường hợp trong EDA, sau đó Leader chọn quy tắc và ghi vào `format_spec.md`.
- Gặp tag lạ (khía cạnh ngoài danh sách) thì script **báo lỗi**, không được bỏ qua âm thầm.

**File gold** (`data/processed/gold_{train,val,test}.csv`):
```
id,text,n_star,has_others,SCREEN,CAMERA,FEATURES,BATTERY,PERFORMANCE,STORAGE,DESIGN,PRICE,GENERAL,SER&ACC
```

**File dự đoán** (`predictions/pred_<method>[_<cấu hình>].csv`):
```
id,SCREEN,CAMERA,FEATURES,BATTERY,PERFORMANCE,STORAGE,DESIGN,PRICE,GENERAL,SER&ACC
```

**Quy tắc chung:**
- Định dạng UTF-8, phân cách bằng dấu phẩy, header đúng thứ tự như trên.
- Ghép dòng gold và pred **theo `id`, không theo thứ tự dòng.**
- `id` có dạng `<split>_<số thứ tự trong file gốc, 5 chữ số>`, ví dụ `test_00001`. Id được sinh một lần trong `download_data.py`, không bao giờ đổi.
- **Ô trống hoặc NaN là lỗi format.** Muốn nói "không có khía cạnh" thì phải ghi `none`.

### 5.4 Dữ liệu [Đề xuất]

`scripts/download_data.py`:
1. Tải UIT-ViSFD từ **nguồn gốc** (`github.com/LuongPhan/UIT-ViSFD`). Nếu không tải được thì dùng bản `visolex/ViSFD` trên Hugging Face, tách split theo cột `type`.
2. Kiểm tra số dòng: train 7.786, dev 1.112, test 2.224. Sai thì dừng và báo lỗi.
3. Chuyển nhãn theo mục 5.3, sinh id, ghi ra 3 file `gold_*.csv`.
4. In thống kê ngắn: số nhãn của từng khía cạnh, số bình luận chỉ có OTHERS.

Script chỉ sinh dữ liệu gold với text **gốc**. Bước tiền xử lý (teencode, tách từ) thuộc module của A, đặt ở `src/preprocessing/`, và **không ghi đè lên file gold**.

### 5.5 Model trên Hugging Face Hub [Đã chốt dùng HF; chi tiết là Đề xuất]

- Tạo một **HF organization** cho nhóm, add cả 5 người. Repo model để **private**.
- C push checkpoint và gắn tag phiên bản (`v0.1`, `v1.0`, ...). Code đọc model **luôn ghim theo tag** (`revision="v1.0"`), không đọc bản mới nhất.
- Class model multi-task đặt ở `src/phobert/model.py`, kế thừa `PyTorchModelHubMixin` để push/load được cả 10 head. Cấm dùng `AutoModel.from_pretrained` trơn, vì cách này sẽ nạp head ngẫu nhiên mà không báo lỗi.
- Tokenizer push cùng repo model. Bước tách từ dùng chung module ở `src/preprocessing/`.
- Token để trong `.env` (`HF_TOKEN=...`), đọc bằng `python-dotenv`. `.env.example` liệt kê các biến cần có, không chứa giá trị thật.
- Tên repo model và tag đang dùng ghi trong `configs/paths.yaml`.

### 5.6 Cấu hình đường dẫn [Đề xuất]

Vì chưa rõ nhóm chạy code ở local hay Colab:
- Mọi đường dẫn (thư mục dữ liệu, thư mục predictions, repo model trên HF, tag) nằm trong `configs/paths.yaml`, đọc qua `src/common/config.py`.
- Có thể ghi đè bằng biến môi trường. Ví dụ trên Colab đặt `ABSA_DATA_DIR=/content/drive/MyDrive/absa/data`.
- Không được viết cứng đường dẫn tuyệt đối trong code.
- Notebook Colab (`notebooks/colab_*.ipynb`) chỉ làm 3 việc: `git clone`, `pip install -r requirements.txt`, rồi gọi script trong `src/`. Không viết logic trong notebook.

### 5.7 `evaluate.py` [Đề xuất, đã thống nhất về metric]

**Cách gọi:**
```
python evaluate.py --gold data/processed/gold_val.csv \
                   --pred predictions/pred_tfidf.csv \
                   --name tfidf \
                   [--ids data/splits/llm_subset_ids.txt] \
                   [--out results/]
```

**Bước 1: Kiểm tra format.** Dừng và báo lỗi rõ ràng nếu gặp một trong các trường hợp:
- thiếu, thừa hoặc sai tên cột;
- id bị trùng;
- id có trong gold mà thiếu trong pred, hoặc ngược lại (sau khi đã lọc theo `--ids` nếu có);
- ô có giá trị ngoài `VALID_VALUES`, kể cả ô trống.

**Bước 2: Tính metric.** Mỗi bình luận được xem là một tập các cặp (khía cạnh, cảm xúc), bỏ qua các ô `none`. TP, FP, FN được **cộng dồn trên toàn tập rồi mới tính P/R/F1**, không tính F1 riêng từng bình luận rồi lấy trung bình. Khi mẫu số bằng 0 thì giá trị tương ứng bằng 0.

| Metric | Điều kiện TP | Báo cáo |
|---|---|---|
| **Aspect** | gold ≠ none và pred ≠ none | P, R, F1 — Micro và Macro (trung bình theo khía cạnh) |
| **Sentiment** | chỉ xét các ô là TP ở mức Aspect; đúng nếu cảm xúc trùng | Accuracy, Macro-F1 trên 3 lớp |
| **Joint** (metric chính) | đúng cả khía cạnh và cảm xúc; đúng khía cạnh nhưng sai cảm xúc thì tính 1 FP + 1 FN | P, R, F1 — Micro và Macro |
| Theo từng khía cạnh | — | P/R/F1 Aspect và Joint cho từng khía cạnh trong 10 khía cạnh |

Khi tính Macro trên một tập con, khía cạnh nào không xuất hiện trong gold thì loại khỏi trung bình và in ra ghi chú.

**Bước 3: Ghi kết quả.**
- Nối thêm một dòng vào `results/summary.csv`, gồm: `name`, `gold_file`, `subset`, `n_reviews`, thời điểm chạy, và các metric chính.
- Ghi `results/per_aspect_<name>.csv`.
- In bảng tóm tắt ra màn hình.

**Bước 4: Ghi file lỗi** `results/errors_<name>.csv`, mỗi dòng là một ô sai:
```
id,text,aspect,gold,pred,error_type   # error_type ∈ {MISSED, SPURIOUS, WRONG_SENTIMENT}
```

**Test** (`tests/test_evaluate.py`), chạy bằng `pytest`:
- Chấm gold với chính nó: mọi F1 bằng 1.0.
- Pred toàn `none`: Aspect F1 và Joint F1 bằng 0.
- Ví dụ tính tay. Gold {PERFORMANCE+, BATTERY+, CAMERA−, PRICE−}, pred {PERFORMANCE+, BATTERY−, CAMERA−, DESIGN+}. Kết quả phải là Aspect F1 = 0.75, Joint F1 = 0.50, Sentiment accuracy = 2/3.
- Bình luận gold rỗng và pred rỗng không làm thay đổi điểm.
- File pred thiếu dòng, id trùng, hoặc có ô sai giá trị: script phải báo lỗi.

Độ trễ và chi phí **không** nằm trong `evaluate.py`. C và D đo riêng.

### 5.8 Tập con cho LLM [Đề xuất]

- Leader chọn 300 id từ tập test, ngẫu nhiên với seed cố định. Nên phân tầng sao cho khía cạnh nào cũng có mặt; riêng STORAGE rất hiếm nên cần đảm bảo có ít nhất vài mẫu.
- Danh sách lưu ở `data/splits/llm_subset_ids.txt` và được commit.
- Bảng kết quả cuối có thêm một cột: điểm của **cả 4 phương pháp** trên cùng tập con này, để so sánh công bằng với LLM.

### 5.9 Quy tắc tập test

- Mọi việc tuning, chọn checkpoint và so sánh cấu hình đều làm trên **val**.
- Chỉ chấm trên **test một lần**, vào cuối dự án. Leader là người chạy và ghi vào bảng cuối.
- Checklist trong PR template nhắc lại quy tắc này.

## 6. Thứ tự làm

1. Tạo repo, viết `.gitignore`, `.env.example`, `README.md`, `CONTRIBUTING.md` và PR template; bật branch protection; add thành viên.
2. Viết `src/common/labels.py`, `io.py`, `config.py` và `docs/format_spec.md`, rồi gửi ngay cho A.
3. Viết `scripts/download_data.py`. Leader hoặc A làm, chốt ai làm khi giao việc.
4. Viết `evaluate.py` và `tests/test_evaluate.py`, test bằng dữ liệu giả trước, sau đó chạy với gold thật.
5. Sinh `llm_subset_ids.txt` khi đã có `gold_test.csv`.
6. Tạo HF organization và repo model trống để C push vào.

## 7. Để lại cho người xây dựng

- Phiên bản cụ thể của các thư viện trong `requirements.txt`.
- Cách trình bày bảng in ra màn hình (markdown hay bảng thường).
- Lời văn chi tiết của `README.md`, `CONTRIBUTING.md` và PR template, miễn là đủ các ý ở mục 5.2.
- Thư viện đọc YAML/.env, miễn là đơn giản và phổ biến.

## 8. Câu hỏi còn mở

1. **Nhóm chạy code ở đâu** (local, Colab/Kaggle, hay cả hai)? Thiết kế hiện tại đã hỗ trợ cả hai. Câu trả lời chỉ ảnh hưởng tới việc có cần viết notebook Colab mẫu ngay từ đầu hay không.
2. **Quy tắc khi một khía cạnh có 2 cảm xúc** trong cùng một bình luận: chờ số liệu EDA của A.
3. **Ai viết `download_data.py`**, Leader hay A?
4. **Repo có chuyển public sau đồ án không?** Hiện tại để private; thiết kế (không commit dữ liệu, không commit token) đã sẵn sàng nếu sau này chuyển public.
