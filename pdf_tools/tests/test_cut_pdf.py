import pytest
from pypdf import PdfReader
from services.cut_pdf_service import cut_pdf
from utils.errors import AppError

def test_cut(make_pdf, tmp_path):
    source = make_pdf('hợp đồng.pdf', 10)
    original = source.read_bytes()
    result = cut_pdf(source, '3-4;7-8\n5', tmp_path)
    assert [p.name for p in result.outputs] == ['hợp đồng_p3-4.pdf', 'hợp đồng_p7-8.pdf', 'hợp đồng_p5.pdf']
    assert [len(PdfReader(p).pages) for p in result.outputs] == [2,2,1]
    assert 'page 3' in PdfReader(result.outputs[0]).pages[0].extract_text()
    assert source.read_bytes() == original
    with pytest.raises(AppError):
        cut_pdf(source, '3-4', tmp_path)

def test_preflight(make_pdf, tmp_path):
    source = make_pdf('source.pdf', 10)
    (tmp_path / 'source_p7-8.pdf').write_bytes(b'existing')
    with pytest.raises(AppError):
        cut_pdf(source, '3-4,7-8', tmp_path)
    assert not (tmp_path / 'source_p3-4.pdf').exists()
