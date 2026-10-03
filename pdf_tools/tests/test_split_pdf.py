import pytest
from pypdf import PdfReader
from services.split_pdf_service import split_pdf
from utils.errors import AppError

def test_split(make_pdf, tmp_path):
    source = make_pdf('source.pdf',3)
    result = split_pdf(source,tmp_path,'bl',5)
    assert [p.name for p in result.outputs] == ['bl5.pdf','bl6.pdf','bl7.pdf','danh_sach_file_pdf.txt']
    assert result.outputs[-1].read_text(encoding='utf-8') == 'bl5.pdf\nbl6.pdf\nbl7.pdf\n'
    assert all(len(PdfReader(p).pages) == 1 for p in result.outputs[:-1])
    with pytest.raises(AppError):
        split_pdf(source,tmp_path,'bl',5)
    split_pdf(source,tmp_path,'bl',5,overwrite=True)

@pytest.mark.parametrize('prefix', ['../x','a/b'])
def test_bad_prefix(make_pdf,tmp_path,prefix):
    with pytest.raises(AppError):
        split_pdf(make_pdf('source.pdf',1),tmp_path,prefix)
