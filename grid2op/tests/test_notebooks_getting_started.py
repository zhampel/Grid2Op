import os
import shutil
import sys
import unittest
import json
import numpy as np
import subprocess

import pdb

import nbformat
from nbconvert.preprocessors import ExecutePreprocessor, CellExecutionError

from grid2op.tests.helper_path_test import *

# TODO check these tests, they don't appear to be working

def delete_all(folder):
    """
    Delete all the files in a folder recursively.

    Parameters
    ----------
    folder: ``str``
        The folder in which we delete everything

    Returns
    -------
    None
    """
    for filename in os.listdir(folder):
        file_path = os.path.join(folder, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print('Failed to delete %s. Reason: %s' % (file_path, e))


def export_all_notebook(folder_in):
    """

    Parameters
    ----------
    folder_in: ``str``
        The folder in which we look for ipynb files

    folder_out: ``str``
        The folder in which we save the py file.

    Returns
    -------
    res: ``list``
        Return the list of notebooks names

    """
    res = []
    for filename in os.listdir(folder_in):
        if os.path.splitext(filename)[1] == ".ipynb":
            notebook_filename = os.path.join(folder_in, filename)
            res.append(notebook_filename)
    return res


class TestNotebook(unittest.TestCase):
    pass


if __name__ == "__main__":
    notebooks_path = os.path.abspath(os.path.join(PATH_DATA_TEST, "../../getting_started"))
    path_save_notebook = os.path.join(PATH_DATA_TEST, "../tests/test_notebooks")

    if not os.path.exists(path_save_notebook):
        os.mkdir(path_save_notebook)
    else:
        delete_all(path_save_notebook)

    all_notebook = export_all_notebook(notebooks_path)

    all_funs = []
    for notebook_filename in all_notebook:
        def f(self):
            with open(notebook_filename) as f:
                nb = nbformat.read(f, as_version=4)
                ep = ExecutePreprocessor(timeout=600)
                try:
                    ep.preprocess(nb, {'metadata': {'path': path_save_notebook}})
                except CellExecutionError:
                    raise
        all_funs.append(("test_{}".format(os.path.split(notebook_filename)[-1]), f))

    for nm, f in all_funs:
        pass
        # setattr(TestNotebook, nm, f)

    unittest.main()

