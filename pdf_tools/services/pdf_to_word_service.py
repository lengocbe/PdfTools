"""PDF sang DOCX bằng Word COM offline."""
from pathlib import Path
from services.common import OperationResult, ProgressCallback
from services.word_com import load_com, convert_documents
from utils.file_utils import check_outputs
from utils.validators import validate_output_dir, validate_sources

WORD_REQUIRED = 'Không tìm thấy Microsoft Word. Chức năng PDF sang Word yêu cầu Microsoft Word được cài trên máy.'


def validate_word_request(input_paths, output_dir, overwrite=False) -> tuple[list[Path], list[Path]]:
    sources = validate_sources(input_paths, 1)
    folder = validate_output_dir(output_dir)
    outputs = [folder / f'{source.stem}.docx' for source in sources]
    check_outputs(outputs, sources, overwrite)
    return sources, outputs


def _load_com():
    return load_com(WORD_REQUIRED)


def pdf_to_word(input_paths: list[str | Path], output_dir: str | Path, overwrite: bool = False,
                progress_callback: ProgressCallback | None = None) -> OperationResult:
    """Mỗi PDF tạo một DOCX; batch trả cả các file thành công và lỗi."""
    sources, targets = validate_word_request(input_paths, output_dir, overwrite)
    return convert_documents(sources, targets, 'DOCX', overwrite, progress_callback, _load_com, WORD_REQUIRED)
