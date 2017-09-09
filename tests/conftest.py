import pytest

from . import pypic as pp
from . import reqtuple

@pytest.fixture
def successful_req(request):
    return reqtuple(status_code=200, content="", url="")

@pytest.fixture
def failed_req(request):
    return reqtuple(status_code=404, content="", url="")

@pytest.fixture
def search_result_string(request):
    return "<table><tr class='odd'><td><a href='curl_to_requests/1.0.1'>\
curl_to_requests&nbsp;1.0.1</a></td><td>9</td>\
<td>Converts cURL commands into equivalent Python Requests code</td></tr>\
<tr class='even'><td><a href='drequests/1.3'>drequests&nbsp;1.3</a></td>\
<td>9</td><td>The descusr web application development framework,\
a drequests project</td></tr></table>"

@pytest.fixture
def fake_req_with_content(request, search_result_string):
    return reqtuple(status_code=200, url="req_url",
                    content=search_result_string)

@pytest.fixture
def failed_search_with_content(request):
    return reqtuple(status_code=200, url="fake_req_url", content="<html></html>")

@pytest.fixture
def parser1(request):
    return pp.PyPiParser()

@pytest.fixture
def parser2(request):
    """Returns a parser with current set to an empty SearchResult class.
    Some test data use partial html that prevents the attribute from been set
    naturally.
    """
    parser = pp.PyPiParser()
    parser.curr = pp.SearchResult()
    return parser

@pytest.fixture
def fake_results(request):
    result1 = pp.SearchResult(
        name='pypi', version='0.1.0', weight=20,
        desc='the most awesome python package ever. pretend i never said that')
    result2 = pp.SearchResult(
        name='qbt-plugins', version='1.1.3', weight=8,
        desc="Man you've got to try qbittorrent.")
    return [result1, result2]
