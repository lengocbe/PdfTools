from pathlib import Path
import pypdfium2 as pdfium
from services.common import OperationResult, ProgressCallback, report
from utils.errors import AppError
from utils.file_utils import atomic_output, check_outputs
from utils.page_range import parse_pages
from utils.validators import open_pdf, validate_pdf, validate_output_dir


def pdf_to_images(input_path: str | Path, output_dir: str | Path, pages: str | None = None,
                  image_format: str = 'PNG', dpi: int = 200, overwrite: bool = False,
                  progress_callback: ProgressCallback | None = None) -> OperationResult:
    """Render lần lượt để giới hạn bộ nhớ; pages=None nghĩa là mọi trang."""
    source = validate_pdf(input_path)
    folder = validate_output_dir(output_dir)
    image_format = image_format.upper()
    if image_format not in ('PNG', 'JPEG'):
        raise AppError("Định dạng ảnh phải là PNG hoặc JPEG.")
    if type(dpi) is not int or not 96 <= dpi <= 600:
        raise AppError("DPI phải là số nguyên từ 96 đến 600.")
    with open_pdf(source) as reader:
        total = len(reader.pages)
    selected = list(range(1, total + 1)) if pages is None else parse_pages(pages, total)
    extension = 'png' if image_format == 'PNG' else 'jpg'
    padding = max(3, len(str(total)))
    outputs = [folder / f'{source.stem}_page_{number:0{padding}d}.{extension}' for number in selected]
    check_outputs(outputs, [source], overwrite)
    with pdfium.PdfDocument(source) as document:
        for index, (number, target) in enumerate(zip(selected, outputs), 1):
            page = document[number - 1]
            try:
                bitmap = page.render(scale=dpi / 72, fill_color=(255, 255, 255, 255))
                try:
                    image = bitmap.to_pil()
                    converted = None
                    try:
                        if image_format == 'JPEG':
                            converted = image.convert('RGB')
                        with atomic_output(target, overwrite) as temporary:
                            (converted or image).save(temporary, format=image_format,
                                                      **({'quality': 90} if image_format == 'JPEG' else {}))
                    finally:
                        if converted is not None:
                            converted.close()
                        image.close()
                finally:
                    bitmap.close()
            finally:
                page.close()
            report(progress_callback, index, len(selected), f"Đang xuất trang {number} ({index}/{len(selected)})...")
    return OperationResult(outputs)
