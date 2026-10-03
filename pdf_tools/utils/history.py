"""Lịch sử cục bộ giới hạn 100 tác vụ; không lưu nội dung tài liệu."""
from datetime import datetime
import json
import logging
from pathlib import Path


class HistoryStore:
    def __init__(self, path: Path):
        self.path = path
        self.records: list[dict] = []
        try:
            loaded = json.loads(path.read_text(encoding='utf-8'))
            if isinstance(loaded, list):
                self.records = [item for item in loaded if isinstance(item, dict)
                                and all(isinstance(item.get(key), str) for key in ('time', 'task', 'status', 'folder'))
                                and type(item.get('count')) is int][:100]
        except (OSError, ValueError):
            logging.getLogger(__name__).debug('Khởi tạo lịch sử mới', exc_info=True)

    def add(self, task: str, count: int, status: str, folder: str = '') -> None:
        self.records.insert(0, dict(time=datetime.now().strftime('%d/%m/%Y %H:%M:%S'),
                                   task=task, count=count, status=status, folder=folder))
        self.records = self.records[:100]
        try:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            temporary = self.path.with_suffix('.tmp')
            temporary.write_text(json.dumps(self.records, ensure_ascii=False, indent=2), encoding='utf-8')
            temporary.replace(self.path)
        except OSError:
            logging.getLogger(__name__).exception('Không lưu được lịch sử')
