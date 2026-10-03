"""Vùng nội dung cuộn để biểu mẫu không mất nút ở cửa sổ nhỏ."""
import tkinter as tk
from tkinter import ttk
from ui.theme import COLORS


class ScrollableContent(ttk.Frame):
    def __init__(self,parent):
        super().__init__(parent)
        self.columnconfigure(0,weight=1)
        self.rowconfigure(0,weight=1)
        self.canvas = tk.Canvas(self,background=COLORS['background'],highlightthickness=0)
        self.canvas.grid(row=0,column=0,sticky='nsew')
        self.scrollbar = ttk.Scrollbar(self,orient='vertical',command=self.canvas.yview)
        self.scrollbar.grid(row=0,column=1,sticky='ns')
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.body = ttk.Frame(self.canvas)
        self.body.columnconfigure(0,weight=1)
        self.item = self.canvas.create_window((0,0),window=self.body,anchor='nw')
        self.body.bind('<Configure>',self._layout)
        self.canvas.bind('<Configure>',self._layout)
        self.canvas.bind_all('<MouseWheel>',self._wheel,add='+')
        self.current_page = None

    def show(self,page):
        if self.current_page is not None:
            self.current_page.grid_remove()
        self.current_page = page
        page.grid(row=0,column=0,sticky='new')
        self.canvas.yview_moveto(0)
        self.after_idle(self._layout)

    def _layout(self,event=None):
        self.canvas.itemconfigure(self.item,width=self.canvas.winfo_width())
        self.canvas.configure(scrollregion=self.canvas.bbox('all'))

    def _wheel(self,event):
        target = self.winfo_containing(event.x_root,event.y_root)
        if target and str(target).startswith(str(self)) and target.winfo_class() not in ('Text','Treeview','TCombobox'):
            if self.body.winfo_height() > self.canvas.winfo_height():
                self.canvas.yview_scroll(-int(event.delta / 120),'units')

    def reveal(self,widget):
        self.update_idletasks()
        top = widget.winfo_rooty() - self.body.winfo_rooty()
        height = max(1,self.body.winfo_height())
        if top + widget.winfo_height() > self.canvas.canvasy(self.canvas.winfo_height()):
            self.canvas.yview_moveto(max(0,(top + widget.winfo_height() - self.canvas.winfo_height()) / height))
