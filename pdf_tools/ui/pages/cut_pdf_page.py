import tkinter as tk
from tkinter import ttk
from ui.pages.base_page import BasePage
from services.cut_pdf_service import cut_pdf
from ui.theme import COLORS


class CutPdfPage(BasePage):
    def __init__(self,parent,app):
        super().__init__(parent,app,'Cắt PDF','Mỗi khoảng trang tạo một file PDF riêng. Số trang bắt đầu từ 1.')
        self.source = self.source_picker()
        group = ttk.Frame(self)
        group.pack(fill='x',pady=(0,18))
        ttk.Label(group,text='Khoảng trang cần cắt',style='Section.TLabel').pack(anchor='w',pady=(0,8))
        self.ranges = tk.Text(group,height=3,wrap='word',font=('Segoe UI',10),undo=True,
                              relief='flat',borderwidth=0,highlightthickness=1,highlightbackground=COLORS['border'],
                              highlightcolor=COLORS['teal'],background=COLORS['white'],foreground=COLORS['text'],
                              insertbackground=COLORS['heading'],selectbackground=COLORS['teal'],
                              selectforeground=COLORS['white'],padx=10,pady=6)
        self.ranges.pack(fill='x')
        ttk.Label(group,text='Ví dụ: 3-4, 7-8 hoặc mỗi khoảng một dòng. Trang đơn: 5.').pack(anchor='w',pady=(6,0))
        self.folder = self.folder_picker()
        self.overwrite = self.overwrite_option()
        self.action('Cắt PDF',self.submit)

    def submit(self):
        self.run_service(cut_pdf,input_path=self.source.value.get(),ranges=self.ranges.get('1.0','end').strip(),
                         output_dir=self.folder.value.get(),overwrite=self.overwrite.get())
