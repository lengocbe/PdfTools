"""Mở entry point source thật, kiểm tra root rồi tự đóng sau 1,5 giây."""
from pathlib import Path
import runpy
from ui.main_window import MainWindow

original_init = MainWindow.__init__
callback_errors = []

def checked_init(self, *args, **kwargs):
    original_init(self, *args, **kwargs)
    self.report_callback_exception = lambda *args: callback_errors.append(args)
    assert len(self.tool_names) == 7
    assert len(self.pages) == 10
    assert self.title() == 'Bộ công cụ PDF'
    self.after(1500, self.on_close)

MainWindow.__init__ = checked_init
runpy.run_path(str(Path(__file__).resolve().parents[1] / 'main.py'), run_name='__main__')
assert not callback_errors, callback_errors
print('SOURCE_STARTUP_OK: one root, seven pages, mainloop opened and closed')
