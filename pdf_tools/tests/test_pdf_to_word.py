from types import SimpleNamespace
from pathlib import Path
import pytest
from services import pdf_to_word_service as service
from utils.errors import AppError


def test_validation(make_pdf,tmp_path):
    with pytest.raises(AppError):
        service.validate_word_request([],tmp_path)
    source = make_pdf('sample.pdf',1)
    (tmp_path / 'sample.docx').write_bytes(b'existing')
    with pytest.raises(AppError):
        service.validate_word_request([source],tmp_path)
    assert service.validate_word_request([source],tmp_path,True)[1] == [tmp_path / 'sample.docx']


@pytest.mark.parametrize('fail_save,fail_quit', [(False,False),(True,False),(False,True)])
def test_cleanup(make_pdf,tmp_path,monkeypatch,fail_save,fail_quit):
    calls = []
    class Document:
        Windows = SimpleNamespace(Item=lambda index:SimpleNamespace(Hwnd=1))
        def SaveAs2(self,**kwargs):
            if fail_save:
                raise RuntimeError('COM error')
            Path(kwargs['FileName']).write_bytes(b'docx')
        def Close(self,**kwargs):
            calls.append('close')
    class Word:
        Hwnd = 1
        Documents = SimpleNamespace(Open=lambda **kwargs:Document(),Add=lambda **kwargs:Document())
        def Quit(self,**kwargs):
            calls.append('quit')
            if fail_quit:
                raise RuntimeError('quit failed')
    class Handle:
        def Close(self):
            calls.append('handle_close')
    com = SimpleNamespace(CoInitialize=lambda:calls.append('init'),CoUninitialize=lambda:calls.append('uninit'))
    client = SimpleNamespace(DispatchEx=lambda name:Word())
    api = SimpleNamespace(OpenProcess=lambda *args:Handle(),TerminateProcess=lambda *args:calls.append('terminate'))
    event = SimpleNamespace(WaitForSingleObject=lambda *args:258 if fail_quit else 0)
    process = SimpleNamespace(GetWindowThreadProcessId=lambda hwnd:(1,123))
    monkeypatch.setattr(service,'_load_com',lambda:(com,client,api,event,process))
    result = service.pdf_to_word([make_pdf('sample.pdf',1)],tmp_path)
    assert calls[0] == 'init' and calls[-1] == 'uninit'
    assert 'close' in calls and 'quit' in calls and 'handle_close' in calls
    assert bool(result.errors) == fail_save
    assert ('terminate' in calls) == fail_quit
    assert not list(tmp_path.glob('.pdftools-*'))

def test_missing_word(make_pdf,tmp_path,monkeypatch):
    calls = []
    def fail(name):
        raise RuntimeError('not registered')
    com = SimpleNamespace(CoInitialize=lambda:None,CoUninitialize=lambda:calls.append('uninit'))
    monkeypatch.setattr(service,'_load_com',lambda:(com,SimpleNamespace(DispatchEx=fail),None,None,None))
    with pytest.raises(AppError,match='Không tìm thấy Microsoft Word'):
        service.pdf_to_word([make_pdf('sample.pdf',1)],tmp_path)
    assert calls == ['uninit']
