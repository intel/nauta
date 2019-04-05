#!/usr/bin/env sh
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


set -e

find_bin() {
    for bin in "$@"
    do
        if which ${bin} > /dev/null 2>&1; then
          which ${bin}
          return
        fi
    done
    >&2 echo "Unable to find $@ on your system"
    return 1
}

find_file() {
    PREFIX=$1
    shift 1
    for file in "$@"
    do
        if [ -f "${PREFIX}/${file}" ]; then
            echo "${PREFIX}/${file}"
            return
        fi
    done
    >&2 echo "Unable to find file $@ under ${PREFIX}"
    return 1
}

if [ X"${VIRTUAL_ENV}" = X"" ]; then
    echo "Running inside user space"
    PYTHON=$(find_bin python3.5 python3.6)

    echo "Python found: ${PYTHON}"

    if ! ${PYTHON} -m pip > /dev/null 2>&1; then
        >&2 echo "Unable to find pip in ${PYTHON}. Trying to find pip binary file installed in system PATH"
        PIP=$(find_bin pip3.5 pip3.6)
    else
        PIP="${PYTHON} -m pip"
    fi

    export PYTHONUSERBASE=${CURDIR}/.venv/

    export VIRTUALENV_ENABLED=0
    export NAUTA_VIRTUALENV="${CURDIR}/.venv"
else
    echo "Running inside virtualenv space"
    if find_file "${VIRTUAL_ENV}/bin" python3.5 python3.6 > /dev/null 2>&1; then
        PYTHON=$(find_file "${VIRTUAL_ENV}/bin" python3.5 python3.6)

        export VIRTUALENV_ENABLED=1
        export NAUTA_VIRTUALENV="${VIRTUAL_ENV}"
    else
        echo "Unable to find proper python in virtualenv. Retrying with system one"
        PYTHON=$(find_bin python3.5 python3.6)

        export VIRTUALENV_ENABLED=0
        export NAUTA_VIRTUALENV="${CURDIR}/.venv"
    fi

    if ! ${PYTHON} -m pip > /dev/null 2>&1; then
        >&2 echo "Unable to find pip in ${PYTHON}. Trying to find pip binary file installed in system PATH"
        PIP=$(find_bin pip3.5 pip3.6)

        export VIRTUALENV_ENABLED=0
        export NAUTA_VIRTUALENV="${CURDIR}/.venv"
    else
        PIP="${PYTHON} -m pip"
    fi
fi

if [ ! -f "${NAUTA_VIRTUALENV}/.done" ]; then
    mkdir -p "${NAUTA_VIRTUALENV}"

    if [ X"${VIRTUALENV_ENABLED}" = X"1" ]; then
        ${PIP} install --upgrade pip==19.0.3 --isolated --ignore-installed --no-cache-dir
        ${PIP} install -U -r ${BINDIR}/pip/requirements.txt --isolated --ignore-installed --no-cache-dir
    else
        ${PIP} install --upgrade pip==19.0.3 --isolated --ignore-installed --no-cache-dir
        ${PIP} install -U -r ${BINDIR}/pip/requirements.txt --user --isolated --ignore-installed --no-cache-dir
    fi

    touch "${NAUTA_VIRTUALENV}/.done"

    echo "Local python packages ready"
fi
ANSIBLE_PATH="${NAUTA_VIRTUALENV}/bin/ansible-playbook"
PATH=${NAUTA_VIRTUALENV}/bin:${PATH}

