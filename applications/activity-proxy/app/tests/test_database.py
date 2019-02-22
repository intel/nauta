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
