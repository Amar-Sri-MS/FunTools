#!/usr/bin/env python3

"""Convert jupyter notebook to html, optinally run the notebook

ex > python ./convert_nb.py --filename malloc_report.ipynb --execute

"""

import nbformat
from nbconvert.preprocessors import ExecutePreprocessor
from nbconvert import HTMLExporter
from nbconvert import PDFExporter

import argparse
import os
import shutil
import time
from datetime import datetime
import logging
import inspect

# A logger for this file
logger = logging.getLogger(__name__)

"""requirements


nbformat                          5.1.3
nbconvert                         6.4.2
numpy                             1.22.2
matplotlib                        3.5.1
matplotlib-inline                 0.1.3

hydra-colorlog                    1.1.0
hydra-core                        1.1.1

#jupyter

#pandoc
# on linux: need this
# sudo apt-get install texlive texlive-latex-extra pandoc

"""


def _gets_timestamp():
    ts = time.time()
    return datetime.fromtimestamp(ts).strftime("%Y-%m-%d %H:%M:%S")


def _parse_args_local():
    my_parser = argparse.ArgumentParser()

    my_parser.add_argument(
        "--filename",
        type=str,
        default="malloc_report.ipynb",
        help="Jupyter notebook filename",
    )

    my_parser.add_argument("--execute", action="store_true", help="Execute notebook")

    args = my_parser.parse_args()

    return args


def save_to_html(nb, filename, out_dir=""):
    """save notebook to html

    - https://stackoverflow.com/questions/65502005/convert-a-jupyter-notebook-to-html-output-in-native-python

    Parameters
    ----------
    nb: notebook
        notebook

    filename: str
        output file name

    out_dir: str
        output director

    Returns
    -------
    html_filename: str
        html saved filename
    """

    filename = os.path.join(out_dir, filename)

    logger.info("Output html path: {}".format(filename))
    # export to html
    html_exporter = HTMLExporter()
    html_exporter.exclude_input = True
    html_data, resources = html_exporter.from_notebook_node(nb)

    try:
        # write to output file
        with open(filename, "w") as f:
            f.write(html_data)
    except Exception as ex:
        logger.error("Exception {}".format(ex))
        filename = None

    return filename


def get_module_info(mod, logger=logger):
    """Get module info
    Parameters
    ----------
    mod: str
        Module name

    Returns
    -------
    mod_file: str
        module code full path
    mod_dirname: str
        module base dir

    """
    mod_file = inspect.getmodule(mod).__file__
    mod_dirname = os.path.dirname(mod_file)
    logger.debug("Mod name : {}".format(mod_file))
    logger.debug("Base dir : {}".format(mod_dirname))

    return mod_file, mod_dirname


def generate_report(
    notebook_filename,
    in_dir="",
    out_dir="",
    execute=False,
    working_dir=".",
    logger=logger,
    report_filename=None,
    backup_notebook=False,
):
    """Generate report based on notebook

    Parameters
    ----------
    notebook_filename: str
        notebook name
    in_dir: str
        notebook directory
    out_dir: str
        directory for generate file
    execute: bool
        to run notebook or not
    working_dir: str
        directory to run notebook, so that we can pick up the data files
    logger: logger
        logger
    report_filename: str
        output filename
    backup_noteook: bool
        if we save backup notebook or not

    Returns
    -------
    html_filename: str
        generate html filename

    """

    html_filename = None
    try:
        in_notebook = os.path.join(in_dir, notebook_filename)
        updated_notebook_dir = os.path.join(in_dir, "notebook_out")
        if not os.path.isdir(updated_notebook_dir):
            os.makedirs(updated_notebook_dir)

        # output notebook, but keep the input notebook as is, i.e. not populating cells
        out_notebook = os.path.join(updated_notebook_dir, notebook_filename)

        logger.info("in_notebook: {}".format(in_notebook))
        logger.info("out_notebook: {}".format(out_notebook))

        nb = nbformat.read(open(in_notebook), as_version=4)

        if execute:
            if backup_notebook:
                backup_filename = "{}_{}".format(in_notebook, _gets_timestamp())
                shutil.copyfile(in_notebook, backup_filename)
            ep = ExecutePreprocessor(timeout=600, kernel_name="python3")
            ep.preprocess(nb, {"metadata": {"path": working_dir}})
            # overwrite
            nbformat.write(nb, open(out_notebook, mode="wt"))

        report_name = (
            report_filename
            if report_filename
            else "{}.html".format(os.path.splitext(notebook_filename)[0])
        )
        html_filename = save_to_html(nb, report_name, out_dir)

    except Exception as ex:
        logger.error("Exception {}".format(ex))
    return html_filename


def main():
    args = _parse_args_local()

    notebook_filename = args.filename
    generate_report(notebook_filename)


if __name__ == "__main__":
    main()
