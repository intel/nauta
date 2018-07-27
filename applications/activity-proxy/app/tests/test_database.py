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

from datetime import datetime

import sqlite3
import pytest

import database


def test_init_db(mocker):
    fake_connection = mocker.MagicMock()
    mocker.patch('sqlite3.connect').return_value = fake_connection
    database.init_db()

    assert fake_connection.execute.call_count == 2
    assert fake_connection.commit.call_count == 1
    assert fake_connection.close.call_count == 1


def test_init_db_already_exists(mocker):
    fake_connection = mocker.MagicMock()
    mocker.patch.object(fake_connection, 'execute').side_effect = sqlite3.OperationalError('already exists')
    mocker.patch('sqlite3.connect').return_value = fake_connection

    database.init_db()

    assert fake_connection.execute.call_count == 1
    assert fake_connection.commit.call_count == 0
    assert fake_connection.close.call_count == 1


def test_init_db_unknown_error(mocker):
    fake_connection = mocker.MagicMock()
    mocker.patch.object(fake_connection, 'execute').side_effect = sqlite3.OperationalError
    mocker.patch('sqlite3.connect').return_value = fake_connection

    with pytest.raises(sqlite3.OperationalError):
        database.init_db()



def test_update_timestamp(mocker):
    fake_connection = mocker.MagicMock()
    mocker.patch('sqlite3.connect').return_value = fake_connection
    database.update_timestamp()

    assert fake_connection.execute.call_count == 1
    assert fake_connection.commit.call_count == 1
    assert fake_connection.close.call_count == 1


def test_get_timestamp(mocker):
    expected_datetime_return = datetime(year=2018, month=7, day=26, hour=11, minute=41, second=26)
    fake_cursor = mocker.MagicMock(fetchone=lambda: ('26.07.2018 11:41:26',))
    mocker.spy(fake_cursor, 'fetchone')
    fake_connection = mocker.MagicMock(execute=lambda *args: fake_cursor)
    mocker.spy(fake_connection, 'execute')
    mocker.patch('sqlite3.connect').return_value = fake_connection
    timestamp = database.get_timestamp()

    assert timestamp == expected_datetime_return
    assert fake_connection.execute.call_count == 1
    assert fake_cursor.fetchone.call_count == 1
    assert fake_connection.close.call_count == 1
