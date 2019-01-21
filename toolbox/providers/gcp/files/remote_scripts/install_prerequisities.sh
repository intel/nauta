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

sudo apt-get update
sudo apt-get install python \
                     python-pip \
                     python-dev \
                     virtualenv \
                     python3-pip \
                     python3-dev \
                     python3-venv \
                     gcc \
                     openssl \
                     libssl-dev \
                     libffi-dev \
                     -y
