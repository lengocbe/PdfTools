"""Hợp đồng kết quả và progress dùng chung cho các dịch vụ."""
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable

ProgressCallback = Callable[[int, int, str], None]


@dataclass
class OperationResult:
    outputs: list[Path] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)


def report(callback: ProgressCallback | None, done: int, total: int, text: str) -> None:
    if callback is not None:
        callback(done, total, text)
