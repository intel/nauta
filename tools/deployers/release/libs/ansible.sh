#!/usr/bin/env sh

set -e

DISTRPATH=${BINPATH}/${DETECTED_OS_NAME}/${DETECTED_OS_VERSION}

if [ ! -f "${DISTRPATH}/ansible-playbook" ]; then
    echo "Precompiled ansible binary for system not found in ${DISTRPATH}/ansible-playbook, using system python"
    . ${LIBDIR}/virtualenv.sh
else
    ANSIBLE_PATH="${DISTRPATH}/ansible-playbook"
fi

ansible() {
    ${ANSIBLE_PATH} $@
    return $?
}
