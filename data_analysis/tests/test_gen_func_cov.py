"""Test code for gen_func_cov.py"""

import filecmp
import os

from gen_func_cov import *


def remove_file(file):
    # remove file if it exists
    if os.path.exists(file):
        os.remove(file)


def test_get_html_file():
    local_file = None
    module = "all"
    build_no = 131
    html_file = get_html_file(build_no, module, local_file)
    url = BUILD_URL.format(build_no, module)
    print(html_file)
    assert html_file == url

    local_file = "tests/index.functions.html"
    module = "all"
    build_no = None
    html_file = get_html_file(build_no, module, local_file)
    print(html_file)
    assert html_file == local_file


def test_extract_html():
    ref_local_file = "tests/index.functions.html"
    gen_html_doc_file = "tests/index.functions.html.out"

    remove_file(gen_html_doc_file)

    module = "all"
    build_no = None
    html_file = get_html_file(build_no, module, ref_local_file)
    html_doc = extract_html(html_file)

    # save to file
    with open(gen_html_doc_file, "w", encoding="utf-8") as f:
        f.write(html_doc)

    # diff the two files
    diff = filecmp.cmp(ref_local_file, gen_html_doc_file)
    # check the diff
    assert diff


def test_extract_table():
    # from previous test
    gen_html_doc_file = "tests/index.functions.html.out"

    ref_df_csv = "tests/index.functions.csv"
    gen_csv = "tests/df_extracted.csv"

    remove_file(gen_csv)

    # read file
    with open(gen_html_doc_file, "r", encoding="utf-8") as f:
        html_doc = f.read()

    df = extract_table(html_doc)

    # save df to csv
    df.to_csv(gen_csv, index=False)

    # diff the two files
    diff = filecmp.cmp(ref_df_csv, gen_csv)
    # check the diff
    assert diff

    remove_file(gen_html_doc_file)
    remove_file(gen_csv)
