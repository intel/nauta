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

import logging

import pytest

import util.logger as logger


def test_initialize_logger():
    mock_package_name = 'mock_package'
    default_log_level = logging.DEBUG
    default_stream_handler_log_level = logging.CRITICAL

    mock_logger = logger.initialize_logger(mock_package_name)

    assert mock_logger
    assert logging.getLogger(mock_package_name).getEffectiveLevel() == default_log_level
    assert logger.STREAM_HANDLER.level == default_stream_handler_log_level


@pytest.mark.parametrize('mock_verbosity,expected_log_level', [(0, logging.CRITICAL), (1, logging.INFO),
                                                               (2, logging.DEBUG), (5, logging.DEBUG)])
def test_set_verbosity_level(mock_verbosity, expected_log_level):
    logger.set_verbosity_level(mock_verbosity)
    assert logger.get_verbosity_level() == expected_log_level
