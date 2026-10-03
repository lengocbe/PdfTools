"""Bảng màu navy/xanh ngọc và style ttk dùng chung."""
from tkinter import ttk

COLORS = {'navy': '#172A3A', 'teal': '#128C9A', 'teal_hover': '#0E7480',
          'background': '#F6F8FB', 'white': '#FFFFFF', 'heading': '#16283A', 'text': '#344054',
          'muted': '#667085', 'border': '#DCE3EA', 'success': '#178A55',
          'error': '#D64545', 'warning': '#D97706', 'nav_text': '#F8FAFC',
          'credit': '#BDCBD8', 'nav_hover': '#213C50', 'nav_active': '#E7F4F5'}


def configure_theme(root) -> None:
    """Clam hỗ trợ màu nền nhất quán trên Windows."""
    c = COLORS
    root.configure(background=c['background'])
    style = ttk.Style(root)
    style.theme_use('clam')
    style.configure('.', font=('Segoe UI', 10), background=c['background'], foreground=c['text'])
    style.configure('TFrame', background=c['background'])
    style.configure('TLabel', background=c['background'], foreground=c['text'])
    style.configure('Title.TLabel', font=('Segoe UI', 21, 'bold'), foreground=c['heading'])
    style.configure('Description.TLabel', foreground=c['muted'])
    style.configure('Sidebar.TFrame', background=c['navy'])
    style.configure('Sidebar.TLabel', background=c['navy'], foreground=c['nav_text'])
    style.configure('Credit.Sidebar.TLabel', font=('Segoe UI', 9), foreground=c['credit'])
    style.configure('Card.TFrame', background=c['white'])
    style.configure('Card.TLabel', background=c['white'])
    style.configure('Card.Title.TLabel', background=c['white'], foreground=c['heading'], font=('Segoe UI',10,'bold'))
    style.configure('Card.Muted.TLabel', background=c['white'], foreground=c['muted'], font=('Segoe UI',9))
    style.configure('Card.File.TLabel', background=c['white'], font=('Segoe UI',11,'bold'))
    style.configure('Section.TLabel', foreground=c['heading'], font=('Segoe UI',10,'bold'))
    style.configure('Footer.TLabel', font=('Segoe UI',9), foreground=c['muted'])
    style.configure('Topbar.TFrame', background=c['white'])
    style.configure('Brand.TLabel', background=c['white'], foreground=c['heading'], font=('Segoe UI',12,'bold'))
    style.configure('NavGroup.TLabel', background=c['navy'], foreground=c['credit'], font=('Segoe UI',8,'bold'))
    style.configure('Card.TLabelframe', background=c['white'], bordercolor=c['border'], relief='solid', borderwidth=1)
    style.configure('Card.TLabelframe.Label', background=c['background'], foreground=c['heading'], font=('Segoe UI', 10, 'bold'))
    for name in ('Card.TCheckbutton', 'Card.TRadiobutton'):
        style.configure(name, background=c['white'])
        style.map(name, background=[('active', c['white'])])
    style.configure('TButton', background=c['white'], foreground=c['text'], bordercolor=c['border'], padding=(10,6))
    style.map('TButton', background=[('disabled', c['background']), ('active', c['background'])],
              foreground=[('disabled', '#8A98A6')])
    style.configure('Action.TButton', background=c['teal'], foreground=c['white'], bordercolor=c['teal'],
                    padding=(18,9), font=('Segoe UI',10,'bold'))
    style.map('Action.TButton', background=[('disabled', c['border']), ('active', c['teal_hover'])],
              foreground=[('disabled', '#8A98A6'), ('!disabled', c['white'])])
    style.configure('Nav.TButton', background=c['navy'], foreground=c['nav_text'], borderwidth=0,
                    bordercolor=c['navy'], padding=(12,6), anchor='w')
    style.map('Nav.TButton', background=[('disabled', c['navy']), ('active', c['nav_hover'])],
              foreground=[('disabled', '#889BAE'), ('!disabled', c['nav_text'])])
    style.configure('Selected.Nav.TButton', background=c['nav_active'], foreground=c['heading'], font=('Segoe UI',10,'bold'))
    style.map('Selected.Nav.TButton', background=[('disabled', c['nav_active']), ('active', c['nav_active']), ('!disabled', c['nav_active'])],
              foreground=[('disabled', c['muted']), ('!disabled', c['heading'])])
    style.configure('TEntry', fieldbackground=c['white'], foreground=c['text'], bordercolor=c['border'], padding=5)
    style.configure('TCombobox', fieldbackground=c['white'], foreground=c['text'], padding=4)
    style.map('TCombobox', fieldbackground=[('readonly', c['white'])], foreground=[('readonly', c['text'])])
    style.configure('Treeview', background=c['white'], fieldbackground=c['white'], foreground=c['text'], rowheight=25, bordercolor=c['border'])
    style.map('Treeview', background=[('selected', c['teal'])], foreground=[('selected', c['white'])])
    style.configure('Treeview.Heading', background=c['background'], foreground=c['heading'], font=('Segoe UI',10,'bold'), padding=5)
    style.configure('Horizontal.TProgressbar', background=c['teal'], troughcolor=c['border'], bordercolor=c['border'], thickness=6)
    style.configure('Success.TLabel', foreground=c['success'], background=c['white'])
    style.configure('Error.TLabel', foreground=c['error'], background=c['white'])


def apply_card_styles(page) -> None:
    """Đồng bộ nền trắng cho widget trong nhóm nhập liệu."""
    mapping = {ttk.Frame: 'Card.TFrame', ttk.Label: 'Card.TLabel',
               ttk.Checkbutton: 'Card.TCheckbutton', ttk.Radiobutton: 'Card.TRadiobutton'}
    def walk(widget, in_card=False):
        if isinstance(widget, ttk.Frame) and widget.cget('style') == 'Card.TFrame':
            in_card = True
        elif isinstance(widget, ttk.LabelFrame):
            widget.configure(style='Card.TLabelframe')
            in_card = True
        elif in_card:
            for klass, style in mapping.items():
                if isinstance(widget, klass):
                    if not widget.cget('style'):
                        widget.configure(style=style)
                    break
        for child in widget.winfo_children():
            walk(child, in_card)
    walk(page)
