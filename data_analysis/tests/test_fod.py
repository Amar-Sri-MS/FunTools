"""Test code for fod code"""

import filecmp
import os
import pandas as pd
import math

from utils import *
from utils_fod import *
from utils_plot import *


def test_extract_pages():
    CONFIG_FILE = "tests/test_fod.yml"
    config = read_config(CONFIG_FILE)
    collected_jobs = fod_extract_pages(config)
    pattern = config["search_pattern"].format(20)
    filter_line_with_pattern = fod_extract_lines_with_pattern_from_console(
        collected_jobs[0]["console_response"], pattern
    )
    assert 20 == len(filter_line_with_pattern)

    extracted_json = fod_extract_json_from_line(filter_line_with_pattern)
    assert 20 == len(extracted_json)
