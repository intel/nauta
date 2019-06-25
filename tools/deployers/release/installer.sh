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

CURDIR=$(dirname $(realpath "$0"))
LIBDIR=${CURDIR}/libs
BINDIR=${CURDIR}/bin

. ${LIBDIR}/os-detect.sh
. ${LIBDIR}/locale.sh
. ${LIBDIR}/bins-detect.sh
. ${LIBDIR}/ansible.sh
. ${LIBDIR}/logs.sh

DATE=$(date '+%Y%m%d%H%M%S')

hide_output() {
    $@ > /dev/null 2&>1
    return $?
}

inventory() {
    if [ X"${ENV_INVENTORY}" = X"" ]; then
        echo "-c local -i localhost,"
    else
        if [ ! -f "${ENV_INVENTORY}" ]; then
            >&2 echo "Could not find or access inventory file: ${ENV_INVENTORY}"
            return 1
        fi
        echo "--inventory-file=$(realpath ${ENV_INVENTORY})"
    fi
}

config() {
    if [ X"${ENV_CONFIG}" = X"" ]; then
        echo ""
    else
        if [ ! -f "${ENV_CONFIG}" ]; then
            >&2 echo "Could not find or access config file: ${ENV_CONFIG}"
            return 1
        fi
        echo "-e @$(realpath ${ENV_CONFIG})"
    fi
}

kubeconfig() {
    if [ X"${NAUTA_KUBECONFIG}" != X"" ]; then
        echo "${NAUTA_KUBECONFIG}"
    elif [ -f "${CURDIR}/platform-admin.config" ]; then
        echo "${CURDIR}/platform-admin.config"
    else
        echo "${HOME}/.kube/config"
    fi
}

ansible_run() {
    export ANSIBLE_CONFIG=${CURDIR}/ansible.cfg
    inventory || return 1
    config || return 1
    mkdir -p ${CURDIR}/logs || exit 1
    export ANSIBLE_LOG_PATH="${CURDIR}/logs/log-${DATE}-${KIND:-install}.log"
    ansible $(inventory) $(config) \
    -e "upgrade=${UPGRADE:-False}" -e "kubectl=${KUBECTL}" -e "helm=${HELM}" \
    -e "kubeconfig=$(realpath $(kubeconfig))" -e "loader=${LOADER}" \
    -e "root=${CURDIR}" -e "default_ansible_python_interpreter=${PYTHON}" \
    $@
    return $?
}

platform_ansible_run() {
    export KIND=platform
    if [ X"${ENV_INVENTORY}" = X"" ]; then
        >&2 echo "Inventory file should be provided for platform installation"
        exit 1
    fi
    if [ X"${ENV_CONFIG}" = X"" ]; then
        >&2 echo "Config file should be provided for platform installation"
        exit 1
    fi
    set +e
    ansible_run ${CURDIR}/platform/nauta.yml
    ret_val=$?
    set -e
    show_error_message $ret_val
    return $ret_val
}

vanila_ansible_run() {
    export KIND=platform
    if [ X"${ENV_INVENTORY}" = X"" ]; then
        >&2 echo "Inventory file should be provided for vanila k8s installation"
        exit 1
    fi
    if [ X"${ENV_CONFIG}" = X"" ]; then
        >&2 echo "Config file should be provided for vanila k8s installation"
        exit 1
    fi
    set +e
    ansible_run ${CURDIR}/platform/vanila.yml
    ret_val=$?
    set -e
    show_error_message $ret_val
    return $ret_val
}

nauta_ansible_run() {
    export KIND=nauta
    set +e
    ansible_run ${CURDIR}/nauta/install.yml
    ret_val=$?
    set -e
    show_error_message $ret_val
    return $ret_val
}

nauta_fetch_ansible_run() {
    export KIND=nauta
    set +e
    ansible_run ${CURDIR}/nauta/fetch.yml
    ret_val=$?
    set -e
    show_error_message $ret_val
    return $ret_val
}

platform_verify_ansible_run() {
    export KIND=platform
    set +e
    ansible_run ${CURDIR}/platform/verification.yml
    ret_val=$?
    set -e
    show_error_message $ret_val
    return $ret_val
}


nauta_uninstall_run() {
    export KIND=uninstaller
    if [ X"${ENV_INVENTORY}" = X"" ]; then
        >&2 echo "Inventory file should be provided for platform installation"
        exit 1
    fi
    set +e
    ansible_run ${CURDIR}/nauta/uninstall.yml
    ret_val=$?
    set -i
    show_error_message $ret_val
    return $ret_val
}

get_diagnostic_data() {
    export ANSIBLE_CONFIG=${CURDIR}/ansible.cfg
    inventory || return 1
    config || return 1
    mkdir -p ${CURDIR}/logs || exit 1
    export ANSIBLE_LOG_PATH="${CURDIR}/logs/log-${DATE}-diagnose.log"
    ansible $(inventory) $(config) \
    -e "upgrade=${UPGRADE:-False}" -e "kubectl=${KUBECTL}" -e "helm=${HELM}" \
    -e "kubeconfig=$(realpath $(kubeconfig))" -e "loader=${LOADER}" \
    -e "root=${CURDIR}" -e "default_ansible_python_interpreter=${PYTHON}" \
    ${CURDIR}/diagnose/diagnose.yml
}

show_error_message() {
    if [ "$1" != "0" ]; then
        echo ""
        echo "\033[0;31mAn error during installation occurred. Please refer to installation documentation. In case of further problems please contact with technical support.\033[0m"
        echo ""
        get_diagnostic_data
    fi
}

COMMAND=$1

if [ X"${COMMAND}" = X"" ]; then
    >&2 echo "Command is not provided"
    exit 1
fi

case "${COMMAND}" in
  install) platform_ansible_run && nauta_ansible_run
     ;;
  platform-install) platform_ansible_run
     ;;
  vanila-install) vanila_ansible_run
     ;;
  nauta-install) nauta_ansible_run
     ;;
  nauta-upgrade) UPGRADE=True nauta_ansible_run
     ;;
  nauta-fetch) nauta_fetch_ansible_run
     ;;
  nauta-uninstall) nauta_uninstall_run
     ;;
  platform-verify) platform_verify_ansible_run
     ;;
  *) echo "Unknown command"
     ;;
esac
