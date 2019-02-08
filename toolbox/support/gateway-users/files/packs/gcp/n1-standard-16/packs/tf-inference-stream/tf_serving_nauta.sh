#!/usr/bin/env bash
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


cp -rf ${MODEL_PATH}/. ${MODEL_BASE_PATH}

if [ -z \"$(ls -A /models)\" ]; then
    echo 'Error: the provided path to model {{ .Values.modelPath }} is invalid or contains no files.'
    exit 1
fi

tensorflow_model_server --port=8500 --rest_api_port=8501 --model_name=${MODEL_NAME} --model_base_path=${MODEL_BASE_PATH} &

while true;
do
if [[ -e /pod-data/END ]]; then
    exit 0
else
    sleep 10
fi
done
