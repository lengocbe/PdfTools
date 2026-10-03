import json
from utils.history import HistoryStore
from utils.file_metadata import describe_pdf


def test_history_is_bounded_and_persistent(tmp_path):
    path = tmp_path / 'history.json'
    store = HistoryStore(path)
    for count in range(105):
        store.add('Cắt PDF',count,'Hoàn tất','D:/Tài liệu')
    loaded = HistoryStore(path)
    assert len(loaded.records) == 100
    assert loaded.records[0]['count'] == 104
    assert loaded.records[-1]['count'] == 5
    assert loaded.records[0]['folder'] == 'D:/Tài liệu'


def test_invalid_history_falls_back(tmp_path):
    path = tmp_path / 'history.json'
    path.write_text('invalid',encoding='utf-8')
    assert HistoryStore(path).records == []
    path.write_text(json.dumps([{'bad':'data'},None,{'time':'a','task':'b','status':'c','folder':'d','count':'bad'}]))
    assert HistoryStore(path).records == []


def test_pdf_metadata(make_pdf):
    path = make_pdf('Thông tin.pdf',3)
    assert '3 trang' in describe_pdf(str(path))
