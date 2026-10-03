from tkinter import ttk
from ui.pages.base_page import BasePage
from widgets.pdf_list import PdfList
from services.pdf_to_word_service import pdf_to_word


class PdfToWordPage(BasePage):
    def __init__(self,parent,app):
        super().__init__(parent,app,'PDF → Word','Mỗi PDF tạo một DOCX cùng tên. Tài liệu được xử lý trên máy, không tải lên Internet.')
        self.files = PdfList(self.group('Danh sách PDF'),app.dialogs)
        self.files.pack(fill='both',expand=True)
        self.folder = self.folder_picker('Thư mục lưu Word')
        self.overwrite = self.overwrite_option('Ghi đè file Word cùng tên nếu đã có')
        ttk.Label(self,wraplength=690,text='Lưu ý: chức năng này sử dụng Microsoft Word. PDF quét dạng ảnh có thể không chuyển đổi được nội dung chữ chính xác.').pack(anchor='w',pady=(0,10))
        self.action('Chuyển sang Word',self.submit)

    def submit(self):
        self.run_service(pdf_to_word,input_paths=self.files.paths(),output_dir=self.folder.value.get(),overwrite=self.overwrite.get())
