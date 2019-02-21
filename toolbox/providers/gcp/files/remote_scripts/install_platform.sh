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

sudo rm -rf install
mkdir -p install
tar xvf artifacts/$1 -C install
chmod +x install/installer.sh

CONFIG_FILE=/home/nauta/config.yml

if [ -f ~/platform-config.yml ]; then
    CONFIG_FILE=~/platform-config.yml
fi

LC_ALL=en_US.UTF-8 LANG=en_US.UTF-8 ENV_CONFIG=${CONFIG_FILE} install/installer.sh nauta-install
