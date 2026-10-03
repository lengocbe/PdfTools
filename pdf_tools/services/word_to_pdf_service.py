"""Word DOC/DOCX sang PDF bằng Microsoft Word desktop."""
from pathlib import Path
from services.common import OperationResult, ProgressCallback
from services.word_com import load_com, convert_documents
from utils.errors import AppError
from utils.file_utils import check_outputs
from utils.validators import validate_file, validate_output_dir, WORD_EXTENSIONS

WORD_REQUIRED = 'Không tìm thấy Microsoft Word. Chức năng Word sang PDF yêu cầu Microsoft Word được cài trên máy.'


def validate_word_to_pdf_request(input_paths: list[str | Path], output_dir: str | Path,
                                 overwrite: bool = False) -> tuple[list[Path], list[Path]]:
    if not input_paths:
        raise AppError('Vui lòng chọn ít nhất 1 file Word (.doc, .docx).')
    sources = [validate_file(path, WORD_EXTENSIONS, 'Word') for path in input_paths]
    folder = validate_output_dir(output_dir)
    outputs = [folder / f'{source.stem}.pdf' for source in sources]
    check_outputs(outputs, sources, overwrite)
    return sources, outputs


def _load_com():
    return load_com(WORD_REQUIRED)


def word_to_pdf(input_paths: list[str | Path], output_dir: str | Path, overwrite: bool = False,
                progress_callback: ProgressCallback | None = None) -> OperationResult:
    """Mỗi Word tạo một PDF, giữ nguyên nguồn và xử lý trên worker."""
    sources, targets = validate_word_to_pdf_request(input_paths, output_dir, overwrite)
    return convert_documents(sources, targets, 'PDF', overwrite, progress_callback, _load_com, WORD_REQUIRED)
