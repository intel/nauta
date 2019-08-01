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

set -e

function delete_pv() {
    USER=$1
    INPUT_HOME_NAME=${APP_RELEASE}-${USER}-input-home
    INPUT_PUB_NAME=${APP_RELEASE}-${USER}-input-public

    OUTPUT_HOME_NAME=${APP_RELEASE}-${USER}-output-home
    OUTPUT_PUB_NAME=${APP_RELEASE}-${USER}-output-public

    kubectl delete pv $INPUT_HOME_NAME $INPUT_PUB_NAME $OUTPUT_HOME_NAME $OUTPUT_PUB_NAME
}

function delete_user() {
    USER=$1
    # check whether a user still exists in the system - at this moment this user
    # no longer exists in k8s cluster
    `id $USER >/dev/null 2>&1`

    if [ $? -eq 0 ];
    then
        echo "Deleting user $USER"
        # delete samba users
        smbpasswd -x $USER
        # remove pv
        delete_pv $USER
        # delete user
        userdel -r $USER
        # remove item in queue of users to be deleted
        kubectl patch configmap nauta-user-del --type=json -p="[{\"op\": \"remove\", \"path\": \"/data/$USER\"}]" -n nauta
    else
        echo "User $USER not found"
    fi
}

USERS_TO_BE_DELETED=`kubectl get cm nauta-user-del -n nauta -o=json | python -c "import sys, json; k = json.load(sys.stdin); k = k['data'].keys() if 'data' in k else ''; print(' '.join(k))"`

if [[ $USERS_TO_BE_DELETED != 'null' ]];
then
    for USER in `echo $USERS_TO_BE_DELETED`
    do
        echo "Deleting $USER"
        delete_user "$USER" || echo " An error occured during removal!"
    done
fi
