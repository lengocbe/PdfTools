import tkinter as tk
from tkinter import ttk
from ui.pages.base_page import BasePage
from services.pdf_to_image_service import pdf_to_images


class PdfToImagePage(BasePage):
    def __init__(self,parent,app):
        super().__init__(parent,app,'PDF → Ảnh','Xuất ảnh theo kích thước trang gốc. DPI càng cao, ảnh càng lớn và cần nhiều bộ nhớ.')
        self.source = self.source_picker()
        group = self.group('Trang cần xuất')
        self.mode = tk.StringVar(value='all')
        self.pages = tk.StringVar()
        ttk.Radiobutton(group,text='Xuất toàn bộ trang',value='all',variable=self.mode,command=self.refresh_state).pack(anchor='w')
        ttk.Radiobutton(group,text='Chỉ xuất các trang này',value='selected',variable=self.mode,command=self.refresh_state).pack(anchor='w',pady=4)
        self.entry = ttk.Entry(group,textvariable=self.pages)
        self.entry.pack(fill='x')
        ttk.Label(group,text='Ví dụ: 1,3,5-8').pack(anchor='w',pady=(4,0))
        options = self.group('Định dạng ảnh')
        self.format = tk.StringVar(value=app.settings.get('image_format'))
        self.dpi = tk.StringVar(value=str(app.settings.get('image_dpi')))
        ttk.Label(options,text='Định dạng').pack(side='left',padx=(0,8))
        ttk.Combobox(options,textvariable=self.format,values=['PNG','JPEG'],state='readonly',width=9).pack(side='left')
        ttk.Label(options,text='DPI').pack(side='left',padx=(20,8))
        ttk.Combobox(options,textvariable=self.dpi,values=[96,150,200,300,600],state='readonly',width=9).pack(side='left')
        self.folder = self.folder_picker()
        self.overwrite = self.overwrite_option()
        self.action('Xuất ảnh',self.submit)
        self.refresh_state()

    def refresh_state(self):
        self.entry.configure(state='normal' if self.mode.get() == 'selected' else 'disabled')

    def submit(self):
        self.app.settings.set('image_format',self.format.get())
        self.app.settings.set('image_dpi',int(self.dpi.get()))
        self.app.settings.save()
        self.run_service(pdf_to_images,input_path=self.source.value.get(),output_dir=self.folder.value.get(),
                         pages=None if self.mode.get() == 'all' else self.pages.get(),
                         image_format=self.format.get(),dpi=int(self.dpi.get()),overwrite=self.overwrite.get())
