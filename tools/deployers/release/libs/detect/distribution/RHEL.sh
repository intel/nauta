#!/usr/bin/env sh

set -e

echo "Detected distribution: REDHAT"
. /etc/os-release
DETECTED_OS_VERSION=${VERSION_ID}
PYTHON=/usr/bin/python
