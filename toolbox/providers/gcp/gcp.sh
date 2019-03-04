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
    if [ "$1" = "DEBUG" ] ; then
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
        print_log "WARNING" "File $1 does not exists"
        exit 1
    fi
}

function validate_prerequisities {
    print_log "INFO" "Validate prerequisities"
}

function validate_arguments {
    print_log "DEBUG" "Validate arguments"
    check_file_presence "${GcpConfig}"
    check_file_presence "${NetworkSettings}"
    check_file_presence "${ServiceAccountConfigFile}"

    if [ "${InstallFile}" != "" ]; then
        check_file_presence "${InstallFile}"
    fi

    if [ "${ClientFile}" != "" ]; then
        check_file_presence "${ClientFile}"
    fi

    if [ "${PlatformConfigFile}" != "" ]; then
        check_file_presence "${PlatformConfigFile}"
    fi

    if [ "${InstallFile}" != "" ] && [ "${CompilePlatformOnCloud}" = "true" ] ; then
        print_log "WARNING" "Both: compile platform on gateway and local install file are set. Compilation on gateway is overriden strategy."
        InstallFile=""
    fi
}

function set_defaults {
    print_log "DEBUG" "Set defaults"
#    if [ "${Operation}" = "" ] ; then Operation="create" ; fi
    if [ "${GcpConfig}" = "" ] ; then GcpConfig="`pwd`/gcp-config.yml" ; fi
    if [ "${K8sCluster}" = "" ] ; then K8sCluster="nauta" ; fi
    if [ "${ExternalPublicKey}" = "" ] ; then ExternalPublicKey="~/.ssh/id_rsa.pub" ; fi
    if [ "${ExternalKey}" = "" ] ; then ExternalKey="~/.ssh/id_rsa" ; fi
    if [ "${K8sOutputFile}" = "" ] ; then K8sOutputFile="`pwd`/${K8sCluster}.info" ; fi
    if [ "${NetworkSettings}" = "" ] ; then NetworkSettings="`pwd`/../../config.yml" ; fi

    if [ "${CompilePlatformOnCloud}" = "" ] ; then CompilePlatformOnCloud="false" ; fi

    if [ "${InstallFile}" != "" ]; then
        INSTALL_FILE_NAME=$(basename -- "${InstallFile}")
    fi

    if [ "${ClientFile}" != "" ]; then
        CLIENT_FILE_NAME=$(basename -- "${ClientFile}")
    fi
    if [ "${ServiceAccountConfigFile}" = "" ] ; then ServiceAccountConfigFile="`pwd`/gcp-service-account.json" ; fi

    if [ "${PlatformConfigFile}" != "" ]; then
        PLATFORM_CONFIG_FILE_NAME=$(basename -- "${PlatformConfigFile}")
    fi

    CurrentBranch=`git status | grep "On branch" | awk '{print $3}'`
    if [ "${CurrentBranch}" = "" ] ; then
        CurrentBranch="develop"
    fi
}

show_parameters() {
    print_log "DEBUG" "Build parameters:"
    echo -e "\t\tOperation=${Operation}"
    echo -e "\t\tK8sCluster=${K8sCluster}"
    echo -e "\t\tGcpConfig=${GcpConfig}"
    echo -e "\t\tExternalPublicKey=${ExternalPublicKey}"
    echo -e "\t\tExternalKey=${ExternalKey}"
    echo -e "\t\tK8sOutputFile=${K8sOutputFile}"
    echo -e "\t\tNetworkSettings=${NetworkSettings}"
    echo -e ""
    echo -e "\t\tServiceAccountConfigFile=${ServiceAccountConfigFile}"
    echo -e "\t\tPlatformConfigFile=${PlatformConfigFile}"
    echo -e ""
    echo -e "\t\tInstallFile=${InstallFile}"
    echo -e "\t\tClientFile=${ClientFile}"
    echo -e "\t\tCompilePlatformOnCloud=${CompilePlatformOnCloud}"
    echo -e "\t\tCurrentBranch=${CurrentBranch}"

    echo -e ""
    echo -e "\t\tS3Url=${S3Url}"
    echo -e "\t\tS3AccessKey=${S3AccessKey}"

    echo -e ""
    echo -e "\t\tSCRIPTDIR=${SCRIPTDIR}"
}

create_cluster() {
    print_log "DEBUG" "\
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
        ENV_SERVICE_ACCOUNT_CONFIG=${ServiceAccountConfigFile} \
        ENV_PLATFORM_CONFIG=${PlatformConfigFile} \
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
        ENV_SERVICE_ACCOUNT_CONFIG=${ServiceAccountConfigFile} \
        ENV_PLATFORM_CONFIG=${PlatformConfigFile} \
        K8S_OUTPUT_FILE=${K8sOutputFile}
}


destroy_cluster() {
   print_log "DEBUG" "\
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
        ENV_SERVICE_ACCOUNT_CONFIG=${ServiceAccountConfigFile} \
        ENV_PLATFORM_CONFIG=${PlatformConfigFile} \
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
        ENV_SERVICE_ACCOUNT_CONFIG=${ServiceAccountConfigFile} \
        ENV_PLATFORM_CONFIG=${PlatformConfigFile} \
        K8S_OUTPUT_FILE=${K8sOutputFile}
}

set_connectivity_params() {
    print_log "DEBUG" "Set connectivity parameters to access gateway node"
    GATEWAY_IP=`cat ${K8sOutputFile} | grep "gateway_ip" | awk -F '"' '{print $2}'`
    GATEWAY_USER=`cat ${GcpConfig} | grep "external_username" | awk -F '"' '{print $2}'`
    PROXY_TO_GATEWAY=`cat ${NetworkSettings} | grep "ssh_args_for_cmd_line" | awk -F '"' '{print $2}'`
}

show_connectivity_parameters() {
    print_log "DEBUG" "Conectivity parameters:"
    echo -e "\t\tGATEWAY_IP=${GATEWAY_IP}"
    echo -e "\t\tGATEWAY_USER=${GATEWAY_USER}"
    echo -e "\t\tPROXY_TO_GATEWAY=${PROXY_TO_GATEWAY}"
}

run_scp_command() {
    if [ "${PROXY_TO_GATEWAY}" = "" ]; then
        print_log "DEBUG" scp -i "${ExternalKey}" $1 $2
        scp -r -i "${ExternalKey}"  $1 $2
    else
        print_log "DEBUG" scp -i "${ExternalKey}" -o ProxyCommand="${PROXY_TO_GATEWAY}" $1 $2
        scp -r -i "${ExternalKey}" -o ProxyCommand="${PROXY_TO_GATEWAY}" $1 $2
    fi
}

run_ssh_command() {
    if [ "${PROXY_TO_GATEWAY}" = "" ]; then
        print_log "DEBUG" ssh -i "${ExternalKey}" "$1"
        ssh -i "${ExternalKey}" "$1"
    else
        print_log "DEBUG" ssh -i "${ExternalKey}" -o ProxyCommand="${PROXY_TO_GATEWAY}" "$1"
        ssh -i "${ExternalKey}" -o ProxyCommand="${PROXY_TO_GATEWAY}" "$1"
    fi
}

transfer_install_file() {
    print_log "DEBUG" "Transfer install file ${InstallFile} to gateway node ${GATEWAY_IP}"

    print_log "DEBUG" "shasum -a 256 ${InstallFile} > ${WORKSPACEDIR}/${INSTALL_FILE_NAME}.sha256"
    shasum -a 256 -p ${InstallFile} > ${WORKSPACEDIR}/${INSTALL_FILE_NAME}.sha256
    rm -rf ${WORKSPACEDIR}/${INSTALL_FILE_NAME}.sha256.remote

    set +e
    run_scp_command ${GATEWAY_USER}@${GATEWAY_IP}:artifacts/${INSTALL_FILE_NAME}.sha256 ${WORKSPACEDIR}/${INSTALL_FILE_NAME}.sha256.remote
    set -e

    set +e
    print_log "DEBUG" diff ${WORKSPACEDIR}/${INSTALL_FILE_NAME}.sha256 ${WORKSPACEDIR}/${INSTALL_FILE_NAME}.sha256.remote
    diff ${WORKSPACEDIR}/${INSTALL_FILE_NAME}.sha256 ${WORKSPACEDIR}/${INSTALL_FILE_NAME}.sha256.remote
    ret_val=$?
    set -e

    print_log "DEBUG" "sha256 comparision result:${ret_val}"


    if [ "${PROXY_TO_GATEWAY}" = "" ]; then
        print_log "DEBUG" ssh -i "${ExternalKey}" ${GATEWAY_USER}@${GATEWAY_IP} "mkdir -p artifacts"
        ssh -i "${ExternalKey}" ${GATEWAY_USER}@${GATEWAY_IP} "mkdir -p artifacts"
    else
        print_log "DEBUG" ssh -i "${ExternalKey}" -o ProxyCommand="${PROXY_TO_GATEWAY}" ${GATEWAY_USER}@${GATEWAY_IP} "mkdir -p artifacts"
        ssh -i "${ExternalKey}" -o ProxyCommand="${PROXY_TO_GATEWAY}" ${GATEWAY_USER}@${GATEWAY_IP} "mkdir -p artifacts"
    fi

    if [ "${ret_val}" != "0" ]; then
        run_scp_command "${InstallFile}" ${GATEWAY_USER}@${GATEWAY_IP}:artifacts/${INSTALL_FILE_NAME}
        run_scp_command ${WORKSPACEDIR}/${INSTALL_FILE_NAME}.sha256 ${GATEWAY_USER}@${GATEWAY_IP}:artifacts/${INSTALL_FILE_NAME}.sha256
    fi

    if [ "${ClientFile}" != "" ]; then
        run_scp_command "${ClientFile}" ${GATEWAY_USER}@${GATEWAY_IP}:artifacts/${CLIENT_FILE_NAME}
        if [ "${PROXY_TO_GATEWAY}" = "" ]; then
            print_log "DEBUG" ssh -i "${ExternalKey}" ${GATEWAY_USER}@${GATEWAY_IP} "ln -fs artifacts/${CLIENT_FILE_NAME} artifacts/nctl.installer"
            ssh -i "${ExternalKey}" ${GATEWAY_USER}@${GATEWAY_IP} "ln -fs artifacts/${CLIENT_FILE_NAME} artifacts/nctl.installer"
        else
            print_log "DEBUG" ssh -i "${ExternalKey}" -o ProxyCommand="${PROXY_TO_GATEWAY}" ${GATEWAY_USER}@${GATEWAY_IP} "ln -fs artifacts/${CLIENT_FILE_NAME} artifacts/nctl.installer"
            ssh -i "${ExternalKey}" -o ProxyCommand="${PROXY_TO_GATEWAY}" ${GATEWAY_USER}@${GATEWAY_IP} "ln -fs artifacts/${CLIENT_FILE_NAME} artifacts/nctl.installer"
        fi
    fi
}

transfer_scripts() {
    print_log "DEBUG" "Transfer install scripts"
    run_scp_command ${SCRIPTDIR}/files/remote_scripts ${GATEWAY_USER}@${GATEWAY_IP}:
}

transfer_config_files() {
    print_log "DEBUG" "Transfer config files"
    if [ "${PlatformConfigFile}" != "" ]; then
        run_scp_command ${PlatformConfigFile} ${GATEWAY_USER}@${GATEWAY_IP}:platform-config.yml
    fi
}

install_platform_prerequisities() {
    print_log "DEBUG" "Install platform prerequisities on gateway"
    if [ "${PROXY_TO_GATEWAY}" = "" ]; then
        print_log "DEBUG" ssh -i "${ExternalKey}" ${GATEWAY_USER}@${GATEWAY_IP} "./remote_scripts/install_prerequisities.sh"
        ssh -i "${ExternalKey}" ${GATEWAY_USER}@${GATEWAY_IP} "./remote_scripts/install_prerequisities.sh"
    else
        print_log "DEBUG" ssh -i "${ExternalKey}" -o ProxyCommand="${PROXY_TO_GATEWAY}" ${GATEWAY_USER}@${GATEWAY_IP} "./remote_scripts/install_prerequisities.sh"
        ssh -i "${ExternalKey}" -o ProxyCommand="${PROXY_TO_GATEWAY}" ${GATEWAY_USER}@${GATEWAY_IP} "./remote_scripts/install_prerequisities.sh"
    fi
}

install_platform() {
    print_log "DEBUG" "Install platform from file ${InstallFile} on gateway"

    print_log "DEBUG" "Install platform prerequisities on gateway"
    if [ "${PROXY_TO_GATEWAY}" = "" ]; then
        print_log "DEBUG" ssh -i "${ExternalKey}" ${GATEWAY_USER}@${GATEWAY_IP} "./remote_scripts/install_platform.sh ${INSTALL_FILE_NAME}"
        ssh -i "${ExternalKey}" ${GATEWAY_USER}@${GATEWAY_IP} "./remote_scripts/install_platform.sh ${INSTALL_FILE_NAME}"
    else
        print_log "DEBUG" ssh -i "${ExternalKey}" -o ProxyCommand="${PROXY_TO_GATEWAY}" ${GATEWAY_USER}@${GATEWAY_IP} "./remote_scripts/install_platform.sh ${INSTALL_FILE_NAME}"
        ssh -i "${ExternalKey}" -o ProxyCommand="${PROXY_TO_GATEWAY}" ${GATEWAY_USER}@${GATEWAY_IP} "./remote_scripts/install_platform.sh ${INSTALL_FILE_NAME}"
    fi
}

install_compiler_prerequisities() {
    print_log "DEBUG" "Install compile prerequisities on gateway"
    if [ "${PROXY_TO_GATEWAY}" = "" ]; then
        print_log "DEBUG" ssh -i "${ExternalKey}" ${GATEWAY_USER}@${GATEWAY_IP} "./remote_scripts/compile_prerequisities.sh"
        ssh -i "${ExternalKey}" ${GATEWAY_USER}@${GATEWAY_IP} "./remote_scripts/compile_prerequisities.sh"
    else
        print_log "DEBUG" ssh -i "${ExternalKey}" -o ProxyCommand="${PROXY_TO_GATEWAY}" ${GATEWAY_USER}@${GATEWAY_IP} "./remote_scripts/compile_prerequisities.sh"
        ssh -i "${ExternalKey}" -o ProxyCommand="${PROXY_TO_GATEWAY}" ${GATEWAY_USER}@${GATEWAY_IP} "./remote_scripts/compile_prerequisities.sh"
    fi
}

function retrieve_repo {
    PROJECT_NAME=$1
    BRANCH_NAME=$2

    if [ -d "$PROJECT_NAME" ]; then
      cd $PROJECT_NAME
      git fetch --all

      set +e
      git reset --hard origin/$BRANCH_NAME
      if [ $? -ne 0 ]; then
        print_log "ERROR" "Error in hard reset. Probably sha sum or tag name is added instead of branch name. Trying to reset again."
        git reset --hard $BRANCH_NAME
      fi
      set -e

      git checkout $BRANCH_NAME

      set +e
      git reset --hard origin/$BRANCH_NAME
      if [ $? -ne 0 ]; then
        print_log "ERROR" "Error in hard reset. Probably sha sum or tag name is added instead of branch name. Trying to reset again."
        git reset --hard $BRANCH_NAME
      fi
      set -e
    else
      #git clone -b $BRANCH_NAME git@github.com:NervanaSystems/$PROJECT_NAME.git --recursive
      git clone -b $BRANCH_NAME https://github.com/IntelAI/$PROJECT_NAME.git --recursive
      cd $PROJECT_NAME
    fi
}

compile_platform() {
    print_log "DEBUG" "Compile platform"

    # till repo won't be public

    mkdir -p ${SCRIPTDIR}/../../../../cloud
    cd ${SCRIPTDIR}/../../../../cloud
    retrieve_repo nauta ${CurrentBranch}
    cd ${SCRIPTDIR}/../../../../cloud

    rm -f nauta.tar
    tar cf nauta.tar nauta
    cd ${SCRIPTDIR}
    run_scp_command ${SCRIPTDIR}/../../../../cloud/nauta.tar ${GATEWAY_USER}@${GATEWAY_IP}:nauta.tar

    if [ "${PROXY_TO_GATEWAY}" = "" ]; then
        print_log "DEBUG" ssh -i "${ExternalKey}" ${GATEWAY_USER}@${GATEWAY_IP} "./remote_scripts/compile_platform.sh ${INSTALL_FILE_NAME} ${INSTALL_CLIENT_FILE_NAME}"
        ssh -i "${ExternalKey}" ${GATEWAY_USER}@${GATEWAY_IP} "./remote_scripts/compile_platform.sh ${INSTALL_FILE_NAME} ${INSTALL_CLIENT_FILE_NAME} ${VERSION_MAJOR} ${VERSION_MINOR} ${VERSION_NO} ${VERSION_ID}"
    else
        print_log "DEBUG" ssh -i "${ExternalKey}" -o ProxyCommand="${PROXY_TO_GATEWAY}" ${GATEWAY_USER}@${GATEWAY_IP} "./remote_scripts/compile_platform.sh ${INSTALL_FILE_NAME} ${INSTALL_CLIENT_FILE_NAME}"
        ssh -i "${ExternalKey}" -o ProxyCommand="${PROXY_TO_GATEWAY}" ${GATEWAY_USER}@${GATEWAY_IP} "./remote_scripts/compile_platform.sh ${INSTALL_FILE_NAME} ${INSTALL_CLIENT_FILE_NAME} ${VERSION_MAJOR} ${VERSION_MINOR} ${VERSION_NO} ${VERSION_ID}"
    fi
}

clean() {
   print_log "DEBUG" "\
    cd ../../.. && \
        make gcp-clean \
    "

    cd ../../.. && \
        make gcp-clean
}

show_help() {
   print_log "DEBUG" "Help"
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
LONG_OPTIONS+="client-file:,"
LONG_OPTIONS+="network-settings:,"
LONG_OPTIONS+="compile-platform-on-cloud:,"
LONG_OPTIONS+="service-account-config-file:,"
LONG_OPTIONS+="platform-config-file:,"
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
        --client-file) ClientFile="$2"; shift 2 ;;
        --network-settings) NetworkSettings="$2"; shift 2 ;;
        --compile-platform-on-cloud) CompilePlatformOnCloud="$2"; shift 2 ;;
        --service-account-config-file) ServiceAccountConfigFile="$2"; shift 2 ;;
        --platform-config-file) PlatformConfigFile="$2"; shift 2 ;;
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

if [ "${CompilePlatformOnCloud}" = "true" ]; then
    set_connectivity_params
    show_connectivity_parameters
    transfer_scripts
    transfer_config_files
    VERSION_MAJOR=1
    VERSION_MINOR=0
    VERSION_NO=0
    VERSION_ID=`date +"%Y%m%d%H%M%S"`
    INSTALL_FILE_NAME="nauta-${VERSION_MAJOR}.${VERSION_MINOR}.${VERSION_NO}-${VERSION_ID}.tar.gz"
    INSTALL_CLIENT_FILE_NAME="nctl-${VERSION_MAJOR}.${VERSION_MINOR}.${VERSION_NO}-${VERSION_ID}-linux.tar.gz"
    install_compiler_prerequisities
    compile_platform
    install_platform_prerequisities
    install_platform
fi

if [ "${InstallFile}" != "" ]; then
    set_connectivity_params
    show_connectivity_parameters
    transfer_scripts
    transfer_config_files
    transfer_install_file
    install_compiler_prerequisities
    install_platform_prerequisities
    install_platform
fi

if [ "${Operation}" = "destroy" ]; then
    destroy_cluster
fi

print_log "DEBUG" "Script finish"
