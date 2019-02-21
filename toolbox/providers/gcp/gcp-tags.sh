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
        print_log "ERROR" "File $1 does not exists"
        exit 1
    fi
}

function validate_prerequisities {
    print_log "INFO" "Validate prerequisities"
}

function validate_arguments {
    print_log "DEBUG" "Validate arguments"
    check_file_presence "${GcpConfig}"
    check_file_presence "${ServiceAccountConfigFile}"
    if [ "${InstallFile}" != "" ]; then
        check_file_presence "${InstallFile}"
    fi
}

function set_defaults {
    print_log "DEBUG" "Set defaults"
    if [ "${K8sCluster}" = "" ] ; then K8sCluster="nauta" ; fi
    if [ "${GcpConfig}" = "" ] ; then GcpConfig="`pwd`/gcp-config.yml" ; fi
    if [ "${K8sOutputFile}" = "" ] ; then K8sOutputFile="`pwd`/${K8sCluster}.info" ; fi
    if [ "${ServiceAccountConfigFile}" = "" ] ; then ServiceAccountConfigFile="`pwd`/gcp-service-account.json" ; fi

    if [ "${ClusterOwner}" = "" ] ; then ClusterOwner="`whoami`" ; fi
}

show_parameters() {
    print_log "DEBUG" "Build parameters:"
    echo -e "\t\tK8sCluster=${K8sCluster}"
    echo -e "\t\tK8sOutputFile=${K8sOutputFile}"
    echo -e "\t\tClusterOwner=${ClusterOwner}"
    echo -e "\t\tServiceAccountConfigFile=${ServiceAccountConfigFile}"

    echo -e ""
    echo -e "\t\tSCRIPTDIR=${SCRIPTDIR}"
}

set_connectivity_params() {
    print_log "DEBUG" "Set connectivity parameters to access gateway node"
    GATEWAY_IP=`cat ${K8sOutputFile} | grep "gateway_ip" | awk -F '"' '{print $2}'`
    TESTNODE_IP=`cat ${K8sOutputFile} | grep "testnode_ip" | awk -F '"' '{print $2}'`
    CLUSTER_ZONE=`cat ${GcpConfig} | grep "zone" | awk -F '"' '{print $2}'`
}

show_connectivity_parameters() {
    print_log "DEBUG" "Conectivity parameters:"
    echo -e "\t\tGATEWAY_IP=${GATEWAY_IP}"
    echo -e "\t\tTESTNODE_IP=${TESTNODE_IP}"
    echo -e "\t\tCLUSTER_ZONE=${CLUSTER_ZONE}"
}

tag_cluster() {
    print_log "DEBUG" "Tag cluster"
    tags_string="owner=${ClusterOwner},provider=gketf,gateway_ip=${GATEWAY_IP},testnode_ip=${TESTNODE_IP}"
    tags_string=`echo ${tags_string} | sed 's/\./_/g'`
    print_log "DEBUG" gcloud auth activate-service-account --key-file ${ServiceAccountConfigFile}
    gcloud auth activate-service-account --key-file ${ServiceAccountConfigFile}
    print_log "DEBUG" gcloud beta container clusters update ${K8sCluster} --update-labels ${tags_string}
    gcloud beta container clusters update ${K8sCluster} --zone ${CLUSTER_ZONE} --update-labels ${tags_string}
}

SCRIPTDIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
WORKSPACEDIR="${SCRIPTDIR}/../../../.workspace"

#validate_prerequisities

LONG_OPTIONS=""
LONG_OPTIONS+="k8s-cluster:,"
LONG_OPTIONS+="cluster-owner:,"
LONG_OPTIONS+="service-account-config-file:,"
LONG_OPTIONS+="gcp-config:,"

SHORT_OPTIONS="c:"
OPTS=`getopt -l ${LONG_OPTIONS} -o ${SHORT_OPTIONS} -n 'gcp-tags.sh' -- "$@"`
eval set -- "$OPTS"
while true; do
   case "$1" in
        --k8s-cluster) K8sCluster="$2"; shift 2 ;;
        --gcp-config) GcpConfig="$2"; shift 2 ;;
        --cluster-owner) ClusterOwner="$2"; shift 2 ;;
        --service-account-config-file) ServiceAccountConfigFile="$2"; shift 2 ;;
        --) break;;
        *) echo "Internal error! |$1|$2|" ; exit 1 ;;
   esac
done

set_defaults
show_parameters
validate_arguments

set_connectivity_params
show_connectivity_parameters

tag_cluster
print_log "DEBUG" "Script finish"
