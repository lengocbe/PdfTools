import pytest
from utils.page_range import parse_pages, parse_range_groups
from utils.errors import AppError

@pytest.mark.parametrize('text,expected', [
    ('1',[1]), ('1,3,5',[1,3,5]), ('1-5',[1,2,3,4,5]),
    ('1,3,5-8',[1,3,5,6,7,8]), ('1; 3; 5-8',[1,3,5,6,7,8]),
    ('1\n3\n5-8',[1,3,5,6,7,8]), (' 1 , 3 - 4 ',[1,3,4])])
def test_valid(text, expected):
    assert parse_pages(text, 10) == expected

@pytest.mark.parametrize('text', ['', '0', '-1', '5-3', 'a', '1-a', '999', '1,,2', '1 2', '1.5'])
def test_invalid(text):
    with pytest.raises(AppError):
        parse_pages(text, 10)

def test_groups_and_duplicates():
    assert parse_range_groups('3-4,7-8') == [(3,4),(7,8)]
    assert parse_pages('3,1-3') == [3,1,2]
