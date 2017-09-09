import logging
from unittest.mock import (patch, MagicMock)

import pytest

from . import pypic as pp
from . import requests

logging.getLogger(__file__)

################################################################################
#                                TESTS FOR NORMALISE                           #
################################################################################


def test_normalise_replaces_runs_of_period_with_single_hyphen():
    expected = "me-test"
    assert pp.normalise("me..test") == expected


def test_normalise_replace_runs_of_hyphen_with_single_hyphen():
    assert pp.normalise("me---test") == "me-test"


def test_calling_normalise_with_float_as_name_raises_type_error():
    with pytest.raises(TypeError):
        print(pp.normalise(0.1))


def test_calling_normalise_with_type_int_raises_type_error():
    with pytest.raises(TypeError):
        print(pp.normalise(100))


def test_calling_normalise_with_a_normalised_name_returns_the_same_name():
    name = "py-test"
    assert pp.normalise(name) == name


def test_one_line_replaces_runs_of_tab_chars_with_single_space_char():
    assert pp.one_line("ama\t\t\tasiamah") == 'ama asiamah'


def test_one_line_replace_runs_of_new_line_with_single_space_char():
    assert pp.one_line("ama\n\n\n\nasia\n\nmah") == 'ama asia mah'


################################################################################
#                                 TESTS FOR EXISTS                             #
################################################################################

@patch('requests.get')
def test_exists_returns_true_for_requests_package_if_version_is_none(
        fake_req, successful_req):
    fake_req.return_value = successful_req
    assert pp.exists("requests") is True


@patch('requests.get')
def test_exists_returns_true_if_pkg_name_and_version_is_supplied(
        fake_req, successful_req):
    fake_req.return_value = successful_req
    assert pp.exists("requests", version="2000.0.1") is True


@patch('requests.get')
def test_exists_returns_false_if_request_has_404_status_code(
        fake_req, failed_req):
    fake_req.return_value = failed_req
    assert pp.exists("pypic", "0.1") is False


@patch('requests.get')
def test_exists_if_version_is_none_returns_false_if_for_failed_request(
        fake_req, failed_req):
    fake_req.return_value = failed_req
    assert pp.exists("requests") is False


################################################################################
#                                TESTS FOR SEARCH                              #
################################################################################

@patch('requests.get')
def test_search_for_non_existent_package_returns_empty_list(
        fake_req, failed_search_with_content):
    fake_req.return_value = failed_search_with_content
    search_term = "1a2b23c4d du38334"
    assert pp.search(search_term) == []

@patch('requests.get')
def test_search_for_package_returns_correct_result_for_existing_term(
        fake_get, fake_req_with_content):
    fake_get.return_value = fake_req_with_content
    result = pp.search('dummy')
    assert len(result) == 2


@patch('requests.get')
def test_search_raises_pypic_error_if_request_returns_connection_error(fake_req):
    fake_req.return_value = MagicMock(
        side_effect=requests.exceptions.ConnectionError)
    fake_req.status_code = 404
    with pytest.raises(pp.PyPicError):
        pp.search("This will create a connection problem")


class TestSearchResultClass:
    def test_create_search_result_with_no_args_sets_all_attribs_to_none(self):
        sr = pp.SearchResult()
        for item in ('name', 'version', 'weight', 'desc'):
            assert sr.__getattribute__(item) is None

    def test_initialise_search_result_with_strange_keywords_raises_attribute(self):
        with pytest.raises(AttributeError):
            pp.SearchResult(name='pypic', popularity='100%')

    def test_initialise_search_result_with_good_keyword_args_set_attributes(self):
        sr = pp.SearchResult(name='pypic', version='0.1.0', weight=45, desc='awesome')
        assert sr.name == 'pypic'
        assert sr.version == '0.1.0'
        assert sr.weight == 45
        assert sr.desc == 'awesome'


class TestPyPiParser:
    def test_creation_of_pypi_parser_sets_start_handling_to_false(self, parser1):
        assert parser1.start_handling is False

    def test_creation_of_pypi_parser_sets_result_to_empty_list(self, parser1):
        assert parser1.results == []

    def test_pypi_parser_sets_handling_to_true_if_a_table_tag_is_parsed(self, parser1):
        parser1.feed("<table><tr><b></b>")
        assert parser1.start_handling is True

    def test_start_handling_remains_false_if_no_table_tag_is_parsed(self, parser2):
        parser2.feed("<tr><td>1</td></tr>")
        assert parser2.start_handling is False

    def test_start_handling_is_set_to_false_when_end_table_tag_is_parsed(self, parser2):
        parser2.start_handling = True
        parser2.feed("<tr><td>12</td></tr></table>")
        assert parser2.start_handling is False

    def test_name_data_is_set_to_true_when_tag_a_is_parsed(self, parser1):
        parser1.feed("<table><a href='dummy_url'>")
        assert parser1.name_data is True

    def test_td_count_is_set_to_zero_when_tag_a_data_is_parsed(self, parser1):
        parser1.feed("<table><a href='dummy_url'>pypic\xa00.1.0</a>")
        assert parser1.td_count == 0

    def test_name_data_is_set_to_false_when_tag_a_data_is_parsed(self, parser1):
        parser1.feed("<table><a href='dummy_url'>pypic\xa00.1.0</a>")
        assert parser1.name_data is False
