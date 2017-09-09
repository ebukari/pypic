"""
Compare pypi packages
"""
import re
import logging
from collections import OrderedDict

# python 2 & python 3 import workarounds
try:
    from html.parser import HTMLParser
except ImportError:  # pragma: no cover
    from HTMLParser import HTMLParser

import requests

__version__ = '0.1.0'
NBSP = "\xa0"   # unicode for non-breaking space
STATUS = 'testing'
BASE = 'http://testpypi.python.org'
JSON_PKG_DATA = BASE + "/{pkg_name}/json"
JSON_PKG_VER_DATA = BASE + "/{pkg_name}/{pkg_ver}/json"
SEARCH_URL = BASE + "?:"


class PyPicError(Exception):
    pass


class SearchResult(object):
    __slots__ = ('name', 'version', 'weight', 'desc')

    def __init__(self, **kw):
        for key in kw:
            if key not in self.__slots__:
                raise AttributeError('SearchResult has no attribute %s' % key)
        self.name = kw.get('name', None)
        self.version = kw.get('version', None)
        self.weight = kw.get('weight', None)
        self.desc = kw.get('desc', None)


class PyPiParser(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self)
        self.start_handling = False
        self.td_count = 0
        self.name_data = False
        self.curr = None
        self.results = []

    def get_results(self):
        return self.results

    def handle_starttag(self, tag, attrs):
        logging.info("Calling handle_starttag with tag = %s\tattrs = %s"
                     % (tag, attrs))
        if tag == 'table':
            self.start_handling = True
        if not self.start_handling:
            return
        if tag == 'a':
            self.curr = SearchResult()
            self.name_data = True

    def handle_endtag(self, tag):
        # logging.info('Calling handle_endtag with tag = %s'.format(tag))
        if tag == 'tr':
            self.results.append(self.curr)
        elif tag == 'table':
            self.start_handling = False

    def handle_data(self, data):
        # logging.info('Calling handle_data with data = {}'.format(data))
        data = data.strip()
        if self.name_data:
            name, version = data.split(NBSP)
            self.curr.name = name
            self.curr.version = version
            # next data i.e. from td tag must be handled by else
            self.name_data = False
            # reset td_count so not to raise IndexError
            self.td_count = 0
        else:
            if self.td_count == 0:
                self.curr.weight = int(data)
            else:
                self.curr.desc = one_line(data)
            self.td_count += 1


def one_line(string):
    """
    Replaces all runs of whitespace with a single space char
    :param string:
    :return: string with all runs of whitespace replaced with a single space
    """
    return re.sub("\s+", " ", string)


def exists(name, version=None):
    """
    Checks if a package exists on pypi.python.org
    If version is not None, checks whether that version
    of the package exists
    :param name: the name of the package
    :type name: str
    :param version: the version of the package
    :type version: str
    :return: True if package exists else False
    """
    logging.debug("Calling exists with name = %s\tversion = %s"
                  % (name, version))
    name = normalise(name)
    if version:
        url = JSON_PKG_VER_DATA.format(pkg_name=name, pkg_ver=version)
    else:
        url = JSON_PKG_DATA.format(pkg_name=name)
    logging.debug("url='{}'".format(url))
    pkg_data = requests.get(url)
    return pkg_data.status_code == 200


def normalise(name):
    """Edit a name to fit pypi standards
    Replaces runs of these chars: -._ with a single -.
    """
    logging.info("Calling normalise with name='{}'".format(name))
    return re.sub(r"[-_.]+", "-", name).lower()

normalize = normalise


def search(*keywords):
    """Search on pypi for a given keywords
    :param keywords: the words to search for
    :type keywords: str
    """
    logging.info("Calling search with keywords = %s" % keywords)
    terms = "+".join(keywords).replace(" ", "+")
    search_args = {"action": "search", 'terms': terms, 'submit': 'search'}
    try:
        search_req = requests.get(SEARCH_URL, params=search_args)
        logging.debug("request for url='%s' return %s status code" %
                      (search_req.url, search_req.status_code))
    except requests.exceptions.ConnectionError:
        logging.error("There was an error when connecting to pypi servers.")
        raise PyPicError("Data could not be retrieved from PyPi servers.")
    parser = PyPiParser()
    for string in search_req.iter_content():
        parser.feed(string)
    return parser.get_results()


if __name__ == '__main__':
    template = "{sr.name:>14} {sr.version:<5} {sr.weight:4} {sr.desc:<20}"
    for result in search("pypi"):
        print(template.format(sr=result))
