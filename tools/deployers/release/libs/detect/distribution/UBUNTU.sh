#!/usr/bin/env sh

set -e

echo "Detected distribution: UBUNTU"

UBUNTU_CODENAME=$(lsb_release -c -s)
DETECTED_OS_VERSION=${UBUNTU_CODENAME}
