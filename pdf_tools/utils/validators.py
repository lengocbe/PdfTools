"""Validation thuần Python, không phụ thuộc GUI."""
from contextlib import contextmanager
from pathlib import Path
import re
import tempfile
from pypdf import PdfReader
from utils.errors import AppError

WORD_EXTENSIONS = ('.doc', '.docx')
IMAGE_EXTENSIONS = ('.png', '.jpg', '.jpeg', '.bmp', '.tif', '.tiff', '.webp')


def validate_file(path: str | Path, extensions: tuple[str, ...], label: str) -> Path:
    """Kiểm tra file nguồn theo định dạng, dùng chung cho Word và ảnh."""
    source = Path(path).expanduser()
    if source.suffix.lower() not in extensions:
        raise AppError(f"Định dạng {label} không được hỗ trợ: {source.name}.")
    if not source.is_file():
        raise AppError(f"Không tìm thấy {label}: {source}")
    return source.resolve()


def validate_pdf(path: str | Path) -> Path:
    path = Path(path).expanduser()
    if path.suffix.lower() != ".pdf":
        raise AppError(f"Vui lòng chọn file .pdf: {path.name}")
    if not path.is_file():
        raise AppError(f"Không tìm thấy PDF: {path}")
    return path.resolve()


@contextmanager
def open_pdf(path: str | Path):
    path = validate_pdf(path)
    with path.open("rb") as stream:
        try:
            reader = PdfReader(stream)
            if reader.is_encrypted:
                raise AppError("PDF được bảo vệ bằng mật khẩu và hiện chưa được hỗ trợ.")
            if not len(reader.pages):
                raise AppError("PDF không có trang.")
        except AppError:
            raise
        except Exception as exc:
            raise AppError(f"Không đọc được PDF '{path.name}'. File có thể bị hỏng.") from exc
        yield reader


def validate_output_dir(path: str | Path) -> Path:
    if not str(path).strip():
        raise AppError("Vui lòng chọn thư mục xuất.")
    folder = Path(path).expanduser().resolve()
    if not folder.is_dir():
        raise AppError(f"Thư mục xuất không tồn tại: {folder}")
    try:
        with tempfile.TemporaryFile(dir=folder):
            pass
    except OSError as exc:
        raise AppError(f"Không có quyền ghi vào thư mục: {folder}") from exc
    return folder


def validate_filename(name: str) -> str:
    if (not name or name in (".", "..") or re.search(r'[<>:"/\\|?*\x00-\x1f]', name)
            or name.endswith((" ", ".")) or len(name) > 180
            or re.fullmatch(r"(?i)(CON|PRN|AUX|NUL|COM[1-9]|LPT[1-9])(?:\..*)?", name)):
        raise AppError(f"Tên file không hợp lệ trên Windows: '{name}'.")
    return name


def validate_sources(paths, minimum: int) -> list[Path]:
    result = [validate_pdf(path) for path in paths]
    if len(result) < minimum:
        raise AppError(f"Vui lòng chọn ít nhất {minimum} file PDF.")
    return result
