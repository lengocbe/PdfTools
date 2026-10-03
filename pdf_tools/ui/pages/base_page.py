"""Tiện ích bố cục và gửi yêu cầu service; không chứa xử lý PDF."""
import tkinter as tk
from tkinter import ttk, messagebox
from widgets.file_picker import FilePicker
from widgets.folder_picker import FolderPicker


class BasePage(ttk.Frame):
    def __init__(self,parent,app,title,description):
        super().__init__(parent,padding=(24,18))
        self.app = app
        self.title = title
        ttk.Label(self,text=title,style='Title.TLabel').pack(anchor='w')
        ttk.Label(self,text=description,wraplength=690,style='Description.TLabel').pack(anchor='w',pady=(5,14))
        self.bind('<Configure>',self._resize_labels)

    def _resize_labels(self,event):
        for child in self.winfo_children():
            if isinstance(child,ttk.Label) and child.cget('wraplength'):
                child.configure(wraplength=max(300,event.width-40))

    def group(self,title):
        card = ttk.Frame(self,padding=(14,10),style='Card.TFrame')
        card.pack(fill='x',pady=(0,16))
        ttk.Label(card,text=title,style='Card.Title.TLabel').pack(anchor='w',pady=(0,8))
        frame = ttk.Frame(card,style='Card.TFrame')
        frame.pack(fill='x')
        return frame

    def source_picker(self):
        picker = FilePicker(self.group('PDF nguồn'),self.app.dialogs)
        picker.pack(fill='x')
        return picker

    def folder_picker(self,title='Thư mục xuất'):
        picker = FolderPicker(self.group(title),self.app.dialogs)
        picker.pack(fill='x')
        return picker

    def overwrite_option(self,text='Ghi đè file cùng tên nếu đã có'):
        value = tk.BooleanVar(value=False)
        ttk.Checkbutton(self,text=text,variable=value).pack(anchor='w',pady=(0,8))
        return value

    def action(self,text,command):
        ttk.Button(self,text=text.upper(),command=command,style='Action.TButton').pack(anchor='e',pady=(4,2))

    def run_service(self,function,**kwargs):
        self.app.run_task(self,function,kwargs)

    def form_error(self,message):
        messagebox.showerror('Thông tin chưa hợp lệ',message,parent=self.app)

    def refresh_state(self):
        """Các page có input phụ thuộc tùy chọn có thể override."""
