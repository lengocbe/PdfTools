"""Integration opt-in: cần Word desktop đã kích hoạt trên Windows."""
import os
from zipfile import ZipFile
import pytest
from services.pdf_to_word_service import pdf_to_word
from services.word_to_pdf_service import word_to_pdf

@pytest.mark.skipif(os.environ.get('PDFTOOLS_WORD_TEST') != '1',reason='Bật PDFTOOLS_WORD_TEST=1 khi có Word')
def test_actual_word(make_pdf,tmp_path):
    source = make_pdf('word_conversion.pdf',1,'PDFTools Word integration')
    result = pdf_to_word([source],tmp_path)
    assert not result.errors, result.errors
    assert len(result.outputs) == 1
    with ZipFile(result.outputs[0]) as archive:
        assert b'PDFTools Word integration' in archive.read('word/document.xml')


@pytest.mark.skipif(os.environ.get('PDFTOOLS_WORD_TEST') != '1',reason='Bật PDFTOOLS_WORD_TEST=1 khi có Word')
def test_actual_word_to_pdf(tmp_path):
    """DOCX tối thiểu được tạo bằng stdlib, không thêm dependency."""
    from pypdf import PdfReader
    source = tmp_path / 'word_export.docx'
    with ZipFile(source,'w') as archive:
        archive.writestr('[Content_Types].xml',
            '<?xml version="1.0" encoding="UTF-8"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
            '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
            '<Default Extension="xml" ContentType="application/xml"/>'
            '<Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/></Types>')
        archive.writestr('_rels/.rels',
            '<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
            '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/></Relationships>')
        archive.writestr('word/document.xml',
            '<?xml version="1.0" encoding="UTF-8"?><w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
            '<w:body><w:p><w:r><w:t>PDFTools Word export integration</w:t></w:r></w:p><w:sectPr/></w:body></w:document>')
    original = source.read_bytes()
    result = word_to_pdf([source],tmp_path)
    assert not result.errors, result.errors
    assert len(result.outputs) == 1
    pages = PdfReader(result.outputs[0]).pages
    assert len(pages) >= 1
    assert 'PDFTools Word export integration' in ''.join(p.extract_text() for p in pages)
    assert source.read_bytes() == original
