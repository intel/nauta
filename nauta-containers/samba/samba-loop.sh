#!/bin/bash
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


for (( ; ; )) ; do
    echo "Checking if max-user-id config map exists..."
    if kubectl --namespace=nauta get configmap max-user-id ; then
        echo "OK: max-user-id config maps already exists."
        break
    fi    
    
    if kubectl --namespace=nauta get configmap max-user-id 2>&1 | grep NotFound ; then
        echo "Missing max-user-id config map, creating..."
        kubectl --namespace=nauta create configmap max-user-id --from-literal=max-user-id=9999
    fi
    if kubectl --namespace=nauta get configmap max-user-id ; then
        echo "OK: max-user-id config maps was created."
        break
    fi
    sleep 5
done


FIRST_RUN=--init
while true; do
  /bin/samba-create.sh $FIRST_RUN || echo "Samba creation loop failed"
  /bin/samba-delete-users.sh
  FIRST_RUN=
  sleep 5
done

