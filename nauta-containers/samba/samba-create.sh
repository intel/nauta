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

echo "Ensuring /smb/input/public and /smb/output public exist and have proper permissions..."
mkdir -vp /smb/input/public
mkdir -vp /smb/output/public
chmod -v 0777 /smb/input/public /smb/output/public
echo "OK."

function create_user() {
    echo "(Re)Creating user $1"
    /bin/samba-create-user.sh $1 && /bin/samba-create-pv.sh $1 || echo "Unable to create user $1"
}

ALL_USERS_JSON=`kubectl get u -o=json`
ALL_USERS_COUNT=`echo "${ALL_USERS_JSON}" | jq '.items | length'`

date
echo "Current user count: $ALL_USERS_COUNT"

for (( n = 0 ; n < $ALL_USERS_COUNT ; n++ )) ; do
    CURRENT_USER=`echo "$ALL_USERS_JSON" | jq ".items[$n]"`
    CURRENT_USER_NAME=`echo "$CURRENT_USER" | jq -r '.metadata.name'`
    CURRENT_USER_UID=`echo "$CURRENT_USER" | jq -r '.spec.uid'`
    CURRENT_USER_STATE=`echo "$CURRENT_USER" | jq -r '.spec.state'`
    echo "Found user: $CURRENT_USER_NAME, uid: $CURRENT_USER_UID, state: $CURRENT_USER_STATE"

    if [[ "x$1" == "x--init" ]] ; then
        echo " -> first run, creating user no matter of their reported state ($CURRENT_USER_STATE)"
        create_user $CURRENT_USER_NAME
    else
        if [[ "x$CURRENT_USER_STATE" != "xCREATED" ]] ; then
            create_user $CURRENT_USER_NAME
        else
            echo "User already exists, doing nothing."
            if [[ "x$CURRENT_USER_UID" == "x" ]] ; then
                echo "Warning: user doesn't have UID assigned"
            fi
        fi
    fi
done

