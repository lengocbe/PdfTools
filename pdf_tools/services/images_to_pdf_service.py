"""Ghép ảnh thành PDF theo thứ tự, một ảnh một trang, không kéo méo."""
from pathlib import Path
from PIL import Image, ImageOps, UnidentifiedImageError
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen.canvas import Canvas
from services.common import OperationResult, ProgressCallback, report
from utils.errors import AppError
from utils.file_utils import atomic_output, check_outputs
from utils.validators import validate_file, validate_output_dir, IMAGE_EXTENSIONS

IMAGE_PAGE_DPI = 150


def images_to_pdf(input_paths: list[str | Path], output_path: str | Path, overwrite: bool = False,
                  progress_callback: ProgressCallback | None = None) -> OperationResult:
    """Mỗi file lấy ảnh/frame đầu; EXIF được áp dụng, alpha có nền trắng."""
    if not input_paths:
        raise AppError('Vui lòng chọn ít nhất 1 ảnh.')
    sources = [validate_file(path, IMAGE_EXTENSIONS, 'ảnh') for path in input_paths]
    target = Path(output_path).expanduser().resolve()
    if target.suffix.lower() != '.pdf':
        raise AppError('File kết quả phải có đuôi .pdf.')
    validate_output_dir(target.parent)
    check_outputs([target], sources, overwrite)
    with atomic_output(target, overwrite) as temporary:
        canvas = Canvas(str(temporary))
        for index, source in enumerate(sources, 1):
            try:
                with Image.open(source) as original:
                    with ImageOps.exif_transpose(original) as oriented:
                        with oriented.convert('RGBA') as rgba:
                            with Image.new('RGB', rgba.size, 'white') as rgb:
                                alpha = rgba.getchannel('A')
                                try:
                                    rgb.paste(rgba, mask=alpha)
                                finally:
                                    alpha.close()
                                width, height = (dimension * 72 / IMAGE_PAGE_DPI for dimension in rgb.size)
                                canvas.setPageSize((width, height))
                                canvas.drawImage(ImageReader(rgb), 0, 0, width=width, height=height)
                                canvas.showPage()
            except (UnidentifiedImageError, OSError, ValueError, Image.DecompressionBombError) as exc:
                raise AppError(f"Không đọc được ảnh '{source.name}'. File có thể bị hỏng hoặc quá lớn.") from exc
            report(progress_callback, index, len(sources), f'Đang ghép ảnh {index}/{len(sources)}...')
        canvas.save()
    return OperationResult([target])
