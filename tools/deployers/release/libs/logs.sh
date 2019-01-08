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

export LOGS_DIR="${CURDIR}/logs"

if [ ! -d "${LOGS_DIR}" ]; then
    mkdir "${LOGS_DIR}"
fi

export LOGS_FILE_NAME="$(date "+%Y%m%d-%H%M%s").log"
export LOGS_FILE="${LOGS_DIR}/${LOGS_FILE_NAME}"

export ANSIBLE_LOG_PATH="${LOGS_FILE}"
