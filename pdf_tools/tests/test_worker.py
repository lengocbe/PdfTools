from threading import get_ident
from services.common import OperationResult
from utils.worker import Worker
from utils.errors import AppError

def test_worker_separate_thread():
    caller = get_ident()
    worker = Worker()
    def task(progress_callback):
        assert get_ident() != caller
        progress_callback(1,1,'done')
        return OperationResult()
    worker.start(task)
    worker.thread.join(timeout=5)
    assert not worker.thread.is_alive()
    assert [event.kind for event in worker.drain()] == ['progress','success']

def test_worker_friendly_error():
    def task(progress_callback):
        raise AppError('Lỗi đầu vào')
    worker = Worker()
    worker.start(task)
    worker.thread.join(timeout=5)
    event = worker.drain()[0]
    assert event.kind == 'error'
    assert event.payload == 'Lỗi đầu vào'
