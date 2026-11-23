# Notebooks

**Chủ thư mục:** A (eda.ipynb), B (insight.ipynb), người tạo (colab_*.ipynb)

Xóa output trước khi commit (Kernel → Restart & Clear Output). Notebook Colab chỉ làm 3 việc: git clone, pip install -r requirements.txt, gọi script trong src/. Không viết logic trong notebook.

**Ô đầu tiên của mọi notebook** (để `import src...` chạy được khi notebook nằm trong `notebooks/`):

```python
import sys
from pathlib import Path

ROOT = Path.cwd().parent if Path.cwd().name == "notebooks" else Path.cwd()
sys.path.insert(0, str(ROOT))

from src.common.labels import ASPECTS
from src.common.config import get_path
from src.common.io import read_gold

gold_train = read_gold(get_path("processed_dir") / "gold_train.csv")
```

Đọc dữ liệu bằng `read_gold` thay vì `pd.read_csv`. Nếu đọc thẳng, pandas sẽ đổi chuỗi `none` và ô trống thành NaN.

Muốn sửa thư mục này mà không phải chủ: mở PR và cần chủ thư mục đồng ý.
