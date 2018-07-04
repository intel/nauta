#!/usr/bin/env sh

set -e

find_python() {
    for python in "$@"
    do
        if which ${python} > /dev/null 2>&1; then
          which ${python}
          return
        fi
    done
    >&2 echo "Unable to find $@ on your system"
    exit 1
}

PYTHON=$(find_python python3.5 python3.6)

echo "Python found: ${PYTHON}"

if ! ${PYTHON} -m pip > /dev/null 2>&1; then
    >&2 echo "Unable to find pip in ${PYTHON}"
    exit 1
fi

PIP="${PYTHON} -m pip"

export PYTHONUSERBASE=${CURDIR}/.venv/

if [ ! -f "${CURDIR}/.venv/.done" ]; then
    rm -rf "${CURDIR}/.venv"
    mkdir -p ~/.venv

    ${PIP} install -U -r ${BINDIR}/pip/requirements.txt -f ${BINDIR}/pip --no-index --user --isolated --ignore-installed --no-cache-dir

    touch "${CURDIR}/.venv/.done"

    echo "Virtualenv ready"
fi
ANSIBLE_PATH="${CURDIR}/.venv/bin/ansible-playbook"
PATH=${CURDIR}/.venv/bin:${PATH}
