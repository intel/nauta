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

function set_object_value() {
    kubectl patch u $1 --type merge --patch "{\"spec\":{\"$2\":\"$3\"}}"
}

function set_object_int_value() {
    kubectl patch u $1 --type merge --patch "{\"spec\":{\"$2\":$3}}"
}

BLOCKED_USERNAMES="root admin centos samba"
function username_blocked() {
  for name in ${BLOCKED_USERNAMES}; do
    if [ X"$1" == X"${name}" ]; then
      return 1
    fi
  done
}

function get_free_uid() {
    echo "Searching for free uid..." 1>&2
    MAX_CURRENT_USER_ID=`kubectl --namespace=nauta get configmap max-user-id -o='jsonpath={.data.max-user-id}'`
    FREE_USER_UID=$((MAX_CURRENT_USER_ID+1))
    echo "Current MAX_CURRENT_USER_ID is $MAX_CURRENT_USER_ID; updating to $FREE_USER_UID" 1>&2
    NEW_MAX_CURRENT_USER_ID=$FREE_USER_UID

    WAS_UPDATED="false"
    for (( n=0 ; n<10 ; n++ )) ; do
        if kubectl --namespace=nauta patch configmap max-user-id -p "{ \"data\": { \"max-user-id\": \"$NEW_MAX_CURRENT_USER_ID\" } }" 1>&2 ; then
            echo "MAX_CURRENT_USER_ID updated to $NEW_MAX_CURRENT_USER_ID" 1>&2
            WAS_UPDATED="true"
            break
        else
            echo "MAX_CURRENT_USER_ID update failed, retrying iter $n/10 in 10s..." 1>&2
        fi
        sleep 10
    done
    if [[ "x$WAS_UPDATED" == "false" ]] ; then
        echo "Failed to update NEW_MAX_CURRENT_USER_ID to $NEW_MAX_CURRENT_USER_ID - fatal error." 1>&2
        exit 3
    fi
    echo $FREE_USER_UID
    return
}

function create_user() {
  USER=$1
  kUID=$2
  PASSWORD=$3
  echo "Checking if group already exists $kUID ..."
  if ! id -u $kUID; then
      echo "Adding group $kUID (user $USER)"
      groupadd -g $kUID $USER
  fi
  echo "Checking if user already exists $kUID ..."
  if ! id $kUID; then
      echo "Adding user $kUID (user $USER)"
      useradd -u $kUID -g $kUID -m $USER
  fi
  echo "Setting samba password for ${USER}"
  ( echo ${PASSWORD} ; echo ${PASSWORD}; ) | smbpasswd -a "${USER}"
}

user=$1
#if username_blocked ${user}; then
#  echo "User name ${name} is blocked"
#  exit 1
#fi

STATE=`kubectl get u $user -o 'jsonpath={.spec.state}'`
echo "User $user in state $STATE"
echo "Creating user $user"
echo "Checking if user has samba password secret in kubernetes..."
if ! kubectl -n $user get secret password; then
    echo "  -> no secret, creating one..."
    echo """
apiVersion: v1
kind: Secret
metadata:
  name: password
  namespace: $user
data:
  password: `cat /dev/urandom | tr -dc 'a-zA-Z0-9' | fold -w 32 | head -n 1 | base64 -w0`
""" | kubectl create -f -
fi
echo "getting user samba password from secret..."
PASSWORD=`kubectl -n $user get secret password -o 'jsonpath={.data.password}' | base64 -d`
kUID=`kubectl get u $user -o 'jsonpath={.spec.uid}'`
if [ X"$kUID" == X"" ]; then
    echo "Generating UID"
    kUID=`get_free_uid $user`
    echo "setting UID for $user in kubernetes..."
    set_object_int_value $user uid $kUID
    echo " -> done!"
fi
create_user $user $kUID $PASSWORD
echo "Create input and output directories"
mkdir -p /smb/input/$user
mkdir -p /smb/output/$user

echo "Adjusting permissions..."
chown -R $kUID:$kUID /smb/input/$user /smb/output/$user

if [ X"$STATE" != X"CREATED" ]; then
    echo "Update user state to CREATED"
    set_object_value $user state CREATED
fi

date
echo " === User creation completed ==="
exit 0
