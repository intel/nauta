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

sudo rm -rf compile
mkdir -p compile

tar xvf carbon.tar -C compile
cd compile/carbon

make nctl-build

find ~/compile/carbon/applications/cli -maxdepth 1 -name "nctl*.tar.gz" -exec cp {} ~/$2 \;

echo "Client file is present as ~/$2"

sudo make k8s-installer-build

find ~/compile/carbon/tools/.workspace -maxdepth 1 -name "nauta*.tar.gz" -exec cp {} ~/$1 \;

echo "Image file is present as ~/$1"
