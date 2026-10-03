import pytest
from pypdf import PdfReader, PdfWriter
from services.merge_pdf_service import merge_pdf
from utils.errors import AppError

@pytest.mark.parametrize('numbering', [False, True])
def test_merge(make_pdf, tmp_path, numbering):
    a, b = make_pdf('a.pdf', 2, 'A'), make_pdf('b.pdf', 3, 'B', (500,300))
    result = merge_pdf([a,b], tmp_path / 'merged.pdf', numbering)
    pages = PdfReader(result.outputs[0]).pages
    assert len(pages) == 5
    for page, expected in zip(pages, ['A 1','A 2','B 1','B 2','B 3']):
        assert expected in page.extract_text()
    if numbering:
        for i, page in enumerate(pages, 1):
            assert page.extract_text().strip().endswith(str(i))
    assert float(pages[2].mediabox.width) == 500

def test_rotation(make_pdf, tmp_path):
    a = make_pdf('a.pdf', 1)
    writer = PdfWriter()
    writer.add_page(PdfReader(a).pages[0]).rotate(90)
    rotated = tmp_path / 'rotated.pdf'
    writer.write(rotated)
    target = tmp_path / 'merged.pdf'
    merge_pdf([a,rotated], target, True)
    page = PdfReader(target).pages[1]
    assert page.rotation == 0
    assert float(page.mediabox.width) == 400
    assert '2' in page.extract_text()

def test_protect_source(make_pdf):
    a,b = make_pdf('a.pdf',1), make_pdf('b.pdf',1)
    original = a.read_bytes()
    with pytest.raises(AppError):
        merge_pdf([a,b], a, overwrite=True)
    assert a.read_bytes() == original
