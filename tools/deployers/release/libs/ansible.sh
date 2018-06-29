#!/usr/bin/env sh

set -e

DISTRPATH=${BINPATH}/${DETECTED_OS_NAME}/${DETECTED_OS_VERSION}

if [ ! -f "${DISTRPATH}/ansible-playbook" ]; then
    echo "Precompiled binary for system not found, creating virtualenv"
    . ${LIBDIR}/virtualenv.sh
else
    ANSIBLE_PATH="${DISTRPATH}/ansible-playbook"
fi

ansible() {
    ${ANSIBLE_PATH} $@
    return $?
}
