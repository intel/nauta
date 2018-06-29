#!/usr/bin/env sh

set -e

if ! which python3.6 > /dev/null 2>&1; then
    >&2 echo "Unable to find python3.6 on your system"
    exit 1
fi
echo "Python3.6 present"

if ! which virtualenv > /dev/null 2>&1; then
    >&2 echo "Unable to find virtualenv on your system"
    exit 1
fi
echo "Virtualenv present"

if [ ! -f "${CURDIR}/.venv/.done" ]; then
    rm -rf "${CURDIR}/.venv"
fi

if [ ! -d "${CURDIR}/.venv" ]; then
    virtualenv -p python3.6 ${CURDIR}/.venv
fi

PIP_VENV="${CURDIR}/.venv/bin/pip"
PYTHON_VENV="${CURDIR}/.venv/bin/python"

if ! ${PIP_VENV} --version > /dev/null 2>&1; then
    2>&1 echo "Unable to find pip in your virtualenv"
    exhit 1
fi

${PIP_VENV} install --upgrade --upgrade-strategy only-if-needed ansible==2.5.0.0 docker==3.3.0 jmespath==0.9.3 netaddr==0.7.19

touch "${CURDIR}/.venv/.done"

echo "Virtualenv ready"
ANSIBLE_PATH="${CURDIR}/.venv/bin/ansible-playbook"
PATH=${CURDIR}/.venv/bin:${PATH}
