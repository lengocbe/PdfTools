# BỘ CÔNG CỤ PDF

Ứng dụng Windows offline, một cửa sổ Tkinter + ttk, giao diện tiếng Việt.
Tên chương trình đóng gói: **PDFTools.exe**. Không sử dụng API online, cloud hoặc OCR.

## Chức năng

- **Cắt PDF:** mỗi khoảng trang tạo một PDF riêng. `3-4,7-8` tạo hai file; hỗ trợ dấu phẩy, chấm phẩy và xuống dòng. Số trang bắt đầu từ 1.
- **Nối PDF:** thêm nhiều file, bỏ file, thay đổi thứ tự bằng Lên/Xuống. Checkbox đánh số trang liên tục ở giữa phía dưới trang, hỗ trợ kích thước và rotation khác nhau.
- **Tách từng trang:** tiền tố và số bắt đầu tùy chọn; kèm danh sách tên PDF trong file text UTF-8.
- **PDF → Ảnh:** mọi trang hoặc trang chọn riêng, PNG/JPEG, 96–600 DPI. JPEG nền trắng, quality 90; không thay đổi tỉ lệ trang.
- **PDF → Word:** nhiều PDF thành DOCX cùng tên, sử dụng Microsoft Word COM trên máy. Cần **Microsoft Word desktop 2013 trở lên**, đã cài và kích hoạt; nên dùng phiên bản hiện được Microsoft hỗ trợ. Word Online không đáp ứng yêu cầu.
- **Word → PDF:** thêm nhiều file `.doc`/`.docx`, mỗi file tạo một PDF cùng tên bằng Word COM; có tùy chọn ghi đè. Giữ nguyên nguồn và không tự mở PDF kết quả.
- **Ảnh → PDF:** ghép PNG, JPEG, BMP, TIFF hoặc WebP vào một PDF, mỗi file ảnh là một trang theo thứ tự danh sách. Lên/Xuống thay đổi thứ tự. Trang có tỉ lệ theo ảnh (quy đổi 150 DPI), áp dụng EXIF orientation và nền trắng cho ảnh trong suốt. Với TIFF/WebP nhiều frame, chỉ lấy frame đầu của mỗi file.

Giao diện dùng theme ttk `clam`: sidebar navy chia nhóm, mục đang chọn có nền teal nhạt và thanh nhấn bên trái. Nội dung gồm card trắng trên nền xám rất nhạt; nút chính và progress màu teal. Dòng **Designed by Lê Ngọc Bé** nằm bên phải footer.

Bảng màu: primary `#128C9A`, sidebar `#172A3A`, sidebar hover `#213C50`, active background `#E7F4F5`, app background `#F6F8FB`, card `#FFFFFF`, heading `#16283A`, text `#344054`, secondary text `#667085`, border `#DCE3EA`. Màu được quản lý chung trong `ui/theme.py`; hover nút chính dùng `#0E7480`.

Ô PDF nguồn hỗ trợ kéo thả, hiển thị tên file, dung lượng và số trang; rê chuột lên tên để xem đường dẫn đầy đủ. Thông tin PDF được đọc trên thread nền. Danh sách PDF/Word/ảnh cũng nhận nhiều file kéo thả. Kéo thả sử dụng `tkinterdnd2` với TkDnD native được đóng gói trong EXE. Hai ứng dụng kéo/thả cần chạy cùng mức quyền Windows; nên chạy bình thường, không chọn Run as administrator.

Tiến trình nằm trong card nội dung; hoàn tất hiện số file đã tạo và nút **Mở thư mục**. Trang **Lịch sử xử lý** lưu tối đa 100 tác vụ cùng số file, kết quả và thư mục xuất; **Cài đặt** cho phép đổi DPI/định dạng ảnh mặc định; **Giới thiệu/Trợ giúp** hướng dẫn sử dụng. Vùng nội dung cuộn khi cửa sổ nhỏ, hỗ trợ con lăn và tự cuộn theo focus bàn phím.

Các thao tác chạy trên worker thread. GUI chỉ nhận progress/kết quả qua queue và `after()`. Các trường nhập và menu bị khóa trong khi chạy; ứng dụng yêu cầu chờ tác vụ hoàn tất trước khi đóng để cleanup Word an toàn.

## Cài đặt và chạy source

Cần Python 3.12 64-bit cho Windows với Tkinter (bản cài chính thức từ python.org có Tcl/Tk). Python mới hơn chỉ nên dùng sau khi kiểm tra toàn bộ dependency. Mở terminal trong thư mục `pdf_tools`:

```bat
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

PowerShell kích hoạt bằng `.venv\Scripts\Activate.ps1`; có thể dùng trực tiếp `.venv\Scripts\python.exe main.py` nếu không muốn kích hoạt môi trường. Việc cài dependency lần đầu cần Internet hoặc các wheel offline. Sau khi cài, ứng dụng xử lý tài liệu hoàn toàn offline.

## Kiểm thử

```bat
.venv\Scripts\python.exe -m pytest -q
```

Test tự tạo PDF bằng ReportLab; kiểm tra parser, trang/nội dung/thứ tự, rotation, ảnh, ghi file an toàn, encrypted PDF, settings và worker. Test Word mock kiểm tra Close/Quit/CoUninitialize, gồm lỗi SaveAs và lỗi Quit.

Test GUI và Word thật mặc định skip để chạy được trên CI không có desktop/Word. Trên Windows desktop, bật riêng trong PowerShell:

```powershell
$env:PDFTOOLS_GUI_TEST = '1'
.venv\Scripts\python.exe -m pytest tests/test_gui.py -q
$env:PDFTOOLS_WORD_TEST = '1'
.venv\Scripts\python.exe -m pytest tests/test_word_integration.py -q
```

Word phải hoàn tất thiết lập lần đầu và kích hoạt trước khi chạy test thật. Test sử dụng PDF/DOCX mẫu tự tạo, lưu kết quả trong thư mục tạm.

## Build EXE

Trên Windows, sau khi cài requirements:

```bat
build.bat
```

Hoặc:

```bat
.venv\Scripts\python.exe -m PyInstaller --noconfirm --clean PDFTools.spec
```

Kết quả: **`dist\PDFTools.exe`**, một file EXE, không có cửa sổ console. Có thể chép EXE sang máy Windows 64-bit khác, không cần cài Python. Chức năng Word vẫn cần Microsoft Word desktop trên máy đích. Khởi động lần đầu có thể mất vài giây để giải nén thư viện.

Spec sử dụng hook PyInstaller cho Tcl/Tk, pywin32 và pypdfium2; thu thập PDFium DLL/data, TkDnD và font ReportLab. Nếu `assets/app.ico` không có, build dùng icon mặc định và vẫn hoạt động. Nếu build báo `tkinter installation is broken`, hãy sửa/cài lại Python có Tcl/Tk và build lại; EXE thiếu Tkinter sẽ không chạy được.

## Cấu trúc source

```text
pdf_tools/
├── main.py                    # entry point
├── app.py                     # bootstrap, một MainWindow
├── requirements.txt
├── README.md
├── build.bat
├── PDFTools.spec
├── pytest.ini
├── ui/
│   ├── main_window.py          # sidebar, worker polling, khóa input
│   ├── theme.py                # bảng màu và styles ttk
│   └── pages/
│       ├── base_page.py
│       ├── cut_pdf_page.py
│       ├── merge_pdf_page.py
│       ├── split_pdf_page.py
│       ├── pdf_to_image_page.py
│       ├── pdf_to_word_page.py
│       ├── word_to_pdf_page.py
│       ├── images_to_pdf_page.py
│       └── support_pages.py       # lịch sử, cài đặt, giới thiệu
├── services/
│   ├── common.py               # OperationResult, progress callback
│   ├── cut_pdf_service.py
│   ├── merge_pdf_service.py
│   ├── split_pdf_service.py
│   ├── pdf_to_image_service.py
│   ├── pdf_to_word_service.py
│   ├── word_to_pdf_service.py
│   ├── word_com.py              # COM lifecycle/batch dùng chung
│   └── images_to_pdf_service.py
├── widgets/
│   ├── file_picker.py
│   ├── folder_picker.py
│   ├── pdf_list.py
│   ├── file_list.py             # danh sách chung cho PDF/Word/ảnh
│   ├── progress_panel.py
│   ├── scrollable_content.py
│   ├── drop_target.py
│   └── tooltip.py
├── utils/
│   ├── errors.py
│   ├── page_range.py
│   ├── file_utils.py
│   ├── validators.py
│   ├── worker.py
│   ├── history.py
│   ├── file_metadata.py
│   └── logging_config.py
├── config/settings.py
├── assets/README.md
├── tests/
│   ├── conftest.py
│   ├── test_page_range.py
│   ├── test_cut_pdf.py
│   ├── test_merge_pdf.py
│   ├── test_split_pdf.py
│   ├── test_pdf_to_image.py
│   ├── test_pdf_to_word.py
│   ├── test_word_to_pdf.py
│   ├── test_images_to_pdf.py
│   ├── test_word_integration.py
│   ├── test_worker.py
│   ├── test_safety.py
│   ├── test_gui.py
│   ├── test_history.py
│   └── startup_smoke.py
└── dist/PDFTools.exe            # sinh ra khi build, không commit
```

Mỗi package có `__init__.py`. UI không xử lý PDF; services không import Tkinter. Có thể gọi service độc lập từ script chạy trong thư mục `pdf_tools`, ví dụ:

```python
from services.cut_pdf_service import cut_pdf
result = cut_pdf('hop_dong.pdf', '3-4,7-8', 'thu_muc_co_san')
print(result.outputs)
```

`progress_callback(done, total, text)` là callback thuần Python; không truyền hàm gọi widget trực tiếp từ worker. Mọi số trang trong API/parser đều là 1-based.

## Dữ liệu và cấu hình

- Settings: `%LOCALAPPDATA%\PDFTools\settings.json`; lỗi/mất file thì dùng default.
- Lịch sử: `%LOCALAPPDATA%\PDFTools\history.json`; tối đa 100 tác vụ, không lưu nội dung file.
- Log: `%LOCALAPPDATA%\PDFTools\logs\pdftools.log`, xoay vòng 3 bản, 2 MB/bản. Log chứa đường dẫn tài liệu và stack trace nội bộ; UI chỉ hiện thông báo thân thiện.
- Không sửa/xóa/đổi tên PDF nguồn. Đường dẫn output trùng nguồn bị từ chối kể cả bật ghi đè.
- Mặc định không ghi đè. Chỉ ghi đè khi người dùng bật checkbox. Trước khi chạy, các tên output được kiểm tra; tên trùng trong cùng batch bị từ chối.
- File được ghi vào file tạm cùng thư mục rồi công bố khi hoàn tất. Nếu batch thất bại giữa chừng, các file đã hoàn thành vẫn được giữ; file đang ghi lỗi được dọn. Batch không phải giao dịch rollback toàn bộ.
- Thư mục xuất phải tồn tại và có quyền ghi; hỗ trợ khoảng trắng và tiếng Việt bằng `pathlib.Path`.

## Giới hạn

- Chưa hỗ trợ PDF có mật khẩu, OCR hoặc hủy tác vụ giữa chừng.
- PDF scan không đảm bảo có chữ chỉnh sửa được khi chuyển Word. Chuyển đổi layout phụ thuộc Word và cấu trúc PDF, nên kiểm tra DOCX kết quả.
- Hai hướng chuyển đổi Word dùng chung COM lifecycle/batch trong `services/word_com.py`: instance riêng (`DispatchEx`), tắt hiển thị/alerts, đóng document trong `finally`, Quit Word và giải phóng COM. Nếu Quit không làm instance riêng thoát, cleanup dùng handle process của chính instance đó, không tìm/kill toàn bộ WINWORD.EXE.
- Thiết lập lần đầu, licensing, add-in hoặc hộp thoại ngoài khả năng điều khiển COM của Word có thể làm chuyển đổi chờ. Hoàn tất thiết lập Word trước khi dùng; không có timeout cưỡng bức cho lời gọi COM đang treo.
- 600 DPI cho trang rất lớn có thể dùng nhiều RAM. Ảnh được render/lưu lần lượt để giảm bộ nhớ.
- Số trang đặt cách đáy vùng nhìn thấy khoảng 14 point; có thể trùng footer của tài liệu không có khoảng trống. Đánh số xử lý rotation trước khi ghép overlay.
- Nối/cắt/tách tái tạo cấu trúc PDF và không giữ tính hợp lệ của chữ ký số cũ. Bản nguồn luôn được giữ nguyên.

Dependency trực tiếp: `pypdf`, `reportlab`, `pypdfium2`, `Pillow`, `pywin32`, `tkinterdnd2`; kiểm thử: `pytest`; đóng gói: `PyInstaller`. Các phiên bản thực dùng khi build được ghi trong `VALIDATION.md`.
