#
# Copyright (c) 2019 Intel Corporation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

import pytest
from unittest.mock import patch, mock_open

from util.jupyter_notebook_creator import convert_py_to_ipynb
from util.exceptions import ScriptConversionError
from util.tests.nbformat_mocks import create_nb_format_mocks  # noqa: F401

py_file = "first line \n second_line"

PY_FILENAME = "py_filename.py"
IPYNB_FILENAME = "py_filename.ipynb"
IPYNB_LOCATION = "/ipynb_location/"


def test_conversion_success(create_nb_format_mocks):  # noqa: F811
    m = mock_open(read_data=py_file)
    m.return_value.__iter__ = lambda self: self
    m.return_value.__next__ = lambda self: next(iter(self.readline, ''))

    with patch('builtins.open', m, create=True):
        filename = convert_py_to_ipynb("py_filename.py", "/ipynb_location/")

    assert filename == IPYNB_FILENAME
    args, _ = create_nb_format_mocks.call_args

    assert args[0]["metadata"]["kernelspec"]["display_name"] == "Python 3"
    cells_list = args[0]["cells"]

    for cell in cells_list:
        assert cell["source"] in py_file


def test_conversion_failure(create_nb_format_mocks):  # noqa: F811
    m = mock_open()
    m.side_effect = RuntimeError()

    with pytest.raises(ScriptConversionError):
        with patch('builtins.open', m, create=True):
            convert_py_to_ipynb("py_filename.py", "/ipynb_location/")
