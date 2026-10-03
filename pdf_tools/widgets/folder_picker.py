import tkinter as tk
from tkinter import ttk
from widgets.file_picker import Dialogs


class FolderPicker(ttk.Frame):
    def __init__(self, parent, dialogs: Dialogs):
        super().__init__(parent)
        self.value = tk.StringVar(value=dialogs.settings.get('last_output_folder'))
        self.columnconfigure(0, weight=1)
        ttk.Entry(self, textvariable=self.value).grid(row=0,column=0,sticky='ew',padx=(0,8))
        def choose():
            path = dialogs.folder()
            if path:
                self.value.set(path)
        ttk.Button(self,text='Chọn thư mục',command=choose).grid(row=0,column=1)
