"""Root duy nhất: điều hướng, điều phối worker và settings cửa sổ."""
import logging
from pathlib import Path
import sys
import tkinter as tk
from tkinter import ttk, messagebox
from tkinterdnd2 import TkinterDnD
from config.settings import APP_NAME, Settings
from utils.worker import Worker
from widgets.file_picker import Dialogs
from widgets.progress_panel import ProgressPanel
from widgets.scrollable_content import ScrollableContent
from utils.history import HistoryStore
from ui.pages.cut_pdf_page import CutPdfPage
from ui.pages.merge_pdf_page import MergePdfPage
from ui.pages.split_pdf_page import SplitPdfPage
from ui.pages.pdf_to_image_page import PdfToImagePage
from ui.pages.pdf_to_word_page import PdfToWordPage
from ui.pages.word_to_pdf_page import WordToPdfPage
from ui.pages.images_to_pdf_page import ImagesToPdfPage
from ui.pages.support_pages import HistoryPage, SettingsPage, AboutPage
from ui.theme import configure_theme, apply_card_styles, COLORS


class MainWindow(TkinterDnD.Tk):
    def __init__(self,settings: Settings):
        super().__init__()
        self.settings = settings
        self.history = HistoryStore(settings.path.parent / 'history.json')
        self.busy = False
        self.title(APP_NAME)
        self.geometry(f"{settings.get('window_width')}x{settings.get('window_height')}")
        self.minsize(900,600)
        configure_theme(self)
        icon = Path(getattr(sys,'_MEIPASS',Path(__file__).resolve().parents[1])) / 'assets' / 'app.ico'
        if icon.is_file():
            try:
                self.iconbitmap(str(icon))
            except tk.TclError:
                logging.getLogger(__name__).warning('Không tải được icon',exc_info=True)
        self.columnconfigure(1,weight=1)
        self.rowconfigure(1,weight=1)
        topbar = ttk.Frame(self,padding=(20,10),style='Topbar.TFrame')
        topbar.grid(row=0,column=0,columnspan=2,sticky='ew')
        ttk.Label(topbar,text='BỘ CÔNG CỤ PDF',style='Brand.TLabel').pack(side='left')
        self.header_buttons = []
        for label,target in [('Trợ giúp','Giới thiệu'),('Cài đặt','Cài đặt')]:
            button = ttk.Button(topbar,text=label,command=lambda name=target:self.show_page(name))
            button.pack(side='right',padx=(8,0))
            self.header_buttons.append(button)
        sidebar = ttk.Frame(self,padding=(12,12),width=230,style='Sidebar.TFrame')
        sidebar.grid(row=1,column=0,sticky='ns')
        sidebar.pack_propagate(False)
        ttk.Label(sidebar,text='KHÔNG GIAN LÀM VIỆC',style='NavGroup.TLabel').pack(anchor='w',padx=8,pady=(4,12))
        container = ttk.Frame(self)
        container.grid(row=1,column=1,sticky='nsew')
        container.columnconfigure(0,weight=1)
        container.rowconfigure(0,weight=1)
        self.content = ScrollableContent(container)
        self.content.grid(row=0,column=0,sticky='nsew')
        self.dialogs = Dialogs(self,settings)
        self.pages = {}
        self.nav_buttons = []
        self.nav_by_name = {}
        self.nav_indicators = {}
        tools = [('Cắt PDF',CutPdfPage),('Nối PDF',MergePdfPage),('Tách từng trang',SplitPdfPage),
                 ('PDF → Ảnh',PdfToImagePage),('PDF → Word',PdfToWordPage),
                 ('Word → PDF',WordToPdfPage),('Ảnh → PDF',ImagesToPdfPage)]
        self.tool_names = tuple(label for label, _ in tools)
        for label,klass in tools + [('Lịch sử xử lý',HistoryPage),('Cài đặt',SettingsPage),('Giới thiệu',AboutPage)]:
            if label in ('Cắt PDF','PDF → Ảnh','Lịch sử xử lý'):
                group = {'Cắt PDF':'CHỈNH SỬA PDF','PDF → Ảnh':'CHUYỂN ĐỔI','Lịch sử xử lý':'ỨNG DỤNG'}[label]
                ttk.Label(sidebar,text=group,style='NavGroup.TLabel').pack(anchor='w',padx=8,pady=(10,6))
            page = klass(self.content.body,self)
            apply_card_styles(page)
            self.pages[label] = page
            row = ttk.Frame(sidebar,style='Sidebar.TFrame')
            row.pack(fill='x',pady=2)
            indicator = tk.Frame(row,width=3,background=COLORS['navy'])
            indicator.pack(side='left',fill='y')
            button = ttk.Button(row,text=label,style='Nav.TButton',command=lambda name=label:self.show_page(name))
            button.pack(side='left',fill='x',expand=True)
            self.nav_indicators[label] = indicator
            self.nav_buttons.append(button)
            self.nav_by_name[label] = button
        footer = ttk.Frame(self,padding=(16,6))
        footer.grid(row=2,column=0,columnspan=2,sticky='ew')
        self.footer_status = tk.StringVar(value='Xử lý hoàn toàn offline · Sẵn sàng')
        ttk.Label(footer,textvariable=self.footer_status,style='Footer.TLabel').pack(side='left')
        self.credit_label = ttk.Label(footer,text='Designed by Lê Ngọc Bé',style='Footer.TLabel')
        self.credit_label.pack(side='right')
        self.progress = ProgressPanel(container)
        self.progress.grid(row=1,column=0,sticky='ew',padx=24,pady=(0,16))
        self.worker = Worker()
        self.busy = False
        self.active_task_page = None
        self.saved_states = []
        self.show_page('Cắt PDF')
        self.protocol('WM_DELETE_WINDOW',self.on_close)
        self.bind_all('<FocusIn>',self._reveal_focus,add='+')
        self.after(60,self.poll_worker)

    def _reveal_focus(self,event):
        page = self.pages[self.current_page_name]
        if (isinstance(event.widget,(ttk.Button,ttk.Entry,ttk.Combobox,ttk.Checkbutton,
                                     ttk.Radiobutton,ttk.Treeview,tk.Text))
                and str(event.widget).startswith(str(page))):
            self.content.reveal(event.widget)

    def show_page(self,name: str):
        if not self.busy:
            self.current_page_name = name
            self.content.show(self.pages[name])
            self.pages[name].refresh_state()
            for label,button in self.nav_by_name.items():
                button.configure(style='Selected.Nav.TButton' if label == name else 'Nav.TButton')
                self.nav_indicators[label].configure(background=COLORS['teal'] if label == name else COLORS['navy'])

    def show_drop_error(self,extensions):
        messagebox.showerror('File không phù hợp','Hãy thả file có định dạng: ' + ', '.join(extensions),parent=self)

    def _lock_inputs(self,page):
        self.saved_states.clear()
        def visit(widget):
            for child in widget.winfo_children():
                if isinstance(child,(ttk.Button,ttk.Entry,ttk.Combobox,ttk.Checkbutton,ttk.Radiobutton,ttk.Treeview)):
                    state = child.state()
                    self.saved_states.append((child,state))
                    child.state(['disabled'])
                elif isinstance(child,tk.Text):
                    state = child.cget('state')
                    self.saved_states.append((child,state))
                    child.configure(state='disabled')
                visit(child)
        visit(page)
        for button in self.nav_buttons + self.header_buttons:
            button.state(['disabled'])

    def _unlock_inputs(self):
        for widget,state in self.saved_states:
            if isinstance(widget,tk.Text):
                widget.configure(state=state)
            else:
                widget.state(['!disabled','!readonly'])
                widget.state(state)
        self.saved_states.clear()
        for button in self.nav_buttons + self.header_buttons:
            button.state(['!disabled'])
        if self.active_task_page is not None:
            self.active_task_page.refresh_state()

    def run_task(self,page,function,kwargs):
        if self.busy:
            return
        self.busy = True
        self.active_task_page = page
        self._lock_inputs(page)
        self.progress.start()
        self.footer_status.set('Đang xử lý · ' + page.title)
        try:
            self.worker.start(function,**kwargs)
        except Exception:
            logging.getLogger(__name__).exception('Không khởi động được worker')
            self.busy = False
            self._unlock_inputs()
            self.progress.finish('Không khởi động được tác vụ.',False)
            self.footer_status.set('Không khởi động được tác vụ')
            messagebox.showerror('Lỗi','Không khởi động được tác vụ. Chi tiết đã được ghi vào log.',parent=self)

    def poll_worker(self):
        events = self.worker.drain()
        # Coalesce progress của trang lớn, không làm nghẽn event loop.
        last_progress = None
        for event in events:
            if event.kind == 'progress':
                last_progress = event.payload
                continue
            if last_progress is not None:
                self.progress.update_progress(*last_progress)
                last_progress = None
            self.busy = False
            self._unlock_inputs()
            if event.kind == 'error':
                self.progress.finish('Xử lý thất bại.',False)
                self.footer_status.set('Xử lý thất bại · Chi tiết đã ghi vào log')
                self.history.add(self.active_task_page.title,0,'Thất bại')
                messagebox.showerror('Không thể hoàn tất',event.payload,parent=self)
            elif event.kind == 'success':
                result = event.payload
                folder = str(result.outputs[0].parent) if result.outputs else ''
                self.history.add(self.active_task_page.title,len(result.outputs),
                                 'Có file lỗi' if result.errors else 'Hoàn tất',folder)
                self.footer_status.set(f'Hoàn tất · Đã tạo {len(result.outputs)} file')
                message = f'Đã tạo {len(result.outputs)} file.\nThư mục xuất: {folder}'
                if result.errors:
                    self.progress.finish(f'Đã tạo {len(result.outputs)} file · Có file lỗi',bool(result.outputs),folder)
                    message += '\n\nFile lỗi:\n' + '\n'.join(result.errors[:10])
                    if len(result.errors) > 10:
                        message += '\nCác lỗi còn lại được ghi trong log.'
                    messagebox.showwarning('Kết quả chuyển đổi',message,parent=self)
                else:
                    self.progress.finish(f'✓ Đã tạo {len(result.outputs)} file',True,folder)
        if last_progress is not None:
            self.progress.update_progress(*last_progress)
        self.after(60,self.poll_worker)

    def report_callback_exception(self,exception,value,traceback):
        logging.getLogger(__name__).error('Lỗi callback GUI',exc_info=(exception,value,traceback))
        messagebox.showerror('Lỗi','Không thực hiện được thao tác. Chi tiết đã được ghi vào log.',parent=self)

    def on_close(self):
        if self.busy:
            messagebox.showinfo('Đang xử lý','Vui lòng chờ tác vụ hoàn tất trước khi đóng ứng dụng.',parent=self)
            return
        self.settings.set('window_width',self.winfo_width())
        self.settings.set('window_height',self.winfo_height())
        self.settings.save()
        logging.getLogger(__name__).info('Ứng dụng đóng')
        self.destroy()
