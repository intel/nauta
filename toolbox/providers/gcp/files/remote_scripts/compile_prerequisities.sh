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

sudo add-apt-repository ppa:deadsnakes/ppa -y

sudo apt-get update
sudo apt-get install make \
                     python \
                     python-pip \
                     python-dev \
                     virtualenv \
                     python3-pip \
                     python3-dev \
                     python3-venv \
                     gcc openssl \
                     libssl-dev \
                     libffi-dev \
                     libxml2-dev \
                     libxslt1-dev \
                     pigz \
                     libjpeg8-dev \
                     zlib1g-dev \
                     apt-transport-https \
                     ca-certificates \
                     curl \
                     software-properties-common \
                     python3.6 \
                     python3.6-dev \
                     python3.6-venv \
                     binutils \
                     build-essential \
                     cifs-utils \
                     -y

pip3 install virtualenv
pip install docker-py

curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -

RELEASE_NAME=`lsb_release -c | awk '{print $2}'`
sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu ${RELEASE_NAME} test"

sudo apt-get update

sudo apt-get install docker-ce -y

pip install jmespath

sudo usermod -aG docker nauta

