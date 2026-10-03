"""Tooltip đường dẫn đầy đủ, không tạo root window bổ sung."""
import tkinter as tk
from tkinter import ttk


class Tooltip:
    def __init__(self, widget, text):
        self.widget, self.text = widget, text
        self.window = None
        self.timer = None
        widget.bind('<Enter>', self.schedule, add='+')
        widget.bind('<Leave>', self.hide, add='+')
        widget.bind('<ButtonPress>', self.hide, add='+')
        widget.bind('<Destroy>', self.hide, add='+')

    def schedule(self, event=None):
        self.hide()
        self.timer = self.widget.after(500, self.show)

    def show(self):
        self.timer = None
        text = self.text()
        if not text:
            return
        self.window = tk.Toplevel(self.widget)
        self.window.wm_overrideredirect(True)
        self.window.wm_geometry(f'+{self.widget.winfo_rootx()+8}+{self.widget.winfo_rooty()+self.widget.winfo_height()+4}')
        ttk.Label(self.window, text=text, padding=8, wraplength=600).pack()

    def hide(self, event=None):
        if self.timer is not None:
            self.widget.after_cancel(self.timer)
            self.timer = None
        if self.window is not None:
            self.window.destroy()
            self.window = None
