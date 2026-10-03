from io import BytesIO
from pathlib import Path
from pypdf import PdfReader, PdfWriter, Transformation
from reportlab.pdfgen.canvas import Canvas
from services.common import OperationResult, ProgressCallback, report
from utils.errors import AppError
from utils.file_utils import atomic_output, check_outputs
from utils.validators import open_pdf, validate_sources, validate_output_dir


def merge_pdf(input_paths: list[str | Path], output_path: str | Path,
              add_page_numbers: bool = False, progress_callback: ProgressCallback | None = None,
              overwrite: bool = False) -> OperationResult:
    """Nối theo thứ tự; số trang theo kích thước hiển thị và rotation thực tế."""
    sources = validate_sources(input_paths, 2)
    target = Path(output_path).expanduser().resolve()
    if target.suffix.lower() != '.pdf':
        raise AppError("File kết quả phải có đuôi .pdf.")
    validate_output_dir(target.parent)
    check_outputs([target], sources, overwrite)
    writer = PdfWriter()
    for index, source in enumerate(sources, 1):
        with open_pdf(source) as reader:
            writer.append(reader, import_outline=False)
        done = int(70 * index / len(sources)) if add_page_numbers else index
        total = 100 if add_page_numbers else len(sources)
        report(progress_callback, done, total, f"Đang nối file {index}/{len(sources)}...")
    if add_page_numbers:
        for number, page in enumerate(writer.pages, 1):
            if page.rotation:
                page.transfer_rotation_to_content()
            # Cropbox là phần thực sự nhìn thấy; hỗ trợ origin khác 0.
            box = page.cropbox
            width, height = float(box.width), float(box.height)
            buffer = BytesIO()
            canvas = Canvas(buffer, pagesize=(width, height))
            canvas.setFont('Helvetica', 10)
            canvas.drawCentredString(width / 2, min(14, height / 20), str(number))
            canvas.save()
            buffer.seek(0)
            overlay = PdfReader(buffer).pages[0]
            page.merge_transformed_page(overlay, Transformation().translate(float(box.left), float(box.bottom)))
            report(progress_callback, 70 + int(30 * number / len(writer.pages)), 100,
                   f"Đang đánh số trang {number}/{len(writer.pages)}...")
    with atomic_output(target, overwrite) as temporary:
        writer.write(temporary)
    return OperationResult([target])
