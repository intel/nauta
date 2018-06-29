#!/usr/bin/env sh

set -e

OS_TYPE=$(uname -s)

if [ X"${OS_TYPE}" = X"Linux" ]; then
    DETECTED_OS_TYPE="Linux"
    . ${LIBDIR}/detect/LINUX.sh
else
    >&2 echo "Your current system ${OS_TYPE} is not supported"
    exit 1
fi
