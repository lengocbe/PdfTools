from pathlib import Path
from pypdf import PdfWriter
from services.common import OperationResult, ProgressCallback, report
from utils.errors import AppError
from utils.file_utils import atomic_output, check_outputs
from utils.validators import open_pdf, validate_pdf, validate_output_dir, validate_filename


def split_pdf(input_path: str | Path, output_dir: str | Path, prefix: str = 'bl',
              start_number: int = 1, list_filename: str = 'danh_sach_file_pdf.txt',
              overwrite: bool = False, progress_callback: ProgressCallback | None = None) -> OperationResult:
    source = validate_pdf(input_path)
    folder = validate_output_dir(output_dir)
    if type(start_number) is not int or start_number < 0:
        raise AppError("Số bắt đầu phải là số nguyên không âm.")
    validate_filename(prefix + str(start_number) + '.pdf')
    validate_filename(list_filename)
    if Path(list_filename).suffix.lower() != '.txt':
        raise AppError("Tên file danh sách phải có đuôi .txt.")
    with open_pdf(source) as reader:
        outputs = [folder / f'{prefix}{start_number + i}.pdf' for i in range(len(reader.pages))]
        text_path = folder / list_filename
        check_outputs(outputs + [text_path], [source], overwrite)
        for index, (page, target) in enumerate(zip(reader.pages, outputs), 1):
            writer = PdfWriter()
            writer.add_page(page)
            with atomic_output(target, overwrite) as temporary:
                writer.write(temporary)
            report(progress_callback, index, len(outputs), f"Đang tách trang {index}/{len(outputs)}...")
        with atomic_output(text_path, overwrite) as temporary:
            temporary.write_text(''.join(f'{p.name}\n' for p in outputs), encoding='utf-8')
    return OperationResult(outputs + [text_path])
