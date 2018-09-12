#!/usr/bin/env bash

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
