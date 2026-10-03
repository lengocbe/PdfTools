"""Bootstrap: logging, settings và một root window."""
import logging
from config.settings import Settings
from utils.logging_config import configure_logging
from ui.main_window import MainWindow


def run() -> None:
    configure_logging()
    logging.getLogger(__name__).info('Ứng dụng bắt đầu')
    window = MainWindow(Settings())
    window.mainloop()
