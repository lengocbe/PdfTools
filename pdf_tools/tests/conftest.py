from pathlib import Path
import pytest
from reportlab.pdfgen.canvas import Canvas

@pytest.fixture
def make_pdf(tmp_path):
    def create(name: str, count: int, label: str = 'page', size=(300, 400)) -> Path:
        path = tmp_path / name
        canvas = Canvas(str(path), pagesize=size)
        for i in range(count):
            canvas.drawString(30, 100, f'{label} {i + 1}')
            canvas.showPage()
        canvas.save()
        return path
    return create
