from tkinter import ttk
from ui.pages.base_page import BasePage
from widgets.file_list import FileList
from services.word_to_pdf_service import word_to_pdf


class WordToPdfPage(BasePage):
    """Nhiều Word thành PDF cùng tên, xử lý offline qua worker."""
    def __init__(self,parent,app):
        super().__init__(parent,app,'Word → PDF','Mỗi tài liệu Word tạo một PDF cùng tên. Hỗ trợ .doc và .docx.')
        self.files = FileList(self.group('Danh sách Word'),app.dialogs,kind='word')
        self.files.pack(fill='both',expand=True)
        self.folder = self.folder_picker('Thư mục lưu PDF')
        self.overwrite = self.overwrite_option('Ghi đè file PDF cùng tên nếu đã có')
        ttk.Label(self,text='Yêu cầu Microsoft Word desktop được cài và kích hoạt trên máy.',wraplength=690,
                  style='Description.TLabel').pack(anchor='w',pady=(0,10))
        self.action('Chuyển sang PDF',self.submit)

    def submit(self):
        self.run_service(word_to_pdf,input_paths=self.files.paths(),output_dir=self.folder.value.get(),
                         overwrite=self.overwrite.get())
