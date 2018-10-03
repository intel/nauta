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

from os import path

import nbformat

from util.logger import initialize_logger
from util.exceptions import ScriptConversionError
from cli_text_consts import UtilJupyterTexts as Texts


logger = initialize_logger(__name__)

# metadata describing kernel used to run our script
notebook_metadata = {"kernelspec": {
                        "display_name": "Python 3",
                        "language": "python",
                        "name": "python3"
                    },
                    "language_info": {
                        "codemirror_mode": {
                            "name": "ipython",
                            "version": 3
                        },
                        "file_extension": ".py",
                        "mimetype": "text/x-python",
                        "name": "python",
                        "nbconvert_exporter": "python",
                        "pygments_lexer": "ipython3",
                    }
                    }


def convert_py_to_ipynb(py_filename: str, ipynb_location: str) -> bool:
    """
    Function converts a python file with a name given as the py_filename paramater to
    Jupyter Notebook file (.ipynb) and stores this file in the location taken from
    the ipynb_location paramater. Name of file is created from a name of a python file
    extended with .ipynb extension.
    It creates notebook file for Python 3 at the moment

    :param py_filename: a path and a name of a file with python code
    :param ipynb_location: path to a place where ipynb file will be stored
    :return: name of an output file, exception in case of any errors
    """
    cells = []

    try:
        with open(py_filename, 'r') as file:
            cell = nbformat.v4.new_code_cell(source=file.read())
            cells.append(cell)

            output_notebook = nbformat.v4.new_notebook(cells=cells, metadata=notebook_metadata)

            py_filename = path.basename(py_filename)

            ipynb_filename = ".".join(py_filename.split(".")[:-1]) + ".ipynb"

            ipynb_full_path = path.join(ipynb_location, ipynb_filename)
            nbformat.write(output_notebook, ipynb_full_path, nbformat.NO_CONVERT)
    except Exception:
        err_message = Texts.IPYNB_CONVERSION_ERROR_MSG
        logger.exception(err_message)
        raise ScriptConversionError(err_message)

    return ipynb_filename
