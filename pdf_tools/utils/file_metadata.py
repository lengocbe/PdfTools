"""Đọc thông tin PDF độc lập với giao diện; được gọi trong thread nền."""
from pathlib import Path
from utils.validators import open_pdf


def describe_pdf(path: str) -> str:
    """Trả dung lượng và số trang, giữ thông báo validation dễ hiểu."""
    source = Path(path)
    size = source.stat().st_size
    size_text = f'{size / (1024 ** 2):.1f} MB' if size >= 1024 ** 2 else f'{size / 1024:.1f} KB'
    with open_pdf(source) as reader:
        return f'{size_text} · {len(reader.pages)} trang'
