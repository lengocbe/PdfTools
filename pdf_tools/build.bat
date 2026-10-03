@echo off
setlocal
cd /d "%~dp0"
set "BUILD_PYTHON=python"
if exist ".venv\Scripts\python.exe" set "BUILD_PYTHON=.venv\Scripts\python.exe"
"%BUILD_PYTHON%" -m pytest -q
if errorlevel 1 exit /b 1
"%BUILD_PYTHON%" -m PyInstaller --noconfirm --clean PDFTools.spec
if errorlevel 1 exit /b 1
echo.
echo Da tao: %CD%\dist\PDFTools.exe
endlocal
