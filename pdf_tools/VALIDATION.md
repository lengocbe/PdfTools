# Kết quả kiểm tra

Ngày kiểm tra cập nhật: 03/10/2026, Windows 11 64-bit, Python 3.12.14.

## Dependency thực tế

| Thư viện | Phiên bản |
|---|---|
| pypdf | 6.10.0 |
| reportlab | 4.4.9 |
| pypdfium2 | 5.13.0 |
| Pillow | 12.3.0 |
| tkinterdnd2 | 0.6.3 |
| pywin32 | 312 |
| pytest | 9.1.1 |
| PyInstaller | 6.22.3 |

## Đã xác nhận

- `python -m pytest -q`: **62 passed, 7 skipped**. Các test skip là 5 test desktop và 2 integration Word opt-in. Pytest dùng thư mục tạm/cache riêng trong project để tránh quyền truy cập của thư mục tạm từ môi trường sandbox cũ.
- Chạy toàn bộ với `PDFTOOLS_GUI_TEST=1`: **67 passed, 2 skipped** (Word thật không chạy lại trong lần sửa giao diện này).
- Chạy riêng `tests/test_gui.py` với `PDFTOOLS_GUI_TEST=1`: **5 passed**. Một root thật, bảy chức năng và ba trang hỗ trợ, theme clam, chữ ký footer, trạng thái menu chọn, font tiêu đề, bố cục 900×600, sidebar không bị cắt, cuộn đến nút thao tác, Lên/Xuống, các thao tác PDF/ảnh qua worker và heartbeat event loop. Fixture kiểm tra không có hộp thoại lỗi/callback bị che bởi mock.
- Metadata PDF đọc trên thread nền: tên có dấu, dung lượng, số trang. Test kéo thả đi qua chuỗi callback OLE/TkDnD (`HandleDragEnter`/`HandleDrop`), kiểm tra thay thế `%D` và đường dẫn có dấu/khoảng trắng; không thay thế bằng Tk `event_generate` thông thường.
- Kiểm tra lịch sử giới hạn 100 tác vụ, lưu/đọc UTF-8, fallback khi JSON hỏng; cài đặt DPI/định dạng ảnh áp dụng vào trang xuất ảnh.
- Chạy riêng `test_actual_word_to_pdf`: **1 passed**, khoảng 8 giây. DOCX mẫu được tạo bằng stdlib, chuyển thành PDF bằng Word thật, kiểm tra số trang/nội dung và giữ nguyên DOCX nguồn.
- Word COM phát sinh thông báo RPC trong lúc giải phóng COM ở môi trường này; conversion vẫn tạo PDF hợp lệ và test pass. Không còn WINWORD.EXE sau test. Test mock kiểm tra đường lỗi export, lỗi Close và lỗi Quit/terminate instance riêng.
- Kiểm tra PDF → Word thật ở phiên trước (02/10/2026): **1 passed**, kiểm tra nội dung `word/document.xml`, nhưng đã chờ hơn 18 phút. Khi đó Word hiển thị **Unlicensed Product**. Cần hoàn tất cài đặt/kích hoạt Word để đánh giá tốc độ và độ ổn định thông thường.
- `compileall` cho source: pass.
- `python -m tests.startup_smoke`: pass; chạy entry point `main.py`, mở mainloop với một root/bảy chức năng và ba trang hỗ trợ rồi tự đóng sau 1,5 giây, không có lỗi callback.
- Build bằng PyInstaller trên Windows với Tcl/Tk, PDFium, ReportLab và pywin32: thành công.
- Đã mở EXE và quan sát đúng cửa sổ **Bộ công cụ PDF** bằng Computer Use.
- Kiểm tra trực tiếp EXE giao diện mới: sidebar chia nhóm, card trắng, footer tác giả; chọn PDF mẫu qua dialog và thấy đúng tên/dung lượng/3 trang. Cắt `1,2-3` tạo đúng hai PDF (1 và 2 trang), progress `2/2`, kết quả “Đã tạo 2 file”, nút mở thư mục và bản ghi lịch sử chính xác. File thử nằm trong `.exe-check-data/interface-output`.
- Kiểm tra focus phát hiện việc cuộn theo frame tổ tiên làm nút dịch chuyển khi click lần đầu; bản cuối chỉ cuộn theo control có thể tương tác. Test GUI kiểm tra focus ô chọn PDF giữ nguyên vị trí cuộn, 5 test GUI pass sau sửa lỗi.
- Cập nhật bảng màu theo yêu cầu: primary `#128C9A`, sidebar `#172A3A`, hover `#213C50`, active `#E7F4F5`, nền `#F6F8FB`, heading `#16283A`, text `#344054`, border `#DCE3EA`. Card trắng và secondary text `#667085`. Tiêu đề được tách màu riêng khỏi sidebar; ô khoảng trang dùng bảng màu chung. Chạy lại 5 test GUI: **5 passed**; PyInstaller build thành công.
- Bản cuối: `dist\PDFTools.exe`, 33.080.745 byte, SHA-256 `F385101CA756438A55AB7484B3145D82B9103AC4A8AA360A8C017C4672C7B79E`.
- Đã kiểm tra archive của EXE chứa Tcl `init.tcl`, `pdfium.dll`, `pythoncom312.dll`, `pywintypes312.dll` và TkDnD DLL/Tcl cho Windows x64; EXE khởi động được với `TkinterDnD.Tk`.
- `dist\PDFTools.previous.exe` là bản cũ từ phiên build trước. Bản sử dụng mới là `dist\PDFTools.exe`.

Test desktop không thay thế việc thử tài liệu thực tế của người dùng. Chuyển PDF phức tạp sang Word phụ thuộc Word, layout PDF và môi trường máy. Không khẳng định giữ layout hoàn hảo hoặc đảm bảo xử lý được mọi PDF.

## Tài liệu kỹ thuật đã đối chiếu

- [pypdf PageObject](https://pypdf.readthedocs.io/en/stable/modules/PageObject.html): rotation, merge overlay.
- [pypdfium2 Python API](https://pypdfium2.readthedocs.io/en/stable/python_api.html): render và quản lý bitmap/page.
- [Word Documents.Open](https://learn.microsoft.com/en-us/office/vba/api/word.documents.open), [SaveAs2](https://learn.microsoft.com/en-us/office/vba/api/word.saveas2), [Window.Hwnd](https://learn.microsoft.com/en-us/office/vba/api/word.window.hwnd): COM conversion và handle instance riêng.
- [PyInstaller hooks](https://pyinstaller.org/en/latest/hooks.html): thu thập DLL/data và hook thư viện.
- [tkinterdnd2](https://github.com/Eliav2/tkinterdnd2): kéo thả native, `TkinterDnD.Tk`, `DND_FILES` và đóng gói tài nguyên TkDnD.
