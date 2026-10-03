"""Ghi file tạm cùng thư mục, không ghi đè ngầm và bảo vệ nguồn."""
from contextlib import contextmanager
from pathlib import Path
import os
import tempfile
from utils.errors import AppError


def check_outputs(outputs: list[Path], sources=(), overwrite: bool = False) -> None:
    keys = [os.path.normcase(str(p.resolve())) for p in outputs]
    source_keys = {os.path.normcase(str(Path(p).resolve())) for p in sources}
    if len(set(keys)) != len(keys):
        raise AppError("Các tên file xuất bị trùng nhau. Hãy điều chỉnh đầu vào.")
    for path, key in zip(outputs, keys):
        if key in source_keys:
            raise AppError(f"File xuất trùng PDF nguồn: {path}")
        if path.exists() and (not overwrite or not path.is_file()):
            raise AppError(f"File đã tồn tại: {path.name}. Hãy chọn tên khác hoặc bật Ghi đè.")


@contextmanager
def atomic_output(target: Path, overwrite: bool = False):
    """Chỉ công bố file khi ghi thành công; rename không ghi đè trên Windows."""
    target = Path(target)
    check_outputs([target], overwrite=overwrite)
    fd, name = tempfile.mkstemp(prefix=".pdftools-", suffix=target.suffix, dir=target.parent)
    os.close(fd)
    temporary = Path(name)
    try:
        yield temporary
        if overwrite:
            os.replace(temporary, target)
        elif os.name == "nt":
            os.rename(temporary, target)
        else:
            os.link(temporary, target)
            temporary.unlink()
    finally:
        temporary.unlink(missing_ok=True)
