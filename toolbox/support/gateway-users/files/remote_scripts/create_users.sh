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

# $1 PoolType for packs

PWD=`pwd`

pwd

sudo apt-get install make -y

SCRIPTDIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

echo ${SCRIPTDIR}

# Uncomment if venv issues will occur
# sudo rm -rf users
mkdir -p users

tar xfz nauta.tar.gz -C users
cd users/nauta

make create-gateway-users ENV_GATEWAY_USERS=~/gateway-users.yml ENV_POOL_TYPE=$1

cd ${PWD}