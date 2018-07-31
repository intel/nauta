#
# INTEL CONFIDENTIAL
# Copyright (c) 2018 Intel Corporation
#
# The source code contained or described herein and all documents related to
# the source code ("Material") are owned by Intel Corporation or its suppliers
# or licensors. Title to the Material remains with Intel Corporation or its
# suppliers and licensors. The Material contains trade secrets and proprietary
# and confidential information of Intel or its suppliers and licensors. The
# Material is protected by worldwide copyright and trade secret laws and treaty
# provisions. No part of the Material may be used, copied, reproduced, modified,
# published, uploaded, posted, transmitted, distributed, or disclosed in any way
# without Intel's prior express written permission.
#
# No license under any patent, copyright, trade secret or other intellectual
# property right is granted to or conferred upon you by disclosure or delivery
# of the Materials, either expressly, by implication, inducement, estoppel or
# otherwise. Any license under such intellectual property rights must be express
# and approved by Intel in writing.
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
