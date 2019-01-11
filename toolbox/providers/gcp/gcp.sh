#!/bin/bash -e
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

print_log () {
    NOCOLOR='\033[0m' # no color
    COLOR='\033[0m' # no color
    if [ "$1" = "ERROR" ] ; then
        COLOR='\033[0;31m' #red
    fi
    if [ "$1" = "INFO" ] ; then
        COLOR='\033[0;32m' #green
    fi
    if [ "$1" = "WARNING" ] ; then
        COLOR='\033[0;33m' #yellow
    fi
    shift
    echo -e "${COLOR}[`hostname`][$0][`date '+%Y-%m-%d %H:%M:%S'`] $@${NOCOLOR}"
}

check_file_presence() {
    if [ -f $1 ]; then
        print_log "INFO" "File $1 exists"
    else
        print_log "ERROR" "File $1 does not exists"
        exit 1
    fi
}

function validate_prerequisities {
    print_log  "INFO" "Validate prerequisities"
}

function validate_arguments {
    print_log  "WARNING" "Validate arguments"
    check_file_presence "${GcpConfig}"
    check_file_presence "${SCRIPTDIR}/gcp-service-account.yml"
    if [ "${InstallFile}" != "" ]; then
        check_file_presence "${InstallFile}"
    fi
}

function set_defaults {
    print_log  "WARNING" "Set defaults"
#    if [ "${Operation}" = "" ] ; then Operation="create" ; fi
    if [ "${GcpConfig}" = "" ] ; then GcpConfig="`pwd`/gcp-config.yml" ; fi
    if [ "${K8sCluster}" = "" ] ; then K8sCluster="nauta" ; fi
    if [ "${ExternalPublicKey}" = "" ] ; then ExternalPublicKey="~/.ssh/id_rsa.pub" ; fi
    if [ "${ExternalKey}" = "" ] ; then ExternalKey="~/.ssh/id_rsa" ; fi
    if [ "${K8sOutputFile}" = "" ] ; then K8sOutputFile="`pwd`/${K8sCluster}.info" ; fi
    if [ "${NetworkSettings}" = "" ] ; then NetworkSettings="config.yml" ; fi

    if [ "${InstallFile}" != "" ]; then
        INSTALL_FILE_NAME=$(basename -- "${InstallFile}")
    fi
}

show_parameters() {
    print_log  "WARNING" "Build parameters:"
    echo -e "\t\tOperation=${Operation}"
    echo -e "\t\tK8sCluster=${K8sCluster}"
    echo -e "\t\tGcpConfig=${GcpConfig}"
    echo -e "\t\tExternalPublicKey=${ExternalPublicKey}"
    echo -e "\t\tExternalKey=${ExternalKey}"
    echo -e "\t\tK8sOutputFile=${K8sOutputFile}"
    echo -e "\t\tNetworkSettings=${NetworkSettings}"
    echo -e ""
    echo -e "\t\tInstallFile=${InstallFile}"

    echo -e ""
    echo -e "\t\tS3Url=${S3Url}"
    echo -e "\t\tS3AccessKey=${S3AccessKey}"

    echo -e ""
    echo -e "\t\tSCRIPTDIR=${SCRIPTDIR}"
}

create_cluster() {
    print_log  "WARNING" "\
    cd ../../.. && \
        ENV_S3_URL="${S3Url}" \
        ENV_SECRET_KEY="${S3SecretKey}" \
        ENV_ACCESS_KEY="${S3AccessKey}" \
        make gcp-create \
        ENV_NAME=${K8sCluster} \
        ENV_NETWORK_SETTINGS=${NetworkSettings} \
        ENV_CLUSTER_CONFIG_FILE=${GcpConfig} \
        ENV_EXTERNAL_PUBLIC_KEY=${ExternalPublicKey} \
        ENV_EXTERNAL_KEY=${ExternalKey} \
        K8S_OUTPUT_FILE=${K8sOutputFile} \
    "

    cd ../../.. && \
        ENV_S3_URL="${S3Url}" \
        ENV_SECRET_KEY="${S3SecretKey}" \
        ENV_ACCESS_KEY="${S3AccessKey}" \
        make gcp-create \
        ENV_NAME=${K8sCluster} \
        ENV_NETWORK_SETTINGS=${NetworkSettings} \
        ENV_CLUSTER_CONFIG_FILE=${GcpConfig} \
        ENV_EXTERNAL_PUBLIC_KEY=${ExternalPublicKey} \
        ENV_EXTERNAL_KEY=${ExternalKey} \
        K8S_OUTPUT_FILE=${K8sOutputFile}
}


destroy_cluster() {
   print_log  "WARNING" "\
    cd ../../.. && \
        ENV_S3_URL="${S3Url}" \
        ENV_SECRET_KEY="${S3SecretKey}" \
        ENV_ACCESS_KEY="${S3AccessKey}" \
        make gcp-destroy \
        ENV_NAME=${K8sCluster} \
        ENV_NETWORK_SETTINGS=${NetworkSettings} \
        ENV_CLUSTER_CONFIG_FILE=${GcpConfig} \
        ENV_EXTERNAL_PUBLIC_KEY=${ExternalPublicKey} \
        ENV_EXTERNAL_KEY=${ExternalKey} \
        K8S_OUTPUT_FILE=${K8sOutputFile} \
    "

    cd ../../.. && \
        ENV_S3_URL="${S3Url}" \
        ENV_SECRET_KEY="${S3SecretKey}" \
        ENV_ACCESS_KEY="${S3AccessKey}" \
        make gcp-destroy \
        ENV_NAME=${K8sCluster} \
        ENV_NETWORK_SETTINGS=${NetworkSettings} \
        ENV_CLUSTER_CONFIG_FILE=${GcpConfig} \
        ENV_EXTERNAL_PUBLIC_KEY=${ExternalPublicKey} \
        ENV_EXTERNAL_KEY=${ExternalKey} \
        K8S_OUTPUT_FILE=${K8sOutputFile}
}

set_connectivity_params() {
    print_log  "WARNING" "Set connectivity parameters to access gateway node"
    GATEWAY_IP=`cat ${K8sOutputFile} | grep "gateway_ip" | awk -F '"' '{print $2}'`
    GATEWAY_USER=`cat ${GcpConfig} | grep "external_username" | awk -F '"' '{print $2}'`
    PROXY_TO_GATEWAY=`cat ${SCRIPTDIR}/../../${NetworkSettings} | grep "ssh_args_for_cmd_line" | awk -F '"' '{print $2}'`
}

show_connectivity_parameters() {
    print_log  "WARNING" "Conectivity parameters:"
    echo -e "\t\tGATEWAY_IP=${GATEWAY_IP}"
    echo -e "\t\tGATEWAY_USER=${GATEWAY_USER}"
    echo -e "\t\tPROXY_TO_GATEWAY=${PROXY_TO_GATEWAY}"
}

transfer_install_file() {
    print_log  "WARNING" "Transfer install file ${InstallFile} to gateway node ${GATEWAY_IP}"

    print_log  "WARNING" "shasum -a 256 ${InstallFile} > ${WORKSPACEDIR}/${INSTALL_FILE_NAME}.sha256"
    shasum -a 256 -p ${InstallFile} > ${WORKSPACEDIR}/${INSTALL_FILE_NAME}.sha256
    rm -rf ${WORKSPACEDIR}/${INSTALL_FILE_NAME}.sha256.remote

    if [ "${PROXY_TO_GATEWAY}" = "" ]; then
        set +e
        print_log  "WARNING" scp -i "${ExternalKey}" ${GATEWAY_USER}@${GATEWAY_IP}:${INSTALL_FILE_NAME}.sha256 ${WORKSPACEDIR}/${INSTALL_FILE_NAME}.sha256.remote
        scp -i "${ExternalKey}" ${GATEWAY_USER}@${GATEWAY_IP}:${INSTALL_FILE_NAME}.sha256 ${WORKSPACEDIR}/${INSTALL_FILE_NAME}.sha256.remote
        set -e
    else
        set +e
        print_log  "WARNING" scp -i "${ExternalKey}" -o ProxyCommand="${PROXY_TO_GATEWAY}" ${GATEWAY_USER}@${GATEWAY_IP}:${INSTALL_FILE_NAME}.sha256 ${WORKSPACEDIR}/${INSTALL_FILE_NAME}.sha256.remote
        scp -i "${ExternalKey}" -o ProxyCommand="${PROXY_TO_GATEWAY}" ${GATEWAY_USER}@${GATEWAY_IP}:${INSTALL_FILE_NAME}.sha256 ${WORKSPACEDIR}/${INSTALL_FILE_NAME}.sha256.remote
        set -e
    fi

    set +e
    print_log  "WARNING" diff ${WORKSPACEDIR}/${INSTALL_FILE_NAME}.sha256 ${WORKSPACEDIR}/${INSTALL_FILE_NAME}.sha256.remote
    diff ${WORKSPACEDIR}/${INSTALL_FILE_NAME}.sha256 ${WORKSPACEDIR}/${INSTALL_FILE_NAME}.sha256.remote
    ret_val=$?
    set -e

    print_log  "WARNING" "sha256 comparision result:${ret_val}"

    if [ "${ret_val}" != "0" ]; then
        if [ "${PROXY_TO_GATEWAY}" = "" ]; then
            print_log  "WARNING" scp -i "${ExternalKey}" "${InstallFile}" ${GATEWAY_USER}@${GATEWAY_IP}:${INSTALL_FILE_NAME}
            scp -i "${ExternalKey}" "${InstallFile}" ${GATEWAY_USER}@${GATEWAY_IP}:${INSTALL_FILE_NAME}

            print_log  "WARNING" scp -i "${ExternalKey}" -o ProxyCommand="${PROXY_TO_GATEWAY}" ${INSTALL_FILE_NAME}.sha256.remote ${GATEWAY_USER}@${GATEWAY_IP}:${INSTALL_FILE_NAME}.sha256
            scp -i "${ExternalKey}" -o ProxyCommand="${PROXY_TO_GATEWAY}" ${WORKSPACEDIR}/${INSTALL_FILE_NAME}.sha256 ${GATEWAY_USER}@${GATEWAY_IP}:${INSTALL_FILE_NAME}.sha256
        else
            print_log  "WARNING" scp -i "${ExternalKey}" -o ProxyCommand="${PROXY_TO_GATEWAY}" "${InstallFile}" ${GATEWAY_USER}@${GATEWAY_IP}:${INSTALL_FILE_NAME}
            scp -i "${ExternalKey}" -o ProxyCommand="${PROXY_TO_GATEWAY}" "${InstallFile}" ${GATEWAY_USER}@${GATEWAY_IP}:${INSTALL_FILE_NAME}

            print_log  "WARNING" scp -i "${ExternalKey}" -o ProxyCommand="${PROXY_TO_GATEWAY}" ${INSTALL_FILE_NAME}.sha256.remote ${GATEWAY_USER}@${GATEWAY_IP}:${INSTALL_FILE_NAME}.sha256
            scp -i "${ExternalKey}" -o ProxyCommand="${PROXY_TO_GATEWAY}" ${WORKSPACEDIR}/${INSTALL_FILE_NAME}.sha256 ${GATEWAY_USER}@${GATEWAY_IP}:${INSTALL_FILE_NAME}.sha256
        fi
    fi
}

install_platform() {
    print_log  "WARNING" "Install platform from file ${InstallFile} on gateway"

    if [ "${PROXY_TO_GATEWAY}" = "" ]; then
        print_log "DEBUG" ssh -i "${ExternalKey}" ${GATEWAY_USER}@${GATEWAY_IP} rm -rf install
        ssh -i "${ExternalKey}" ${GATEWAY_USER}@${GATEWAY_IP} rm -rf install

        print_log "DEBUG" ssh -i "${ExternalKey}" ${GATEWAY_USER}@${GATEWAY_IP} mkdir -p install
        ssh -i "${ExternalKey}" ${GATEWAY_USER}@${GATEWAY_IP} mkdir -p install

        print_log "DEBUG" ssh -i "${ExternalKey}" ${GATEWAY_USER}@${GATEWAY_IP} tar xvf ${INSTALL_FILE_NAME} -C install
        ssh -i "${ExternalKey}" ${GATEWAY_USER}@${GATEWAY_IP} tar xvf ${INSTALL_FILE_NAME} -C install

        print_log "DEBUG" ssh -i "${ExternalKey}" ${GATEWAY_USER}@${GATEWAY_IP} sudo apt-get update
        ssh -i "${ExternalKey}" ${GATEWAY_USER}@${GATEWAY_IP} sudo apt-get update

        print_log "DEBUG" ssh -i "${ExternalKey}" ${GATEWAY_USER}@${GATEWAY_IP} sudo apt-get install python python-pip python-dev virtualenv python3-pip python3-dev python3-venv gcc openssl libssl-dev libffi-dev -y
        ssh -i "${ExternalKey}" ${GATEWAY_USER}@${GATEWAY_IP} sudo apt-get install python python-pip python-dev virtualenv python3-pip python3-dev python3-venv gcc openssl libssl-dev libffi-dev -y

        print_log "DEBUG" ssh -i "${ExternalKey}" ${GATEWAY_USER}@${GATEWAY_IP} chmod +x install/installer.sh
        ssh -i "${ExternalKey}" ${GATEWAY_USER}@${GATEWAY_IP} chmod +x install/installer.sh

        print_log "DEBUG" ssh -i "${ExternalKey}" ${GATEWAY_USER}@${GATEWAY_IP} LC_ALL=en_US.UTF-8 LANG=en_US.UTF-8 ENV_CONFIG=/home/dls4e/config.yml install/installer.sh dls4e-install
        ssh -i "${ExternalKey}" ${GATEWAY_USER}@${GATEWAY_IP} LC_ALL=en_US.UTF-8 LANG=en_US.UTF-8 ENV_CONFIG=/home/dls4e/config.yml install/installer.sh dls4e-install
    else
        print_log "DEBUG" ssh -i "${ExternalKey}" -o ProxyCommand="${PROXY_TO_GATEWAY}" ${GATEWAY_USER}@${GATEWAY_IP} mkdir -p install
        ssh -i "${ExternalKey}" -o ProxyCommand="${PROXY_TO_GATEWAY}" ${GATEWAY_USER}@${GATEWAY_IP} mkdir -p install

        print_log "DEBUG" ssh -i "${ExternalKey}" -o ProxyCommand="${PROXY_TO_GATEWAY}" ${GATEWAY_USER}@${GATEWAY_IP} tar xvf ${INSTALL_FILE_NAME} -C install
        ssh -i "${ExternalKey}" -o ProxyCommand="${PROXY_TO_GATEWAY}" ${GATEWAY_USER}@${GATEWAY_IP} tar xvf ${INSTALL_FILE_NAME} -C install

        print_log "DEBUG" ssh -i "${ExternalKey}" -o ProxyCommand="${PROXY_TO_GATEWAY}" ${GATEWAY_USER}@${GATEWAY_IP} sudo apt-get update
        ssh -i "${ExternalKey}" -o ProxyCommand="${PROXY_TO_GATEWAY}" ${GATEWAY_USER}@${GATEWAY_IP} sudo apt-get update

        print_log "DEBUG" ssh -i "${ExternalKey}" -o ProxyCommand="${PROXY_TO_GATEWAY}" ${GATEWAY_USER}@${GATEWAY_IP} sudo apt-get install python python-pip python-dev virtualenv python3-pip python3-dev python3-venv gcc openssl libssl-dev libffi-dev -y
        ssh -i "${ExternalKey}" -o ProxyCommand="${PROXY_TO_GATEWAY}" ${GATEWAY_USER}@${GATEWAY_IP} sudo apt-get install python python-pip python-dev virtualenv python3-pip python3-dev python3-venv gcc openssl libssl-dev libffi-dev -y

        print_log "DEBUG" ssh -i "${ExternalKey}" -o ProxyCommand="${PROXY_TO_GATEWAY}" ${GATEWAY_USER}@${GATEWAY_IP} chmod +x install/installer.sh
        ssh -i "${ExternalKey}" -o ProxyCommand="${PROXY_TO_GATEWAY}" ${GATEWAY_USER}@${GATEWAY_IP} chmod +x install/installer.sh

        print_log "DEBUG" ssh -i "${ExternalKey}" -o ProxyCommand="${PROXY_TO_GATEWAY}" ${GATEWAY_USER}@${GATEWAY_IP} LC_ALL=en_US.UTF-8 LANG=en_US.UTF-8 ENV_CONFIG=/home/dls4e/config.yml install/installer.sh dls4e-install
        ssh -i "${ExternalKey}" -o ProxyCommand="${PROXY_TO_GATEWAY}" ${GATEWAY_USER}@${GATEWAY_IP} LC_ALL=en_US.UTF-8 LANG=en_US.UTF-8 ENV_CONFIG=/home/dls4e/config.yml install/installer.sh dls4e-install
    fi
}

clean() {
   print_log  "WARNING" "\
    cd ../../.. && \
        make gcp-clean \
    "

    cd ../../.. && \
        make gcp-clean
}

show_help() {
   print_log  "WARNING" "Help"
   echo -e `cat ${SCRIPTDIR}/gcp.sh.help | sed 's/\[RED\]/\\\033\[0;31m/g' | sed 's/\[GREEN\]/\\\033\[0;32m/g' | sed 's/\[YELLOW\]/\\\033\[0;33m/g' | sed 's/\[NOCOLOR\]/\\\033\[0m/g' | sed 's/\[BR\]/\\\n/g'`
}

SCRIPTDIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
WORKSPACEDIR="${SCRIPTDIR}/../../../.workspace"

#validate_prerequisities

LONG_OPTIONS=""
LONG_OPTIONS+="operation:,"
LONG_OPTIONS+="k8s-cluster:,"
LONG_OPTIONS+="gcp-config:,"
LONG_OPTIONS+="external-public-key:,"
LONG_OPTIONS+="external-key:,"
LONG_OPTIONS+="s3-url:,"
LONG_OPTIONS+="s3-secret-key:,"
LONG_OPTIONS+="s3-access-key:,"
LONG_OPTIONS+="install-file:,"
LONG_OPTIONS+="network-settings:,"
LONG_OPTIONS+="help"

SHORT_OPTIONS="c:"
OPTS=`getopt -l ${LONG_OPTIONS} -o ${SHORT_OPTIONS} -n 'gcp.sh' -- "$@"`
eval set -- "$OPTS"
while true; do
   case "$1" in
        --help) show_help; exit 1 ;;
        --operation) Operation="$2"; shift 2 ;;
        --k8s-cluster) K8sCluster="$2"; shift 2 ;;
        --gcp-config) GcpConfig="$2"; shift 2 ;;
        --external-public-key) ExternalPublicKey="$2"; shift 2 ;;
        --external-key) ExternalKey="$2"; shift 2 ;;
        --s3-url) S3Url="$2"; shift 2 ;;
        --s3-secret-key) S3SecretKey="$2"; shift 2 ;;
        --s3-access-key) S3AccessKey="$2"; shift 2 ;;
        --install-file) InstallFile="$2"; shift 2 ;;
        --network-settings) NetworkSettings="$2"; shift 2 ;;
        --) break;;
        *) echo "Internal error! |$1|$2|" ; exit 1 ;;
   esac
done

set_defaults
show_parameters
validate_arguments

if [ "${Operation}" = "clean" ]; then
    clean
fi

if [ "${Operation}" = "create" ]; then
    create_cluster
fi

if [ "${InstallFile}" != "" ]; then
    set_connectivity_params
    show_connectivity_parameters
    transfer_install_file
    install_platform
fi

if [ "${Operation}" = "destroy" ]; then
    destroy_cluster
fi

print_log "WARNING" "Script finish"
