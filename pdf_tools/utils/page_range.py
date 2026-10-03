"""Phân tích trang 1-based, giữ nguyên thứ tự người dùng nhập."""
import re
from utils.errors import AppError


def parse_range_groups(text: str, total_pages: int | None = None) -> list[tuple[int, int]]:
    if not text.strip():
        raise AppError("Vui lòng nhập ít nhất một trang hoặc khoảng trang.")
    if re.search(r'[,;]\s*[,;]', text):
        raise AppError("Có phần tử khoảng trang bị bỏ trống.")
    groups = []
    for token in re.split(r"[,;\r\n]+", text.strip()):
        token = token.strip()
        if not token:
            raise AppError("Có phần tử khoảng trang bị bỏ trống.")
        match = re.fullmatch(r"([0-9]+)\s*(?:-\s*([0-9]+))?", token)
        if not match:
            raise AppError(f"Khoảng trang không hợp lệ: '{token}'. Ví dụ: 1,3,5-8.")
        first = int(match[1])
        last = int(match[2] or match[1])
        if first < 1 or last < 1:
            raise AppError(f"Trang phải lớn hơn 0: '{token}'.")
        if first > last:
            raise AppError(f"Trang đầu phải nhỏ hơn hoặc bằng trang cuối: '{token}'.")
        if total_pages is not None and last > total_pages:
            raise AppError(f"Khoảng '{token}' vượt số trang PDF ({total_pages} trang).")
        groups.append((first, last))
    return groups


def parse_pages(text: str, total_pages: int | None = None) -> list[int]:
    """Mở rộng khoảng và loại trang lặp, giữ thứ tự lần xuất hiện đầu."""
    return list(dict.fromkeys(page for a, b in parse_range_groups(text, total_pages)
                             for page in range(a, b + 1)))
