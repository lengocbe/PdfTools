# Bộ công cụ PDF

Ứng dụng Windows offline với giao diện tiếng Việt, hỗ trợ cắt, nối, tách PDF,
PDF sang ảnh, PDF sang Word, Word sang PDF và ảnh sang PDF.

Source và hướng dẫn cài đặt, chạy, kiểm thử, đóng gói nằm trong
[pdf_tools/README.md](pdf_tools/README.md).

Mở terminal trong thư mục `pdf_tools` trước khi chạy các lệnh:

```bat
cd pdf_tools
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

Kiểm thử: `python -m pytest -q`. Đóng gói Windows: `build.bat`.
Kết quả đóng gói: `pdf_tools/dist/PDFTools.exe`.

Hai chức năng chuyển đổi Word yêu cầu Microsoft Word desktop được cài và
cấp phép hợp lệ trên máy chạy ứng dụng.
