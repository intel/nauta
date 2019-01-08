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

# The source code contained or described herein and all documents related to
# the source code ("Material") are owned by Intel Corporation or its suppliers
# or licensors. Title to the Material remains with Intel Corporation or its
# suppliers and licensors. The Material contains trade secrets and proprietary
# and confidential information of Intel or its suppliers and licensors. The
# Material is protected by worldwide copyright and trade secret laws and treaty
# provisions. No part of the Material may be used, copied, reproduced, modified,
# published, uploaded, posted, transmitted, distributed, or disclosed in any way
# without Intel's prior express written permission.

# No license under any patent, copyright, trade secret or other intellectual
# property right is granted to or conferred upon you by disclosure or delivery
# of the Materials, either expressly, by implication, inducement, estoppel or
# otherwise. Any license under such intellectual property rights must be express
# and approved by Intel in writing.
NAMESPACE="kube-system"
echo "Getting registry pod name"
DOCKER_REGISTRY_POD=`kubectl get --namespace=$NAMESPACE --no-headers=true -l app=docker-registry pods -o custom-columns=:metadata.name`
if [[ -z "$DOCKER_REGISTRY_POD" ]]; then
  echo "Unable to get docker registry pod name";
  exit 1
fi
echo "Docker registry pod = $DOCKER_REGISTRY_POD"

echo "Getting docker registry port"
DOCKER_REGISTRY_PORT=`kubectl get --namespace=$NAMESPACE --no-headers=true -l app=docker-registry svc -o go-template='{{range .items}}{{range.spec.ports}}{{.nodePort}}{{end}}{{end}}'`
if [[ -z "$DOCKER_REGISTRY_PORT" ]]; then
  echo "Unable to get docker registry port"
  exit 2
fi
echo "Docker registry port = $DOCKER_REGISTRY_PORT"

echo "Port-forwarding..."
kubectl port-forward --namespace=$NAMESPACE $DOCKER_REGISTRY_POD $DOCKER_REGISTRY_PORT:5000 &>/dev/null &

UNAME="$(uname -s)"
if [[ $UNAME = "Darwin" ]]; then
  echo "Running on Darwin OS, starting docker host port-forwarding"
  if ! docker top dlsctl-registry &>/dev/null; then
    echo "Starting dlsctl-registry container"
    docker run -d --rm --net=host --name=dlsctl-registry alpine/socat TCP-LISTEN:$DOCKER_REGISTRY_PORT,fork,reuseaddr TCP:host.docker.internal:$DOCKER_REGISTRY_PORT
  fi
fi

echo "Configuring draft"
draft config set registry 127.0.0.1:$DOCKER_REGISTRY_PORT

