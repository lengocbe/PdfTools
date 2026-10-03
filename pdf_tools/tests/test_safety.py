import pytest
from pypdf import PdfReader, PdfWriter
from config.settings import Settings
from utils.validators import open_pdf, validate_filename
from utils.file_utils import atomic_output
from utils.errors import AppError

def test_atomic_failed_write(tmp_path):
    target = tmp_path / 'output.pdf'
    target.write_bytes(b'original')
    with pytest.raises(RuntimeError):
        with atomic_output(target,True) as temporary:
            temporary.write_bytes(b'partial')
            raise RuntimeError('failure')
    assert target.read_bytes() == b'original'
    assert not list(tmp_path.glob('.pdftools-*'))

def test_encrypted_and_corrupt(make_pdf,tmp_path):
    writer = PdfWriter()
    writer.add_page(PdfReader(make_pdf('a.pdf',1)).pages[0])
    writer.encrypt('password')
    target = tmp_path / 'protected.pdf'
    writer.write(target)
    with pytest.raises(AppError,match='mật khẩu'):
        with open_pdf(target):
            pass
    target.write_bytes(b'not pdf')
    with pytest.raises(AppError,match='Không đọc được'):
        with open_pdf(target):
            pass

@pytest.mark.parametrize('name',['CON.txt','NUL','../a','a/b','a\\b','a:','a.',''])
def test_bad_names(name):
    with pytest.raises(AppError):
        validate_filename(name)

def test_settings_fallback(tmp_path):
    path = tmp_path / 'settings.json'
    path.write_text('{invalid',encoding='utf-8')
    assert Settings(path).get('image_dpi') == 200
    path.write_text('{"image_dpi": -1, "window_width": "a", "image_format": "bad"}',encoding='utf-8')
    settings = Settings(path)
    assert settings.get('window_width') == 1100
    assert settings.get('image_format') == 'PNG'
    assert settings.get('image_dpi') == 96
