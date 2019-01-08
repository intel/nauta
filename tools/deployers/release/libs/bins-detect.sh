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

BINPATH=${BINDIR}/${DETECTED_OS_TYPE}/${DETECTED_OS_ARCH}

HELM=${BINPATH}/helm
KUBECTL=${BINPATH}/kubectl
LOADER=${BINPATH}/loader

if [ ! -f "${HELM}" ]; then
    >&2 echo "Unable to find helm binary in ${HELM}"
    exit 1
fi
chmod +x ${HELM}
${HELM} version -c > /dev/null

if [ ! -f "${KUBECTL}" ]; then
    >&2 echo "Unable to find kubectl binary in ${KUBECTL}"
    exit 1
fi
chmod +x ${KUBECTL}
${KUBECTL} version --client > /dev/null

if [ ! -f "${LOADER}" ]; then
    >&2 echo "Unable to find loeader binary in ${LOADER}"
    exit 1
fi
