#!/usr/bin/env sh

set -e

echo "Detected distribution: CENTOS"
. /etc/os-release
DETECTED_OS_VERSION=${VERSION_ID}
