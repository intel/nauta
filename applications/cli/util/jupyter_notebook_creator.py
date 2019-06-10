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


def convert_py_to_ipynb(py_filename: str, ipynb_location: str) -> str:
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
