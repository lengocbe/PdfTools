import pytest
from PIL import Image
from services.pdf_to_image_service import pdf_to_images

@pytest.mark.parametrize('format', ['PNG','JPEG'])
@pytest.mark.parametrize('pages', [None, '1,3'])
def test_images(make_pdf,tmp_path,format,pages):
    source = make_pdf('test.pdf',3)
    progress = []
    result = pdf_to_images(source,tmp_path,pages,format,96,progress_callback=lambda *event: progress.append(event))
    assert len(result.outputs) == (3 if pages is None else 2)
    for path in result.outputs:
        assert path.stat().st_size > 100
        with Image.open(path) as image:
            assert image.size == (400,534)
            assert image.format == format
    assert progress[-1][0] == progress[-1][1]
