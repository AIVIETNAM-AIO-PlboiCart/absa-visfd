# Đề tài: Phân tích cảm xúc theo khía cạnh (ABSA) trên bình luận điện thoại tiếng Việt

## 1. Tên đề tài

- **Tiếng Việt:** Phân tích cảm xúc theo khía cạnh (ABSA) trên bình luận sản phẩm điện thoại tiếng Việt bằng mô hình ngôn ngữ tiền huấn luyện
- **Tiếng Anh:** Aspect-Based Sentiment Analysis for Vietnamese Smartphone Reviews using Fine-tuned Pre-trained Language Models

## 2. Bối cảnh

Thương mại điện tử ở Việt Nam phát triển mạnh, và người mua ngày càng dựa vào bình luận của người dùng trước để ra quyết định. Với ngành hàng điện thoại, mỗi sản phẩm có thể nhận hàng nghìn bình luận. Mỗi bình luận thường nói về nhiều khía cạnh cùng lúc, như pin, camera, hiệu năng, giá và dịch vụ.

Doanh nghiệp (nhà bán lẻ, hãng sản xuất) muốn khai thác nguồn phản hồi này để cải thiện sản phẩm và dịch vụ. Tuy nhiên, số lượng bình luận quá lớn nên không thể đọc thủ công.

## 3. Vấn đề thực tại

- **Số sao không phản ánh đủ ý kiến:** một bình luận 4 sao vẫn có thể chê camera hoặc chê giá. Điểm đánh giá tổng chỉ cho biết người dùng hài lòng *bao nhiêu*, không cho biết họ hài lòng hay không hài lòng *về điều gì*.
- **Phân tích cảm xúc truyền thống quá thô:** gán một nhãn tích cực/tiêu cực cho cả bình luận sẽ làm mất thông tin khi bình luận vừa khen vừa chê.
- **Ngôn ngữ bình luận tiếng Việt khó xử lý:** viết tắt, teencode, thiếu dấu, câu phủ định ("không tệ"), mỉa mai, và khía cạnh ngầm (ví dụ "máy cầm hơi nóng" không nhắc tên khía cạnh nào).
- **Phương pháp dựa trên từ khóa dễ sai:** cách tiếp cận rule-based không bao quát được cách diễn đạt đa dạng và ngữ cảnh.

→ Cần một hệ thống tự động xác định **những khía cạnh được nhắc đến** trong bình luận và **cảm xúc đối với từng khía cạnh**.

## 4. Input – Output

**Input:** một bình luận tiếng Việt về sản phẩm điện thoại, ở dạng văn bản thô.

**Output:** tập các cặp *(khía cạnh, cảm xúc)*, trong đó:

- Khía cạnh thuộc tập định nghĩa sẵn của dataset UIT-ViSFD, ví dụ: màn hình, camera, pin, hiệu năng, bộ nhớ, thiết kế, tính năng, giá, dịch vụ & phụ kiện, đánh giá chung.
- Cảm xúc ∈ {tích cực, tiêu cực, trung tính}.

**Ví dụ:**

```
Input:  "Máy chạy mượt, pin trâu nhưng camera chụp đêm tệ, giá hơi chát"
Output: {Hiệu năng: tích cực, Pin: tích cực, Camera: tiêu cực, Giá: tiêu cực}
```

**Ở mức hệ thống:**

- Input: tập bình luận của một sản phẩm.
- Output: báo cáo tổng hợp tỷ lệ khen/chê theo từng khía cạnh.

## 5. Các nhiệm vụ chính

1. **Khảo sát và chuẩn bị dữ liệu:** tìm hiểu bộ UIT-ViSFD, thống kê phân bố khía cạnh và nhãn, rồi tiền xử lý văn bản (chuẩn hóa teencode, dấu, tách từ).
2. **Xây dựng baseline rule-based:** dùng từ điển từ khóa khía cạnh kết hợp sentiment lexicon.
3. **Xây dựng baseline học máy:** TF-IDF kết hợp Logistic Regression/SVM.
4. **Fine-tune mô hình ngôn ngữ tiền huấn luyện:** PhoBERT hoặc ViSoBERT, thiết kế theo kiến trúc multi-task cho hai tác vụ phát hiện khía cạnh và phân loại cảm xúc.
5. **Thực nghiệm với LLM:** zero-shot/few-shot prompting, làm mốc so sánh.
6. **Đánh giá và so sánh:** dùng Precision, Recall, Micro/Macro-F1 trên tập test, kèm so sánh độ trễ và chi phí giữa các phương pháp.
7. **Phân tích lỗi:** phân loại các trường hợp mô hình dự đoán sai và tìm nguyên nhân.
8. **Phân tích insight:** xác định khía cạnh ảnh hưởng mạnh nhất đến số sao, và phát hiện các bình luận điểm cao nhưng vẫn có phàn nàn.
9. **Triển khai demo:** API (FastAPI) và giao diện (Streamlit/Gradio) để nhập bình luận và nhận kết quả phân tích.

## 6. Bảng phân công nhiệm vụ

| Thành viên | Vai trò | Nhiệm vụ | Sản phẩm bàn giao |
|---|---|---|---|
| **Leader** | Điều phối & tích hợp | Tạo repo Git, quy định cấu trúc thư mục và quy trình branch/pull request | Repo + README hướng dẫn |
| | | Chốt format file dự đoán và danh sách nhãn chung | Tài liệu quy ước format |
| | | Viết `evaluate.py`: kiểm tra format, tính Aspect/Sentiment/Joint F1, xuất bảng kết quả và file lỗi | `evaluate.py` |
| | | Review code và merge pull request của các thành viên | — |
| | | Hỗ trợ C fine-tune PhoBERT (thiết kế kiến trúc, tuning) | — |
| | | Tổng hợp bảng so sánh các phương pháp | Bảng kết quả cuối |
| | | Đưa ra template báo cáo, ghép báo cáo và làm slide | Báo cáo + slide |
| **A** | Dữ liệu & Rule-based | Tải UIT-ViSFD, chuyển nhãn JSON sang format chung | `gold_train/val/test.csv` |
| | | EDA: phân bố khía cạnh, phân bố nhãn, độ dài review, mất cân bằng nhãn | Notebook EDA + biểu đồ |
| | | Tiền xử lý: chuẩn hóa teencode/viết tắt, xử lý dấu, tách từ (thống nhất với C) | Module tiền xử lý + dữ liệu sạch |
| | | Xây dựng baseline rule-based: từ điển từ khóa khía cạnh + sentiment lexicon + xử lý phủ định đơn giản | `pred_rule.csv` + code |
| **B** | ML cổ điển & Insight | Xây dựng baseline TF-IDF + Logistic Regression/SVM, mỗi khía cạnh một classifier | `pred_tfidf.csv` + code |
| | | Thử một vài cấu hình (n-gram, có/không tiền xử lý) và ghi lại kết quả | Bảng thử nghiệm |
| | | Phân tích insight: khía cạnh nào kéo số sao xuống, review điểm cao nhưng vẫn có phàn nàn | Notebook insight + biểu đồ |
| **C** | PhoBERT | Dựng pipeline fine-tune PhoBERT/ViSoBERT (multi-task cho từng khía cạnh) | Code training |
| | | Huấn luyện và tuning trên tập validation, lưu checkpoint | Model tốt nhất |
| | | Chạy dự đoán trên tập test | `pred_phobert.csv` |
| | | Ghi lại cấu hình, thời gian train, độ trễ khi dự đoán | Bảng cấu hình + thông số |
| **D** | LLM & Demo | Thiết kế prompt zero-shot/few-shot cho bài toán ABSA | Bộ prompt |
| | | Chạy LLM trên 200–300 mẫu test, chuyển câu trả lời về format chung | `pred_llm.csv` |
| | | Đo độ trễ và ước tính chi phí của LLM so với PhoBERT | Bảng so sánh chi phí |
| | | Xây API (FastAPI) và giao diện demo (Streamlit/Gradio) với model tốt nhất | API + demo chạy được |
| **Cả nhóm** | Việc chung | Error analysis: mỗi người phân tích 10–15 mẫu sai ngẫu nhiên theo khía cạnh được chia, ghi vào sheet chung | Sheet error analysis |
| | | Viết phần báo cáo về phần việc của mình theo template | Phần báo cáo cá nhân |
| | | Ghép cặp dự phòng: A↔B, C↔D nắm sơ việc của nhau | — |

### Lưu ý về thứ tự phụ thuộc

- Dữ liệu sạch (A) và `evaluate.py` (Leader) phải xong **trước tiên**, vì B, C, D đều phụ thuộc vào hai phần này.
- A và C cần **thống nhất cách tách từ ngay từ đầu**, vì PhoBERT yêu cầu văn bản đã tách từ.
- Phần demo của D cần chờ C có model tốt nhất.
- **Không ai dùng tập test để tuning.** Tập test chỉ dùng cho lần đánh giá cuối cùng.
