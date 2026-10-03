"""Worker gửi sự kiện qua queue, tuyệt đối không gọi Tkinter."""
from dataclasses import dataclass
import logging
from queue import Queue, Empty
from threading import Thread
from typing import Callable, Any
from utils.errors import AppError


@dataclass(frozen=True)
class WorkerEvent:
    kind: str
    payload: Any


class Worker:
    """Một job tại một thời điểm; UI gọi drain() từ root.after."""
    def __init__(self):
        self.events: Queue[WorkerEvent] = Queue()
        self.thread: Thread | None = None

    def start(self, function: Callable, **kwargs) -> None:
        if self.thread is not None and self.thread.is_alive():
            raise AppError("Một tác vụ khác đang chạy.")

        def progress(done: int, total: int, text: str):
            self.events.put(WorkerEvent('progress', (done, total, text)))

        def run():
            logger = logging.getLogger(__name__)
            logger.info("Bắt đầu %s: %s", function.__name__, kwargs)
            try:
                result = function(**kwargs, progress_callback=progress)
                logger.info("Hoàn tất %s: %s", function.__name__, result)
                self.events.put(WorkerEvent('success', result))
            except Exception as exc:
                logger.exception("Tác vụ %s thất bại", function.__name__)
                if isinstance(exc, AppError):
                    message = str(exc)
                elif isinstance(exc, PermissionError):
                    message = "Không có quyền ghi hoặc file đang được chương trình khác sử dụng."
                elif isinstance(exc, OSError):
                    message = "Không đọc/ghi được file. Hãy kiểm tra dung lượng, quyền truy cập và đường dẫn."
                else:
                    message = "Không xử lý được tài liệu. File có thể bị hỏng. Chi tiết đã được ghi vào log."
                self.events.put(WorkerEvent('error', message))
        self.thread = Thread(target=run, name='PDFToolsWorker', daemon=False)
        self.thread.start()

    def drain(self) -> list[WorkerEvent]:
        result = []
        while True:
            try:
                result.append(self.events.get_nowait())
            except Empty:
                return result
