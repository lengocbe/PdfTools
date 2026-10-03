"""Card tiến trình dùng chung, kết quả và mở thư mục xuất."""
import os
from pathlib import Path
import tkinter as tk
from tkinter import ttk, messagebox


class ProgressPanel(ttk.Frame):
    def __init__(self,parent):
        super().__init__(parent,padding=(16,12),style='Card.TFrame')
        self.columnconfigure(0,weight=1)
        self.status = tk.StringVar(value='Sẵn sàng.')
        self.count = tk.StringVar(value='0 / 0')
        self.output_folder = None
        self.label = ttk.Label(self,textvariable=self.status,style='Card.Title.TLabel')
        self.label.grid(row=0,column=0,sticky='w')
        self.bind('<Configure>',lambda event:self.label.configure(wraplength=max(200,event.width-170)))
        self.open_button = ttk.Button(self,text='Mở thư mục',command=self.open_folder)
        self.open_button.grid(row=0,column=1,rowspan=2,padx=(16,0))
        self.open_button.grid_remove()
        ttk.Label(self,text='Tiến trình',style='Card.Muted.TLabel').grid(row=1,column=0,sticky='w',pady=(8,5))
        ttk.Label(self,textvariable=self.count,style='Card.Muted.TLabel').grid(row=1,column=0,sticky='e',pady=(8,5))
        self.bar = ttk.Progressbar(self,maximum=100,mode='determinate')
        self.bar.grid(row=2,column=0,columnspan=2,sticky='ew')

    def start(self):
        self.label.configure(style='Card.Title.TLabel')
        self.output_folder = None
        self.open_button.grid_remove()
        self.count.set('0 / 0')
        self.status.set('Đang kiểm tra và chuẩn bị xử lý...')
        self.bar.configure(mode='indeterminate')
        self.bar.start(15)

    def update_progress(self,done,total,text):
        self.bar.stop()
        self.bar.configure(mode='determinate',value=100 * done / max(total,1))
        self.count.set(f'{done} / {total}')
        self.status.set(text)

    def finish(self,text,success=True,folder=None):
        self.label.configure(style='Success.TLabel' if success else 'Error.TLabel')
        self.bar.stop()
        self.bar.configure(mode='determinate',value=100 if success else 0)
        self.status.set(text)
        self.output_folder = Path(folder) if folder else None
        if self.output_folder:
            self.open_button.grid()

    def open_folder(self):
        if self.output_folder:
            try:
                os.startfile(str(self.output_folder))
            except OSError:
                messagebox.showerror('Không mở được thư mục','Thư mục không tồn tại hoặc không có quyền truy cập.',parent=self)
