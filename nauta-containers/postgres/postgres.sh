#!/bin/bash -e
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


echo "Checking PGDATA($PGDATA) content..."
ls -A "${PGDATA}"

chown -R postgres:postgres "${PGDATA}"

if [ -z "$(ls -A ${PGDATA})" ]; then
    echo 'Initialize postgres...'
    if [ -n "${POSTGRES_PASSWORD}" ]; then
        echo 'Setting up postgres with password..'
        echo "${POSTGRES_PASSWORD}" > /tmp/pwfile
        PGSETUP_INITDB_OPTIONS='--pwfile=/tmp/pwfile' postgresql-setup initdb 
    else
        postgresql-setup initdb
    fi
    cat /var/lib/pgsql/initdb.log || true

    cp /etc/pg_hba.conf "${PGDATA}/pg_hba.conf"
    cp /etc/postgresql.conf "${PGDATA}/postgresql.conf"

    if [ -n "${POSTGRES_DB}" ]; then
        echo "POSTGRES_DB: ${POSTGRES_DB}"
        su - postgres -c "echo CREATE DATABASE ${POSTGRES_DB}\; | PGDATA=${PGDATA} postgres --single"
    fi
fi

su - postgres -c "PGDATA=${PGDATA} postgres"
