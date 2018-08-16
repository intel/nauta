#!/usr/bin/env sh

set -e

echo "System detected: ${OS_TYPE}"

## Arch detection
OS_ARCH=$(uname -m)

if [ X"${OS_ARCH}" = X"x86_64" ]; then
    DETECTED_OS_ARCH="amd64"
else
    >&2 echo "Arch ${OS_ARCH} is not supported"
    exit 1
fi

echo "Detected arch: ${DETECTED_OS_ARCH}"

## Distribution detection
OS_NAME=$(awk -F= '/^NAME/{print $2}' /etc/os-release | tr -d '"')

if [ X"${OS_NAME}" = X"Ubuntu" ]; then
    DETECTED_OS_NAME="UBUNTU"
    . ${LIBDIR}/detect/distribution/UBUNTU.sh
elif [ X"${OS_NAME}" = X"Red Hat Enterprise Linux Server" ]; then
    DETECTED_OS_NAME="REDHAT"
    . ${LIBDIR}/detect/distribution/RHEL.sh
elif [ X"${OS_NAME}" = X"CentOS Linux" ]; then
    DETECTED_OS_NAME="CENTOS"
    . ${LIBDIR}/detect/distribution/CENTOS.sh
else
    >&2 echo "Distribution ${OS_NAME} is not supported"
    exit 1
fi
