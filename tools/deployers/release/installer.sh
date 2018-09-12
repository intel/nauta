#!/usr/bin/env sh

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
    if [ X"${DLS_KUBECONFIG}" != X"" ]; then
        echo "${DLS_KUBECONFIG}"
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
    ansible_run ${CURDIR}/platform/dls.yml
    return $?
}

dls4e_ansible_run() {
    export KIND=dls4e
    ansible_run ${CURDIR}/dls4e/install.yml
    return $?
}

dls4e_fetch_ansible_run() {
    export KIND=dls4e
    ansible_run ${CURDIR}/dls4e/fetch.yml
    return $?
}

platform_verify_ansible_run() {
    export KIND=platform
    ansible_run ${CURDIR}/platform/verification.yml
    return $?
}

COMMAND=$1

if [ X"${COMMAND}" = X"" ]; then
    >&2 echo "Command is not provided"
    exit 1
fi

case "${COMMAND}" in
  install) platform_ansible_run && dls4e_ansible_run
     ;;
  platform-install) platform_ansible_run
     ;;
  dls4e-install) dls4e_ansible_run
     ;;
  dls4e-upgrade) UPGRADE=True dls4e_ansible_run
     ;;
  dls4e-fetch) dls4e_fetch_ansible_run
     ;;
  platform-verify) platform_verify_ansible_run
     ;;
  *) echo "Unknown command"
     ;;
esac
