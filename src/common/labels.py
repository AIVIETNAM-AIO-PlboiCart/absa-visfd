"""Danh sách nhãn chung — NGUỒN DUY NHẤT. Mọi module import từ đây, không gõ lại.

Xem docs/format_spec.md để biết quy tắc chuyển nhãn.
"""

ASPECTS = ["SCREEN", "CAMERA", "FEATURES", "BATTERY", "PERFORMANCE",
           "STORAGE", "DESIGN", "PRICE", "GENERAL", "SER&ACC"]

SENTIMENTS = ["positive", "negative", "neutral"]
NONE = "none"
VALID_VALUES = SENTIMENTS + [NONE]

# Chỉ dùng khi hiển thị (demo, báo cáo)
ASPECT_VI = {
    "SCREEN": "Màn hình",
    "CAMERA": "Camera",
    "FEATURES": "Tính năng",
    "BATTERY": "Pin",
    "PERFORMANCE": "Hiệu năng",
    "STORAGE": "Bộ nhớ",
    "DESIGN": "Thiết kế",
    "PRICE": "Giá",
    "GENERAL": "Đánh giá chung",
    "SER&ACC": "Dịch vụ & phụ kiện",
}
SENTIMENT_VI = {"positive": "tích cực", "negative": "tiêu cực", "neutral": "trung tính"}

# Thứ tự cột cố định của các file CSV
GOLD_COLUMNS = ["id", "text", "n_star", "has_others"] + ASPECTS
PRED_COLUMNS = ["id"] + ASPECTS
