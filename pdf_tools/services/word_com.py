"""Lifecycle COM/Word và batch dùng chung cho hai hướng chuyển đổi."""
from contextlib import contextmanager
import logging
from pathlib import Path
from typing import Callable
from services.common import OperationResult, ProgressCallback, report
from utils.errors import AppError
from utils.file_utils import atomic_output
from utils.validators import open_pdf

LOGGER = logging.getLogger(__name__)
DOCX_FORMAT = 16
PDF_FORMAT = 17


def load_com(required_message: str) -> tuple:
    try:
        import pythoncom
        import win32com.client
        import win32api
        import win32event
        import win32process
    except ImportError as exc:
        raise AppError(required_message) from exc
    return pythoncom, win32com.client, win32api, win32event, win32process


@contextmanager
def word_session(com_loader: Callable, required_message: str):
    """Tạo instance riêng, đảm bảo Quit/cleanup và CoUninitialize."""
    pythoncom, client, api, event, process = com_loader()
    pythoncom.CoInitialize()
    word = None
    handle = None
    try:
        try:
            word = client.DispatchEx('Word.Application')
        except Exception as exc:
            raise AppError(required_message) from exc
        word.Visible = False
        word.DisplayAlerts = 0
        word.AutomationSecurity = 3
        bootstrap = word.Documents.Add(Visible=False)
        try:
            _, pid = process.GetWindowThreadProcessId(bootstrap.Windows.Item(1).Hwnd)
            handle = api.OpenProcess(0x00100000 | 0x0001, False, pid)
        finally:
            try:
                bootstrap.Close(SaveChanges=0)
            finally:
                bootstrap = None
        yield word
    finally:
        try:
            if word is not None:
                try:
                    word.Quit(SaveChanges=0)
                except Exception:
                    LOGGER.exception('Word.Quit thất bại; cleanup instance riêng')
                finally:
                    word = None
            if handle is not None:
                try:
                    if event.WaitForSingleObject(handle, 5000) == 258:
                        LOGGER.warning('Kết thúc instance Word riêng chưa thoát')
                        api.TerminateProcess(handle, 1)
                        event.WaitForSingleObject(handle, 5000)
                finally:
                    handle.Close()
        finally:
            pythoncom.CoUninitialize()


def convert_documents(sources: list[Path], targets: list[Path], output_format: str,
                      overwrite: bool, progress_callback: ProgressCallback | None,
                      com_loader: Callable, required_message: str) -> OperationResult:
    """Chuyển batch; tiếp tục file kế tiếp khi lỗi có thể phục hồi."""
    result = OperationResult()
    with word_session(com_loader, required_message) as word:
        for index, (source, target) in enumerate(zip(sources, targets), 1):
            document = None
            close_failed = False
            try:
                report(progress_callback, index - 1, len(sources),
                       f'Đang chuyển {source.name} ({index}/{len(sources)})...')
                if source.suffix.lower() == '.pdf':
                    with open_pdf(source):
                        pass
                with atomic_output(target, overwrite) as temporary:
                    try:
                        document = word.Documents.Open(FileName=str(source), ConfirmConversions=False,
                                                       ReadOnly=True, AddToRecentFiles=False,
                                                       Visible=False, NoEncodingDialog=True)
                        if output_format == 'DOCX':
                            document.SaveAs2(FileName=str(temporary), FileFormat=DOCX_FORMAT,
                                             AddToRecentFiles=False)
                        else:
                            document.ExportAsFixedFormat(OutputFileName=str(temporary),
                                                         ExportFormat=PDF_FORMAT, OpenAfterExport=False)
                    finally:
                        if document is not None:
                            try:
                                document.Close(SaveChanges=0)
                            except Exception:
                                close_failed = True
                                LOGGER.exception('Không đóng được document %s', source)
                                raise
                            finally:
                                document = None
                    if output_format == 'PDF':
                        with open_pdf(temporary):
                            pass
                result.outputs.append(target)
            except Exception as exc:
                LOGGER.exception('Word conversion thất bại: %s -> %s', source, target)
                detail = str(exc) if isinstance(exc, AppError) else 'Microsoft Word không chuyển đổi được file này.'
                result.errors.append(f'{source.name}: {detail}')
                if close_failed:
                    result.errors.append('Đã dừng batch để đóng Microsoft Word an toàn.')
                    break
            report(progress_callback, index, len(sources),
                   f'Đã xử lý {index}/{len(sources)} file sang {output_format}.')
    return result
