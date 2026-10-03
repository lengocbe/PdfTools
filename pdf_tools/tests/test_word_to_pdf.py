from pathlib import Path
from types import SimpleNamespace
import pytest
from pypdf import PdfWriter, PdfReader
from services import word_to_pdf_service as service
from utils.errors import AppError


def test_validation(tmp_path):
    with pytest.raises(AppError,match='ít nhất'):
        service.validate_word_to_pdf_request([],tmp_path)
    a = tmp_path / 'hợp đồng.docx'; a.write_bytes(b'word')
    b = tmp_path / 'hợp đồng.doc'; b.write_bytes(b'word')
    with pytest.raises(AppError,match='trùng'):
        service.validate_word_to_pdf_request([a,b],tmp_path)
    target = tmp_path / 'hợp đồng.pdf'; target.write_bytes(b'previous')
    with pytest.raises(AppError,match='đã tồn tại'):
        service.validate_word_to_pdf_request([a],tmp_path)
    assert service.validate_word_to_pdf_request([a],tmp_path,True)[1] == [target]


@pytest.mark.parametrize('failure',['none','export','close','quit'])
def test_export_batch_and_cleanup(tmp_path,monkeypatch,failure):
    calls = []
    class Document:
        Windows = SimpleNamespace(Item=lambda index:SimpleNamespace(Hwnd=1))
        def __init__(self,name='bootstrap'):
            self.name = name
        def ExportAsFixedFormat(self,**kwargs):
            calls.append(('export',kwargs['ExportFormat'],kwargs['OpenAfterExport']))
            if failure == 'export' and self.name == 'a.docx':
                raise RuntimeError('export failed')
            writer = PdfWriter(); writer.add_blank_page(width=100,height=200)
            writer.write(Path(kwargs['OutputFileName']))
        def Close(self,**kwargs):
            calls.append('close')
            if failure == 'close' and self.name == 'a.docx':
                raise RuntimeError('close failed')
    class Word:
        Documents = SimpleNamespace(Add=lambda **kw:Document(),
                                    Open=lambda **kw:Document(Path(kw['FileName']).name))
        def Quit(self,**kw):
            calls.append('quit')
            if failure == 'quit':
                raise RuntimeError('quit failed')
    class Handle:
        def Close(self):
            calls.append('handle_close')
    com = SimpleNamespace(CoInitialize=lambda:calls.append('init'),CoUninitialize=lambda:calls.append('uninit'))
    client = SimpleNamespace(DispatchEx=lambda name:Word())
    api = SimpleNamespace(OpenProcess=lambda *args:Handle(),TerminateProcess=lambda *args:calls.append('terminate'))
    event = SimpleNamespace(WaitForSingleObject=lambda *args:258 if failure == 'quit' else 0)
    process = SimpleNamespace(GetWindowThreadProcessId=lambda hwnd:(1,123))
    monkeypatch.setattr(service,'_load_com',lambda:(com,client,api,event,process))
    sources = [tmp_path/'a.docx',tmp_path/'b.docx']
    for path in sources:
        path.write_bytes(b'source')
    progress = []
    result = service.word_to_pdf(sources,tmp_path,progress_callback=lambda *args:progress.append(args))
    expected = {'none':2,'export':1,'close':0,'quit':2}[failure]
    assert len(result.outputs) == expected
    assert bool(result.errors) == (failure in ('export','close'))
    assert calls[0] == 'init' and calls[-1] == 'uninit'
    assert 'quit' in calls and 'handle_close' in calls
    assert ('terminate' in calls) == (failure == 'quit')
    assert all(len(PdfReader(path).pages) == 1 for path in result.outputs)
    assert all(path.read_bytes() == b'source' for path in sources)
    assert not list(tmp_path.glob('.pdftools-*'))
    if failure != 'close':
        assert progress[-1][:2] == (2,2)


def test_missing_word(tmp_path,monkeypatch):
    calls = []
    def fail(name):
        raise RuntimeError('not installed')
    com = SimpleNamespace(CoInitialize=lambda:None,CoUninitialize=lambda:calls.append('uninit'))
    monkeypatch.setattr(service,'_load_com',lambda:(com,SimpleNamespace(DispatchEx=fail),None,None,None))
    source = tmp_path / 'a.docx'; source.write_bytes(b'word')
    with pytest.raises(AppError,match='Không tìm thấy Microsoft Word'):
        service.word_to_pdf([source],tmp_path)
    assert calls == ['uninit']
