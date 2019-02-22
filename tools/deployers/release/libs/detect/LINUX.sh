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
