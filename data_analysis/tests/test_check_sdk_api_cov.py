"""Test code for gen_func_cov.py"""

import filecmp
import os
import pandas as pd
import math

from check_sdk_api_cov import *


def remove_file(file):
    # remove file if it exists
    if os.path.exists(file):
        os.remove(file)


def test_update_coverage_for_sdk_api():
    # read csv
    ref_sdk_api_csv = "tests/sdk_api.csv"
    ref_cov_df_csv = "tests/index.functions.csv"
    ref_cov_percent = 53.51

    df_api = pd.read_csv(ref_sdk_api_csv)
    df_cov = pd.read_csv(ref_cov_df_csv)

    df_api, cov_percent = update_coverage_for_sdk_api(df_api, df_cov)
    print(cov_percent)
    assert math.isclose(cov_percent, ref_cov_percent, rel_tol=1e-2)
