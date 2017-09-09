import sys
# import os
from os.path import abspath, join, dirname
from collections import namedtuple

import requests

PYPIC = abspath(dirname(dirname(__file__)))
sys.path.insert(0, join(PYPIC, 'pypic'))

import pypic

TESTDIR = abspath(dirname(__file__))
FIXTURE_DIR = join(TESTDIR, "fixtures")
LOGS_PATH = join(PYPIC, 'logs')

reqtuple = namedtuple("RequestTuple", ("status_code", "content", "url"))
