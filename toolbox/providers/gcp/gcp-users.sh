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
    check_file_presence "${K8sOutputFile}"
    check_file_presence "${GcpConfig}"
    check_file_presence "${GatewayUsers}"
    check_file_presence "${NetworkSettings}"
}

function set_defaults {
    print_log "DEBUG" "Set defaults"
#    if [ "${Operation}" = "" ] ; then Operation="create" ; fi
    if [ "${K8sCluster}" = "" ] ; then K8sCluster="nauta" ; fi
    if [ "${ExternalKey}" = "" ] ; then ExternalKey="~/.ssh/id_rsa" ; fi
    if [ "${GcpConfig}" = "" ] ; then GcpConfig="`pwd`/gcp-config.yml" ; fi
    if [ "${K8sOutputFile}" = "" ] ; then K8sOutputFile="`pwd`/${K8sCluster}.info" ; fi
    if [ "${NetworkSettings}" = "" ] ; then NetworkSettings="`pwd`/../../config.yml" ; fi

    if [ "${GatewayUsers}" = "" ] ; then GatewayUsers="`pwd`/../../support/gateway-users/gateway-users.yml" ; fi

    CurrentBranch=`git status | grep "On branch" | awk '{print $3}'`
    if [ "${CurrentBranch}" = "" ] ; then
        CurrentBranch="develop"
    fi

    PoolType=`cat "${GcpConfig}" | grep "pool_type" | awk -F '"' '{print $2}'`
}

show_parameters() {
    print_log "DEBUG" "Build parameters:"
    echo -e "\t\tK8sCluster=${K8sCluster}"
    echo -e "\t\tK8sOutputFile=${K8sOutputFile}"
    echo -e "\t\tNetworkSettings=${NetworkSettings}"
    echo -e "\t\tGatewayUsers=${GatewayUsers}"
    echo -e "\t\tGcpConfig=${GcpConfig}"
    echo -e "\t\tExternalKey=${ExternalKey}"
    echo -e ""
    echo -e "\t\tCurrentBranch=${CurrentBranch}"
    echo -e "\t\tPoolType=${PoolType}"

    echo -e ""
    echo -e "\t\tSCRIPTDIR=${SCRIPTDIR}"
}

set_connectivity_params() {
    print_log "DEBUG" "Set connectivity parameters to access gateway node"
    GATEWAY_IP=`cat ${K8sOutputFile} | grep "gateway_ip" | awk -F '"' '{print $2}'`
    GATEWAY_USER=`cat "${GcpConfig}" | grep "external_username" | awk -F '"' '{print $2}'`
    PROXY_TO_GATEWAY=`cat "${NetworkSettings}" | grep "ssh_args_for_cmd_line" | awk -F '"' '{print $2}'`
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

transfer_config() {
    print_log "DEBUG" "Transfer config file"
    run_scp_command ${GatewayUsers}/ ${GATEWAY_USER}@${GATEWAY_IP}:gateway-users.yml
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

create_users_prerequisities() {
    print_log "DEBUG" "Install compile prerequisities on gateway"
    if [ "${PROXY_TO_GATEWAY}" = "" ]; then
        print_log "DEBUG" ssh -i "${ExternalKey}" ${GATEWAY_USER}@${GATEWAY_IP} "./remote_scripts/create_users_prerequisities.sh"
        ssh -i "${ExternalKey}" ${GATEWAY_USER}@${GATEWAY_IP} "./remote_scripts/create_users_prerequisities.sh"
    else
        print_log "DEBUG" ssh -i "${ExternalKey}" -o ProxyCommand="${PROXY_TO_GATEWAY}" ${GATEWAY_USER}@${GATEWAY_IP} "./remote_scripts/create_users_prerequisities.sh"
        ssh -i "${ExternalKey}" -o ProxyCommand="${PROXY_TO_GATEWAY}" ${GATEWAY_USER}@${GATEWAY_IP} "./remote_scripts/create_users_prerequisities.sh"
    fi
}

create_users() {
    # till repo won't be public

    mkdir -p ${SCRIPTDIR}/../../../../cloud
    cd ${SCRIPTDIR}/../../../../cloud
    retrieve_repo nauta ${CurrentBranch}
    cd ${SCRIPTDIR}/../../../../cloud

    rm -f nauta.tar
    tar cfz nauta.tar.gz nauta
    cd ${SCRIPTDIR}
    run_scp_command ${SCRIPTDIR}/../../../../cloud/nauta.tar.gz ${GATEWAY_USER}@${GATEWAY_IP}:nauta.tar.gz


    print_log "DEBUG" "Install platform prerequisities on gateway"
    if [ "${PROXY_TO_GATEWAY}" = "" ]; then
        print_log "DEBUG" ssh -i "${ExternalKey}" ${GATEWAY_USER}@${GATEWAY_IP} "./remote_scripts/create_users.sh ${PoolType}"
        ssh -i "${ExternalKey}" ${GATEWAY_USER}@${GATEWAY_IP} "./remote_scripts/create_users.sh ${PoolType}"
    else
        print_log "DEBUG" ssh -i "${ExternalKey}" -o ProxyCommand="${PROXY_TO_GATEWAY}" ${GATEWAY_USER}@${GATEWAY_IP} "./remote_scripts/create_users.sh ${PoolType}"
        ssh -i "${ExternalKey}" -o ProxyCommand="${PROXY_TO_GATEWAY}" ${GATEWAY_USER}@${GATEWAY_IP} "./remote_scripts/create_users.sh ${PoolType}"
    fi
}

transfer_scripts() {
    print_log "DEBUG" "Transfer scripts"
    run_scp_command ${SCRIPTDIR}/../../support/gateway-users/files/remote_scripts ${GATEWAY_USER}@${GATEWAY_IP}:
}

show_help() {
   print_log "DEBUG" "Help"
   echo -e `cat ${SCRIPTDIR}/gcp-users.sh.help | sed 's/\[RED\]/\\\033\[0;31m/g' | sed 's/\[GREEN\]/\\\033\[0;32m/g' | sed 's/\[YELLOW\]/\\\033\[0;33m/g' | sed 's/\[NOCOLOR\]/\\\033\[0m/g' | sed 's/\[BR\]/\\\n/g'`
}

SCRIPTDIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
WORKSPACEDIR="${SCRIPTDIR}/../../../.workspace"

#validate_prerequisities

LONG_OPTIONS=""
LONG_OPTIONS+="k8s-cluster:,"
LONG_OPTIONS+="external-key:,"
LONG_OPTIONS+="network-settings:,"
LONG_OPTIONS+="gcp-config:,"
LONG_OPTIONS+="gateway-users:,"
LONG_OPTIONS+="help"

SHORT_OPTIONS="c:"
OPTS=`getopt -l ${LONG_OPTIONS} -o ${SHORT_OPTIONS} -n 'gcp-users.sh' -- "$@"`
eval set -- "$OPTS"
while true; do
   case "$1" in
        --help) show_help; exit 1 ;;
        --k8s-cluster) K8sCluster="$2"; shift 2 ;;
        --external-key) ExternalKey="$2"; shift 2 ;;
        --gcp-config) GcpConfig="$2"; shift 2 ;;
        --gateway-users) GatewayUsers="$2"; shift 2 ;;
        --network-settings) NetworkSettings="$2"; shift 2 ;;
        --) break;;
        *) echo "Internal error! |$1|$2|" ; exit 1 ;;
   esac
done

set_defaults
show_parameters
validate_arguments

set_connectivity_params
show_connectivity_parameters

transfer_scripts
transfer_config

create_users_prerequisities
create_users

print_log "DEBUG" "Script finish"
