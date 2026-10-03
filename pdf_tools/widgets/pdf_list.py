"""Tên tương thích cho danh sách PDF; logic chung nằm trong FileList."""
from widgets.file_list import FileList
from widgets.file_picker import Dialogs


class PdfList(FileList):
    def __init__(self, parent, dialogs: Dialogs, reorder=False):
        super().__init__(parent, dialogs, kind='pdf', reorder=reorder)
