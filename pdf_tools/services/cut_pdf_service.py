from pathlib import Path
from pypdf import PdfWriter
from services.common import OperationResult, ProgressCallback, report
from utils.page_range import parse_range_groups
from utils.validators import open_pdf, validate_output_dir, validate_pdf
from utils.file_utils import atomic_output, check_outputs


def cut_pdf(input_path: str | Path, ranges: str, output_dir: str | Path,
            progress_callback: ProgressCallback | None = None, overwrite: bool = False) -> OperationResult:
    """Mỗi khoảng tạo một PDF riêng, không sửa nguồn."""
    source = validate_pdf(input_path)
    folder = validate_output_dir(output_dir)
    with open_pdf(source) as reader:
        groups = parse_range_groups(ranges, len(reader.pages))
        outputs = [folder / f"{source.stem}_p{a}{'-' + str(b) if a != b else ''}.pdf" for a, b in groups]
        check_outputs(outputs, [source], overwrite)
        for index, ((first, last), target) in enumerate(zip(groups, outputs), 1):
            writer = PdfWriter()
            for page in range(first - 1, last):
                writer.add_page(reader.pages[page])
                report(progress_callback, index - 1, len(groups), f"Đang cắt trang {page + 1}...")
            with atomic_output(target, overwrite) as temporary:
                writer.write(temporary)
            report(progress_callback, index, len(groups), f"Đã tạo {index}/{len(groups)} file PDF.")
    return OperationResult(outputs)
