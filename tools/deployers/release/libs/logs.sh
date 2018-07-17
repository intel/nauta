#!/usr/bin/env sh

set -e

export LOGS_DIR="${CURDIR}/logs"

if [ ! -d "${LOGS_DIR}" ]; then
    mkdir "${LOGS_DIR}"
fi

export LOGS_FILE_NAME="$(date "+%Y%m%d-%H%M%s").log"
export LOGS_FILE="${LOGS_DIR}/${LOGS_FILE_NAME}"

export ANSIBLE_LOG_PATH="${LOGS_FILE}"
