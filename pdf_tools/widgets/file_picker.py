"""Các dialog và trường đường dẫn dùng chung."""
from pathlib import Path
import tkinter as tk
from tkinter import ttk, filedialog
from config.settings import Settings
import logging
from queue import Queue, Empty
from threading import Thread
from utils.errors import AppError
from utils.file_metadata import describe_pdf
from widgets.tooltip import Tooltip
from widgets.drop_target import register_drop


class Dialogs:
    def __init__(self, parent, settings: Settings):
        self.parent = parent
        self.settings = settings

    def _initial(self, key):
        folder = self.settings.get(key)
        return folder if folder and Path(folder).is_dir() else str(Path.home())

    def _remember(self, key, folder):
        self.settings.set(key, str(folder))
        self.settings.save()

    def _files(self, title, filetypes, key, multiple=False):
        options = dict(parent=self.parent, title=title, filetypes=filetypes,
                       initialdir=self._initial(key))
        result = filedialog.askopenfilenames(**options) if multiple else filedialog.askopenfilename(**options)
        if result:
            first = result[0] if multiple else result
            self._remember(key, Path(first).parent)
        return result

    def pdfs(self, multiple=False):
        return self._files('Chọn PDF', [('Tài liệu PDF', '*.pdf')], 'last_pdf_folder', multiple)

    def words(self, multiple=False):
        return self._files('Chọn Word', [('Tài liệu Word', '*.doc *.docx')], 'last_word_folder', multiple)

    def images(self, multiple=False):
        return self._files('Chọn ảnh', [('Ảnh được hỗ trợ', '*.png *.jpg *.jpeg *.bmp *.tif *.tiff *.webp')],
                           'last_image_folder', multiple)

    def folder(self):
        result = filedialog.askdirectory(parent=self.parent, title='Chọn thư mục xuất',
                                         initialdir=self._initial('last_output_folder'), mustexist=True)
        if result:
            self._remember('last_output_folder', result)
        return result

    def output_pdf(self, initialfile='PDF_da_noi.pdf'):
        result = filedialog.asksaveasfilename(parent=self.parent, title='Chọn nơi lưu PDF',
                                              initialdir=self._initial('last_output_folder'),
                                              initialfile=initialfile, defaultextension='.pdf',
                                              filetypes=[('Tài liệu PDF','*.pdf')])
        if result:
            self._remember('last_output_folder', Path(result).parent)
        return result


class FilePicker(ttk.Frame):
    def __init__(self, parent, dialogs: Dialogs, output=False, output_name='PDF_da_noi.pdf'):
        super().__init__(parent)
        self.value = tk.StringVar()
        self.output = output
        self._generation = 0
        self._metadata_queue = Queue()
        self.columnconfigure(0, weight=1)
        if output:
            ttk.Entry(self, textvariable=self.value).grid(row=0, column=0, sticky='ew', padx=(0,8))
        else:
            self.name = tk.StringVar(value='Kéo thả file PDF vào đây hoặc Chọn PDF')
            self.details = tk.StringVar(value='Chưa chọn tài liệu')
            self.name_label = ttk.Label(self, textvariable=self.name, style='Card.File.TLabel', anchor='w')
            self.name_label.grid(row=0,column=0,sticky='ew',padx=(0,8))
            self.bind('<Configure>',lambda event:self.name_label.configure(wraplength=max(160,event.width-150)))
            detail_label = ttk.Label(self,textvariable=self.details,style='Card.Muted.TLabel')
            detail_label.grid(row=1,column=0,sticky='w',pady=(5,0))
            Tooltip(self.name_label, self.value.get)
            for target in (self, self.name_label, detail_label):
                register_drop(target, self.accept_paths, ('.pdf',))
            self.value.trace_add('write', self._selected)
            self.after(80,self._poll_metadata)
        def choose():
            path = dialogs.output_pdf(output_name) if output else dialogs.pdfs()
            if path:
                self.value.set(path)
        self.button = ttk.Button(self, text='Chọn nơi lưu' if output else 'Chọn PDF', command=choose)
        self.button.grid(row=0,column=1,rowspan=1 if output else 2)

    def accept_paths(self, paths: list[str]) -> None:
        if len(paths) != 1:
            from tkinter import messagebox
            messagebox.showerror('Chọn một PDF','Chức năng này cần đúng một file PDF nguồn.',parent=self)
            return
        self.value.set(paths[0])

    def _selected(self, *_):
        """Không đọc PDF trên GUI thread; token loại bỏ kết quả chọn file cũ."""
        path = self.value.get()
        self._generation += 1
        token = self._generation
        self.name.set(Path(path).name if path else 'Kéo thả file PDF vào đây hoặc Chọn PDF')
        self.button.configure(text='Thay đổi' if path else 'Chọn PDF')
        self.details.set('Đang đọc thông tin tài liệu...' if path else 'Chưa chọn tài liệu')
        if not path:
            return
        queue = self._metadata_queue
        def read():
            try:
                detail = describe_pdf(path)
            except AppError as exc:
                detail = str(exc)
            except OSError:
                detail = 'Không đọc được file. Hãy kiểm tra đường dẫn và quyền truy cập.'
            except Exception:
                logging.getLogger(__name__).exception('Không đọc được metadata PDF: %s',path)
                detail = 'Không đọc được thông tin PDF.'
            queue.put((token, detail))
        Thread(target=read,daemon=True,name='PDF metadata').start()

    def _poll_metadata(self):
        try:
            while True:
                token, detail = self._metadata_queue.get_nowait()
                if token == self._generation:
                    self.details.set(detail)
        except Empty:
            pass  # Queue không còn sự kiện; đây là trạng thái bình thường.
        self.after(80,self._poll_metadata)
