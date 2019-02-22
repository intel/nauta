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

DATABASE_FILENAME = 'proxy.db'

DATETIME_STRING_FORMAT = '%d.%m.%Y %H:%M:%S'


def init_db():
    c = sqlite3.connect(DATABASE_FILENAME)
    try:
        c.execute('CREATE TABLE main (datetimestamp TEXT)')
        current_datetime = datetime.utcnow().strftime(DATETIME_STRING_FORMAT)
        c.execute(f"INSERT INTO main VALUES ('{current_datetime}')")
        c.commit()
    except sqlite3.OperationalError as ex:
        if "already exists" in str(ex):
            pass
        else:
            raise
    finally:
        c.close()


def update_timestamp():
    c = sqlite3.connect(DATABASE_FILENAME)
    current_datetime = datetime.utcnow().strftime(DATETIME_STRING_FORMAT)
    c.execute(f"UPDATE main SET datetimestamp='{current_datetime}'")
    c.commit()
    c.close()


def get_timestamp() -> datetime:
    c = sqlite3.connect(DATABASE_FILENAME)
    cur = c.execute('SELECT * FROM main')
    db_datetimestamp = cur.fetchone()
    c.close()

    result = datetime.strptime(db_datetimestamp[0], DATETIME_STRING_FORMAT)

    return result
