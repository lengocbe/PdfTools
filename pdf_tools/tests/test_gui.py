"""Kiểm tra GUI thực: bật PDFTOOLS_GUI_TEST=1 khi có Windows desktop."""
import os
from pathlib import Path
import time
import tkinter as tk
from tkinter import messagebox
import pytest
from config.settings import Settings
from services.common import OperationResult
from ui.main_window import MainWindow

pytestmark = pytest.mark.skipif(os.environ.get('PDFTOOLS_GUI_TEST') != '1', reason='Cần Windows desktop và PDFTOOLS_GUI_TEST=1')

@pytest.fixture(scope='module')
def window(tmp_path_factory):
    tmp_path = tmp_path_factory.mktemp('window')
    monkeypatch = pytest.MonkeyPatch()
    errors = []
    monkeypatch.setattr(messagebox,'showinfo',lambda *a,**k:None)
    monkeypatch.setattr(messagebox,'showerror',lambda *a,**k:errors.append(a))
    monkeypatch.setattr(messagebox,'showwarning',lambda *a,**k:None)
    root = MainWindow(Settings(tmp_path / 'settings.json'))
    root.update()
    yield root
    if root.worker.thread is not None:
        root.worker.thread.join(timeout=10)
    root.destroy()
    monkeypatch.undo()
    assert not errors, errors

def wait_task(window):
    deadline = time.monotonic() + 20
    while window.busy and time.monotonic() < deadline:
        window.update()
        time.sleep(0.01)
    window.update()
    assert not window.busy

def test_navigation_layout_and_order(window):
    assert window.title() == 'Bộ công cụ PDF'
    assert tk._default_root is window
    assert len(window.tool_names) == 7
    assert len(window.pages) == 10
    assert window.credit_label.cget('text') == 'Designed by Lê Ngọc Bé'
    from tkinter import ttk
    assert int(window.tk.splitlist(ttk.Style(window).lookup('Title.TLabel','font'))[1]) >= 20
    window.geometry('900x600')
    window.update()
    for button in window.nav_buttons:
        assert button.winfo_rooty() + button.winfo_height() <= window.credit_label.winfo_rooty()
    for name,page in window.pages.items():
        window.show_page(name)
        window.update()
        assert window.nav_by_name[name].cget('style') == 'Selected.Nav.TButton'
        def check(widget):
            for child in widget.winfo_children():
                if child.winfo_class() == 'TButton' and child.winfo_ismapped():
                    window.content.reveal(child)
                    window.update()
                    bottom = child.winfo_rooty() + child.winfo_height()
                    assert bottom <= window.progress.winfo_rooty(), (name,child.cget('text'),bottom,window.progress.winfo_rooty())
                check(child)
        check(page)
    assert window.progress.winfo_rootx() > window.nav_buttons[0].winfo_rootx()
    window.show_page('Cắt PDF')
    window.update()
    first_view = window.content.canvas.yview()[0]
    window.pages['Cắt PDF'].source.button.focus_set()
    window.update()
    assert window.content.canvas.yview()[0] == first_view
    files = window.pages['Nối PDF'].files
    ids = [files.tree.insert('', 'end',values=(name,)) for name in ['a.pdf','b.pdf','c.pdf']]
    files.tree.selection_set(ids[1])
    files.move(-1)
    assert files.paths() == ['b.pdf','a.pdf','c.pdf']
    files.move(1)
    assert files.paths() == ['a.pdf','b.pdf','c.pdf']
    for item in ids:
        files.tree.delete(item)

def test_gui_pdf_tasks(window,make_pdf,tmp_path):
    source = make_pdf('input.pdf',3)
    a = window.pages['Cắt PDF']
    a.source.value.set(str(source)); a.folder.value.set(str(tmp_path))
    a.ranges.insert('1.0','1-2,3')
    a.submit(); wait_task(window)
    assert (tmp_path / 'input_p1-2.pdf').exists()
    b = window.pages['Nối PDF']
    for path in [tmp_path / 'input_p1-2.pdf',tmp_path / 'input_p3.pdf']:
        b.files.tree.insert('', 'end',values=(str(path),))
    b.target.value.set(str(tmp_path / 'merged.pdf')); b.numbering.set(True)
    b.submit(); wait_task(window)
    assert (tmp_path / 'merged.pdf').exists()
    c = window.pages['Tách từng trang']
    c.source.value.set(str(source)); c.folder.value.set(str(tmp_path)); c.start.set('5')
    c.submit(); wait_task(window)
    assert (tmp_path / 'bl7.pdf').exists()
    d = window.pages['PDF → Ảnh']
    d.source.value.set(str(source)); d.folder.value.set(str(tmp_path))
    d.mode.set('selected'); d.pages.set('1,3'); d.dpi.set('96')
    d.submit(); wait_task(window)
    assert (tmp_path / 'input_page_003.png').exists()
    assert not (tmp_path / 'input_page_002.png').exists()

def test_gui_images_to_pdf(window,tmp_path):
    from PIL import Image
    from pypdf import PdfReader
    page = window.pages['Ảnh → PDF']
    window.show_page('Ảnh → PDF')
    paths = [tmp_path/'one.png',tmp_path/'two.png']
    for path in paths:
        with Image.new('RGB',(80,120),'red') as image:
            image.save(path)
        page.files.tree.insert('', 'end',values=(str(path),))
    page.target.value.set(str(tmp_path/'images.pdf'))
    page.submit(); wait_task(window)
    assert len(PdfReader(tmp_path/'images.pdf').pages) == 2

def test_responsive_event_loop(window):
    ticks = []
    def heartbeat():
        ticks.append(1)
        if window.busy:
            window.after(10,heartbeat)
    def slow_task(progress_callback):
        for i in range(20):
            time.sleep(0.03)
            progress_callback(i+1,20,'Đang xử lý')
        return OperationResult()
    window.run_task(window.pages['Cắt PDF'],slow_task,{})
    window.after(10,heartbeat)
    assert all('disabled' in button.state() for button in window.nav_buttons)
    wait_task(window)
    assert len(ticks) > 20
    assert all('disabled' not in button.state() for button in window.nav_buttons)


def test_metadata_drop_settings_and_history(window,make_pdf,tmp_path):
    source = make_pdf('Tài liệu có dấu.pdf',4)
    page = window.pages['Cắt PDF']
    page.source.accept_paths([str(source)])
    deadline = time.monotonic() + 5
    while '4 trang' not in page.source.details.get() and time.monotonic() < deadline:
        window.update()
        time.sleep(0.01)
    assert page.source.name.get() == source.name
    assert '4 trang' in page.source.details.get()
    assert window.tk.call('package','present','tkdnd')
    # Đi qua chuỗi callback OLE/TkDnD thật, gồm phép thay thế %D của TkDnD.
    page.source.value.set('')
    window.show_page('Cắt PDF')
    window.update()
    target = page.source.name_label
    x,y = target.winfo_rootx()+5,target.winfo_rooty()+5
    window.tk.call('tkdnd::olednd::HandleDragEnter',str(target),('CF_HDROP',),('copy',),'',x,y,('CF_HDROP',))
    action = window.tk.call('tkdnd::olednd::HandleDrop',str(target),'',x,y,'CF_HDROP',(str(source),))
    assert action == 'copy'
    window.update()
    assert page.source.value.get() == str(source)
    settings = window.pages['Cài đặt']
    settings.dpi.set('300'); settings.image_format.set('JPEG'); settings.save()
    assert window.pages['PDF → Ảnh'].format.get() == 'JPEG'
    assert window.settings.get('image_dpi') == 300
    assert window.history.records
    window.show_page('Lịch sử xử lý'); window.update()
    assert len(window.pages['Lịch sử xử lý'].tree.get_children()) == len(window.history.records)
    # Reset để kiểm tra khác không bị ảnh hưởng cấu hình ảnh.
    settings.dpi.set('200'); settings.image_format.set('PNG'); settings.save()
