"""Danh sách file dùng chung cho PDF, Word và ảnh."""
from pathlib import Path
from tkinter import ttk
from widgets.file_picker import Dialogs
from widgets.drop_target import register_drop
from utils.validators import WORD_EXTENSIONS, IMAGE_EXTENSIONS


class FileList(ttk.Frame):
    def __init__(self, parent, dialogs: Dialogs, kind: str = 'pdf', reorder: bool = False):
        super().__init__(parent)
        label = {'pdf': 'PDF', 'word': 'Word', 'image': 'ảnh'}[kind]
        choose = {'pdf': dialogs.pdfs, 'word': dialogs.words, 'image': dialogs.images}[kind]
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        self.tree = ttk.Treeview(self, columns=('path',), show='headings', height=4, selectmode='extended')
        self.tree.heading('path', text=f'Đường dẫn {label}' + (' — thứ tự từ trên xuống' if reorder else ''))
        self.tree.column('path', width=580, minwidth=200)
        self.tree.grid(row=0, column=0, sticky='nsew')
        scroll = ttk.Scrollbar(self, orient='vertical', command=self.tree.yview)
        scroll.grid(row=0, column=1, sticky='ns')
        self.tree.configure(yscrollcommand=scroll.set)
        horizontal = ttk.Scrollbar(self, orient='horizontal', command=self.tree.xview)
        horizontal.grid(row=1, column=0, sticky='ew')
        self.tree.configure(xscrollcommand=horizontal.set)
        extensions = {'pdf': ('.pdf',), 'word': WORD_EXTENSIONS, 'image': IMAGE_EXTENSIONS}[kind]
        register_drop(self.tree, self.add_paths, extensions)
        buttons = ttk.Frame(self)
        buttons.grid(row=2, column=0, columnspan=2, sticky='w', pady=(8,0))
        def add():
            self.add_paths(choose(multiple=True))
        def remove():
            for item in self.tree.selection():
                self.tree.delete(item)
        def clear():
            for item in self.tree.get_children():
                self.tree.delete(item)
        for text, command in [(f'Thêm {label}', add), ('Bỏ file', remove)]:
            ttk.Button(buttons, text=text, command=command).pack(side='left', padx=(0,6))
        if reorder:
            ttk.Button(buttons, text='Lên', command=lambda:self.move(-1)).pack(side='left', padx=(0,6))
            ttk.Button(buttons, text='Xuống', command=lambda:self.move(1)).pack(side='left', padx=(0,6))
        ttk.Button(buttons, text='Xóa tất cả', command=clear).pack(side='left')
        ttk.Label(self,text='Có thể kéo thả file vào danh sách.',style='Card.Muted.TLabel').grid(row=3,column=0,sticky='w',pady=(8,0))

    def add_paths(self, paths) -> None:
        for path in paths:
            self.tree.insert('', 'end', values=(str(Path(path)),))

    def paths(self) -> list[str]:
        return [self.tree.item(item, 'values')[0] for item in self.tree.get_children()]

    def move(self, direction: int) -> None:
        selection = set(self.tree.selection())
        children = list(self.tree.get_children())
        for item in (children if direction < 0 else reversed(children)):
            if item not in selection:
                continue
            current = list(self.tree.get_children())
            index = current.index(item)
            other = index + direction
            if 0 <= other < len(current) and current[other] not in selection:
                self.tree.move(item, '', other)
