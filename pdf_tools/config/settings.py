"""Cấu hình nhẹ, lỗi dữ liệu sẽ dùng giá trị mặc định."""
import json
import logging
import os
from pathlib import Path

APP_NAME = "Bộ công cụ PDF"
APP_DIR = Path(os.environ.get("LOCALAPPDATA", Path.home() / "AppData" / "Local")) / "PDFTools"
DEFAULTS = {"last_pdf_folder": "", "last_word_folder": "", "last_image_folder": "",
            "last_output_folder": "", "window_width": 1100,
            "window_height": 720, "image_dpi": 200, "image_format": "PNG"}


class Settings:
    def __init__(self, path: Path | None = None):
        self.path = path or APP_DIR / "settings.json"
        self.values = DEFAULTS.copy()
        try:
            loaded = json.loads(self.path.read_text(encoding="utf-8"))
            if isinstance(loaded, dict):
                for key, default in DEFAULTS.items():
                    value = loaded.get(key, default)
                    if type(value) is type(default):
                        self.values[key] = value
        except (OSError, ValueError):
            logging.getLogger(__name__).debug("Dùng cấu hình mặc định", exc_info=True)
        for key, minimum, maximum in [("window_width", 900, 5000), ("window_height", 600, 3000),
                                      ("image_dpi", 96, 600)]:
            self.values[key] = min(maximum, max(minimum, self.values[key]))
        if self.values["image_format"] not in ("PNG", "JPEG"):
            self.values["image_format"] = "PNG"

    def get(self, key: str):
        return self.values[key]

    def set(self, key: str, value):
        self.values[key] = value

    def save(self):
        try:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            temporary = self.path.with_suffix(".tmp")
            temporary.write_text(json.dumps(self.values, ensure_ascii=False, indent=2), encoding="utf-8")
            temporary.replace(self.path)
        except OSError:
            logging.getLogger(__name__).exception("Không lưu được cấu hình")
