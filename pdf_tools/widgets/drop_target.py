"""Đăng ký kéo thả native; callback luôn chạy trên GUI thread."""
from pathlib import Path
from tkinterdnd2 import DND_FILES


def register_drop(widget, callback, extensions: tuple[str, ...]) -> None:
    def dropped(event):
        app = widget.winfo_toplevel()
        if app.busy:
            return 'refuse_drop'
        paths = [str(Path(path)) for path in widget.tk.splitlist(event.data)]
        if paths and all(Path(path).is_file() and Path(path).suffix.lower() in extensions for path in paths):
            callback(paths)
            return 'copy'
        app.show_drop_error(extensions)
        return 'refuse_drop'
    widget.drop_target_register(DND_FILES)
    widget.dnd_bind('<<Drop>>', dropped)
