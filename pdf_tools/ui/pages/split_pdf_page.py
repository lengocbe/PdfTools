import tkinter as tk
from tkinter import ttk
from ui.pages.base_page import BasePage
from services.split_pdf_service import split_pdf


class SplitPdfPage(BasePage):
    def __init__(self,parent,app):
        super().__init__(parent,app,'Tách từng trang','Mỗi trang tạo một PDF. File text lưu danh sách tên PDF bằng UTF-8.')
        self.source = self.source_picker()
        group = self.group('Tên file kết quả')
        group.columnconfigure(1,weight=1)
        self.prefix = tk.StringVar(value='bl')
        self.start = tk.StringVar(value='1')
        self.list_name = tk.StringVar(value='danh_sach_file_pdf.txt')
        for row,(label,value) in enumerate([('Tiền tố',self.prefix),('Số bắt đầu',self.start),('Tên file text',self.list_name)]):
            ttk.Label(group,text=label).grid(row=row,column=0,sticky='w',padx=(0,16),pady=4)
            ttk.Entry(group,textvariable=value).grid(row=row,column=1,sticky='ew',pady=4)
        self.folder = self.folder_picker()
        self.overwrite = self.overwrite_option()
        self.action('Tách từng trang',self.submit)

    def submit(self):
        try:
            start = int(self.start.get())
        except ValueError:
            self.form_error('Số bắt đầu phải là số nguyên không âm.')
            return
        self.run_service(split_pdf,input_path=self.source.value.get(),output_dir=self.folder.value.get(),
                         prefix=self.prefix.get(),start_number=start,list_filename=self.list_name.get(),
                         overwrite=self.overwrite.get())
