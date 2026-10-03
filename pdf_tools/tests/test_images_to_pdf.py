from pathlib import Path
import pytest
import pypdfium2 as pdfium
from PIL import Image
from pypdf import PdfReader
from services.images_to_pdf_service import images_to_pdf
from utils.errors import AppError


def save_image(path: Path, size, color, mode='RGB') -> Path:
    with Image.new(mode,size,color) as image:
        image.save(path)
    return path


def test_order_aspect_transparency_and_unicode(tmp_path):
    a = save_image(tmp_path / 'ảnh đỏ.png',(300,150),'red')
    b = save_image(tmp_path / 'ảnh trong suốt.png',(150,300),(0,0,255,0),'RGBA')
    originals = [p.read_bytes() for p in [a,b]]
    events = []
    output = tmp_path / 'ảnh ghép.pdf'
    result = images_to_pdf([a,b],output,progress_callback=lambda *args:events.append(args))
    assert result.outputs == [output]
    reader = PdfReader(output)
    assert len(reader.pages) == 2
    assert float(reader.pages[0].mediabox.width) / float(reader.pages[0].mediabox.height) == 2
    assert float(reader.pages[1].mediabox.height) / float(reader.pages[1].mediabox.width) == 2
    assert [p.read_bytes() for p in [a,b]] == originals
    assert [event[:2] for event in events] == [(1,2),(2,2)]
    with pdfium.PdfDocument(output) as document:
        for number,expected in [(0,(255,0,0)),(1,(255,255,255))]:
            page = document[number]
            bitmap = page.render(scale=1)
            image = bitmap.to_pil()
            try:
                assert image.getpixel((image.width//2,image.height//2))[:3] == expected
            finally:
                image.close(); bitmap.close(); page.close()


def test_exif_orientation(tmp_path):
    path = tmp_path / 'rotated.jpg'
    with Image.new('RGB',(300,150),'blue') as image:
        exif = Image.Exif(); exif[274] = 6
        image.save(path,exif=exif)
    target = tmp_path / 'rotated.pdf'
    images_to_pdf([path],target)
    page = PdfReader(target).pages[0]
    assert float(page.mediabox.height) / float(page.mediabox.width) == 2


def test_collision_failure_preserves_output(tmp_path):
    source = save_image(tmp_path / 'source.png',(20,20),'blue')
    bad = tmp_path / 'bad.png'; bad.write_bytes(b'not image')
    target = tmp_path / 'output.pdf'; target.write_bytes(b'old output')
    with pytest.raises(AppError,match='đã tồn tại'):
        images_to_pdf([source],target)
    with pytest.raises(AppError,match='bad.png'):
        images_to_pdf([source,bad],target,overwrite=True)
    assert target.read_bytes() == b'old output'
    assert not list(tmp_path.glob('.pdftools-*'))
    images_to_pdf([source],target,overwrite=True)
    assert len(PdfReader(target).pages) == 1


def test_bad_input(tmp_path):
    with pytest.raises(AppError,match='ít nhất'):
        images_to_pdf([],tmp_path/'out.pdf')
    with pytest.raises(AppError):
        images_to_pdf([tmp_path/'missing.png'],tmp_path/'out.pdf')
