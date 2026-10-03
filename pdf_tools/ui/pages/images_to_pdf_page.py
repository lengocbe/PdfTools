from ui.pages.base_page import BasePage
from widgets.file_list import FileList
from widgets.file_picker import FilePicker
from services.images_to_pdf_service import images_to_pdf


class ImagesToPdfPage(BasePage):
    """Danh sách ảnh theo thứ tự, mỗi ảnh là một trang PDF."""
    def __init__(self,parent,app):
        super().__init__(parent,app,'Ảnh → PDF','Ghép ảnh thành một PDF: mỗi ảnh một trang theo thứ tự từ trên xuống, giữ tỉ lệ và nền trắng.')
        self.files = FileList(self.group('Danh sách ảnh'),app.dialogs,kind='image',reorder=True)
        self.files.pack(fill='both',expand=True)
        self.target = FilePicker(self.group('File PDF kết quả'),app.dialogs,output=True,output_name='Anh_da_ghep.pdf')
        self.target.pack(fill='x')
        self.overwrite = self.overwrite_option()
        self.action('Tạo PDF từ ảnh',self.submit)

    def submit(self):
        self.run_service(images_to_pdf,input_paths=self.files.paths(),output_path=self.target.value.get(),
                         overwrite=self.overwrite.get())
