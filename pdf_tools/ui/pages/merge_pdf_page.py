import tkinter as tk
from tkinter import ttk
from ui.pages.base_page import BasePage
from widgets.pdf_list import PdfList
from widgets.file_picker import FilePicker
from services.merge_pdf_service import merge_pdf


class MergePdfPage(BasePage):
    def __init__(self,parent,app):
        super().__init__(parent,app,'Nối PDF','Thêm ít nhất hai PDF. Thứ tự từ trên xuống là thứ tự nối vào file kết quả.')
        self.files = PdfList(self.group('Danh sách PDF'),app.dialogs,reorder=True)
        self.files.pack(fill='both',expand=True)
        self.target = FilePicker(self.group('File PDF kết quả'),app.dialogs,output=True)
        self.target.pack(fill='x')
        self.numbering = tk.BooleanVar(value=False)
        ttk.Checkbutton(self,text='Đánh số trang liên tục, ở giữa phía dưới trang',variable=self.numbering).pack(anchor='w',pady=(0,8))
        self.overwrite = self.overwrite_option()
        self.action('Nối PDF',self.submit)

    def submit(self):
        self.run_service(merge_pdf,input_paths=self.files.paths(),output_path=self.target.value.get(),
                         add_page_numbers=self.numbering.get(),overwrite=self.overwrite.get())
