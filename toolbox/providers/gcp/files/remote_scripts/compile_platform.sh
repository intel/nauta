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

# Parameters (positional)
# ${INSTALL_FILE_NAME} ${INSTALL_CLIENT_FILE_NAME} ${VERSION_MAJOR} ${VERSION_MINOR} ${VERSION_NO} ${VERSION_ID} ${VERSION_SUFFIX}

mkdir -p artifacts

sudo rm -rf compile
mkdir -p compile

tar xvf nauta.tar -C compile
cd compile/nauta

make nctl-build VERSION_MAJOR=$3 VERSION_MINOR=$4 VERSION_NO=$5 VERSION_ID=$6 VERSION_SUFFIX=$7

find ~/compile/nauta/applications/cli -maxdepth 1 -name "nctl*.tar.gz" -exec cp {} ~/artifacts/$2 \;

ln -fs ~/artifacts/$2 ~/artifacts/nctl.installer

echo "Client file is present as ~/$2"

sudo make k8s-installer-build VERSION_MAJOR=$3 VERSION_MINOR=$4 VERSION_NO=$5 VERSION_ID=$6 VERSION_SUFFIX=$7

find ~/compile/nauta/tools/.workspace -maxdepth 1 -name "nauta*.tar.gz" -exec cp {} ~/artifacts/$1 \;

echo "Image file is present as ~/$1"
