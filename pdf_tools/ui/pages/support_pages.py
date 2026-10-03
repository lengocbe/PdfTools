"""Lịch sử, cài đặt và giới thiệu trong cùng cửa sổ chính."""
import os
import tkinter as tk
from tkinter import ttk
from ui.pages.base_page import BasePage


class HistoryPage(BasePage):
    def __init__(self,parent,app):
        super().__init__(parent,app,'Lịch sử xử lý','100 tác vụ gần nhất trên máy này. Không lưu nội dung tài liệu.')
        group = self.group('Tác vụ gần đây')
        listing = ttk.Frame(group)
        listing.pack(fill='x')
        listing.columnconfigure(0,weight=1)
        self.tree = ttk.Treeview(listing,columns=('time','task','count','status'),show='headings',height=9)
        for key,title,width in [('time','Thời gian',145),('task','Chức năng',120),('count','Số file',65),('status','Kết quả',150)]:
            self.tree.heading(key,text=title)
            self.tree.column(key,width=width,minwidth=50,stretch=key=='status')
        self.tree.grid(row=0,column=0,sticky='nsew')
        scroll = ttk.Scrollbar(listing,orient='vertical',command=self.tree.yview)
        scroll.grid(row=0,column=1,sticky='ns')
        self.tree.configure(yscrollcommand=scroll.set)
        self.details = tk.StringVar(value='Chọn tác vụ để xem thư mục xuất.')
        ttk.Label(group,textvariable=self.details,wraplength=560,style='Card.Muted.TLabel').pack(anchor='w',pady=10)
        self.open_button = ttk.Button(group,text='Mở thư mục xuất',command=self.open_folder,state='disabled')
        self.open_button.pack(anchor='w')
        self.tree.bind('<<TreeviewSelect>>',self.selected)

    def refresh_state(self):
        self.tree.delete(*self.tree.get_children())
        for index,record in enumerate(self.app.history.records):
            self.tree.insert('', 'end',iid=str(index),values=tuple(record[key] for key in ('time','task','count','status')))
        self.details.set('Chọn tác vụ để xem thư mục xuất.')
        self.open_button.state(['disabled'])

    def selected(self,event=None):
        selection = self.tree.selection()
        folder = self.app.history.records[int(selection[0])]['folder'] if selection else ''
        self.details.set(folder or 'Tác vụ chưa tạo file xuất.')
        self.open_button.state(['!disabled'] if folder else ['disabled'])

    def open_folder(self):
        selection = self.tree.selection()
        if selection:
            folder = self.app.history.records[int(selection[0])]['folder']
            if folder:
                try:
                    os.startfile(folder)
                except OSError:
                    self.form_error('Không mở được thư mục xuất. Thư mục có thể đã bị di chuyển.')


class SettingsPage(BasePage):
    def __init__(self,parent,app):
        super().__init__(parent,app,'Cài đặt','Cấu hình được lưu cục bộ và áp dụng cho lần xuất ảnh tiếp theo.')
        group = self.group('Xuất ảnh mặc định')
        self.dpi = tk.StringVar(value=str(app.settings.get('image_dpi')))
        self.image_format = tk.StringVar(value=app.settings.get('image_format'))
        for label,value,options in [('DPI',self.dpi,('96','150','200','300','600')),('Định dạng',self.image_format,('PNG','JPEG'))]:
            row = ttk.Frame(group)
            row.pack(fill='x',pady=5)
            ttk.Label(row,text=label,width=16).pack(side='left')
            ttk.Combobox(row,textvariable=value,values=options,state='readonly',width=12).pack(side='left')
        group = self.group('Dữ liệu ứng dụng')
        ttk.Label(group,text=str(app.settings.path.parent),wraplength=560).pack(anchor='w')
        ttk.Label(group,text='Cấu hình, lịch sử và log được lưu trên máy. Tài liệu không được tải lên Internet.',
                  wraplength=560,style='Card.Muted.TLabel').pack(anchor='w',pady=(8,0))
        self.feedback = tk.StringVar()
        ttk.Label(self,textvariable=self.feedback).pack(anchor='w')
        self.action('Lưu cài đặt',self.save)

    def refresh_state(self):
        self.dpi.set(str(self.app.settings.get('image_dpi')))
        self.image_format.set(self.app.settings.get('image_format'))

    def save(self):
        self.app.settings.set('image_dpi',int(self.dpi.get()))
        self.app.settings.set('image_format',self.image_format.get())
        self.app.settings.save()
        page = self.app.pages['PDF → Ảnh']
        page.dpi.set(self.dpi.get())
        page.format.set(self.image_format.get())
        self.feedback.set('Đã lưu cài đặt.')


class AboutPage(BasePage):
    def __init__(self,parent,app):
        super().__init__(parent,app,'Giới thiệu','Bộ công cụ PDF · Xử lý tài liệu hoàn toàn offline')
        group = self.group('Bộ công cụ PDF')
        for text in ['Cắt, nối, tách PDF; chuyển đổi PDF, Word và ảnh trong một cửa sổ.',
                     'Designed by Lê Ngọc Bé',
                     'Word → PDF và PDF → Word cần Microsoft Word được cài đặt, kích hoạt trên máy.',
                     'PDF quét dạng ảnh có thể không chuyển được chữ chính xác. Ứng dụng không có OCR.',
                     'Kéo thả PDF vào ô nguồn; kéo thả nhiều PDF, Word hoặc ảnh vào danh sách tương ứng.',
                     'Tài liệu gốc được giữ nguyên. Chỉ ghi đè kết quả khi bạn bật tùy chọn ghi đè.',
                     'Khi cửa sổ nhỏ, cuộn vùng nội dung để xem các tùy chọn và nút xử lý.']:
            ttk.Label(group,text=text,wraplength=560).pack(anchor='w',pady=(0,12))
