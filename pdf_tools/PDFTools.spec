# -*- mode: python ; coding: utf-8 -*-
from pathlib import Path
from PyInstaller.utils.hooks import collect_data_files, collect_dynamic_libs
from PyInstaller.utils.hooks.tcl_tk import tcltk_info

if not tcltk_info.available:
    raise SystemExit('Tkinter/Tcl/Tk unavailable. Use a Python Windows installation with Tcl/Tk before building.')

root = Path(SPECPATH)
icon = root / 'assets' / 'app.ico'
datas = collect_data_files('reportlab') + collect_data_files('pypdfium2_raw') + collect_data_files('tkinterdnd2')
if icon.is_file():
    datas.append((str(icon), 'assets'))
binaries = collect_dynamic_libs('pypdfium2_raw')
a = Analysis([str(root / 'main.py')], pathex=[str(root)], binaries=binaries,
             datas=datas, hiddenimports=['pythoncom', 'pywintypes', 'win32com.client',
                                        'win32com.client.dynamic', 'win32timezone'],
             hookspath=[], hooksconfig={}, runtime_hooks=[],
             excludes=['pytest', 'IPython', 'matplotlib', 'numpy', 'pandas'], noarchive=False)
pyz = PYZ(a.pure)
exe = EXE(pyz, a.scripts, a.binaries, a.datas, [], name='PDFTools',
          debug=False, bootloader_ignore_signals=False, strip=False, upx=False,
          console=False, disable_windowed_traceback=True,
          icon=str(icon) if icon.is_file() else None)
