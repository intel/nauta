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

import argparse
from enum import Enum
import logging
import os
from time import sleep
from threading import Thread
from typing import Optional
import pickle

from retry.api import retry_call
import tensorflow as tf

from experiment_metrics.api import publish
import grpc
from kubernetes import config, client
from tensorflow_serving.apis import predict_pb2, prediction_service_pb2_grpc

PROGRESS_METRIC_KEY = 'progress'

API_GROUP_NAME = 'aggregator.aipg.intel.com'
RUN_PLURAL = 'runs'
RUN_VERSION = 'v1'

LABEL_KEY = "label"
RESULT_KEY = "result"

progress = 0
max_progress = 1
stop_thread = False

log_level_env_var = os.getenv('LOG_LEVEL')


class APPLICABLE_FORMATS(Enum):
    TF_RECORD = "tf-record"


if log_level_env_var:
    desired_log_level = logging.getLevelName(log_level_env_var.upper())
    if desired_log_level not in (logging.CRITICAL, logging.ERROR, logging.WARNING, logging.INFO, logging.DEBUG):
        desired_log_level = logging.INFO
else:
    desired_log_level = logging.INFO

logging.basicConfig(level=desired_log_level)

# CAN-1237 - by setting level of logs for k8s rest client to INFO I'm removing displaying content of
# every rest request sent by k8s client
k8s_rest_logger = logging.getLogger('kubernetes.client.rest')
k8s_rest_logger.setLevel(logging.INFO)


def do_batch_inference(server_address: str, input_dir_path: str, output_dir_path: str, related_run_name: str,
                       input_format: str):
    detected_files = []

    for root, _, files in os.walk(input_dir_path):
        for name in files:
            detected_files.append(os.path.join(root, name))

    detected_files.sort()

    channel = grpc.insecure_channel(server_address)
    stub = prediction_service_pb2_grpc.PredictionServiceStub(channel)

    global max_progress
    global progress
    max_progress = len(detected_files)

    reverted_progress = try_revert_progress(related_run_name)
    if reverted_progress:
        logging.debug(f"new progress for processing: {progress}")
        progress = reverted_progress
    else:
        logging.debug("no progress reverted")

    files_to_process = detected_files[progress:]

    for data_file in files_to_process:
        logging.debug(f"processing file: {data_file}")

        if input_format == APPLICABLE_FORMATS.TF_RECORD.value:
            record_iterator = tf.python_io.tf_record_iterator(path=data_file)

            id = 0
            # if tf-record input format is chosen, results are stored in Python list containing dictionary items
            # each item contains label (key - label) and binary object (key - result)
            output_list = []

            filename, _ = os.path.splitext(data_file)

            for string_record in record_iterator:
                example = tf.train.Example()
                example.ParseFromString(string_record)

                label = example.features.feature['label'].bytes_list.value[0].decode('utf_8') \
                    if example.features.feature.get('label') else None

                if not label:
                    label = data_file
                    if len(record_iterator) > 1:
                        label = "{}_{}".format(filename, id)
                        id += 1

                binary_result = make_prediction(input=example.features.feature['data_pb'].bytes_list.value[0],
                                                stub=stub)

                output_list.append({LABEL_KEY: label, RESULT_KEY: binary_result})

            output_filename = "{}.result".format(data_file)

            with open(f'{output_dir_path}/{os.path.basename(output_filename)}', mode='wb') as fi:
                pickle.dump(obj=output_list, file=fi, protocol=pickle.HIGHEST_PROTOCOL)

        else:
            with open(data_file, mode='rb') as fi:
                pb_bytes = fi.read()

                make_prediction(input=pb_bytes,
                                stub=stub,
                                output_filename=data_file,
                                output_dir_path=output_dir_path)

        progress += 1
        logging.info(f'progress: {progress}/{max_progress}')


def build_label_from_filename(filename: str, id: int):
    name, _ = os.path.splitext(filename)

    return "{}_{}".format(name, id)


def make_prediction(input: bytes, stub: prediction_service_pb2_grpc.PredictionServiceStub,
                    output_filename: str = None, output_dir_path: str = None):
    request = predict_pb2.PredictRequest()
    try:
        request.ParseFromString(input)
    except Exception as ex:
        raise RuntimeError(f"failed to parse {output_filename}") from ex

    # actual call without retry:
    # result = stub.Predict(request, timeout=30.0)  # timeout 30 seconds
    result = retry_call(stub.Predict, fargs=[request], fkwargs={"timeout": 30.0}, tries=5, delay=30)

    result_pb_serialized: bytes = result.SerializeToString()

    if output_filename:
        with open(f'{output_dir_path}/{os.path.basename(output_filename)}', mode='wb') as fi:
            fi.write(result_pb_serialized)

    return result_pb_serialized


def publish_progress():
    logging.debug("starting publish_progress ...")
    progress_percent = 0
    while progress_percent != 100 and not stop_thread:
        new_progress_percent = progress/max_progress * 100 if max_progress else 100
        logging.debug(f"new_progress_percent: %.1f" % new_progress_percent)
        if new_progress_percent != progress_percent:
            progress_percent = new_progress_percent

            metrics = {
                PROGRESS_METRIC_KEY: str("%.1f" % progress_percent)
            }
            logging.debug("publishing metrics ...")
            publish(metrics)

        sleep(1)


def try_revert_progress(run_name: str) -> Optional[int]:
    logging.debug("trying to revert progress...")
    config.load_incluster_config()

    with open("/var/run/secrets/kubernetes.io/serviceaccount/namespace", mode='r') as file:
        my_current_namespace = file.read()

    if not my_current_namespace:
        raise RuntimeError(f"error reading my current namespace {str(my_current_namespace)}")

    runs_custom_obj_client = client.CustomObjectsApi()

    try:
        run = runs_custom_obj_client.get_namespaced_custom_object(group=API_GROUP_NAME, version=RUN_VERSION,
                                                                  plural=RUN_PLURAL, namespace=my_current_namespace,
                                                                  name=run_name)
    except Exception:
        logging.exception("error when contacting to kubernetes API")
        return None

    try:
        saved_progress: str = run['spec']['metrics']['progress']
    except KeyError:
        logging.debug(f"no progress metric detected")
        return None

    logging.debug(f"progress reverted! progress from metrics: {saved_progress}")
    saved_progress: float = float(saved_progress)

    real_progress = saved_progress/100 * max_progress if max_progress else 100

    progress = int(real_progress)
    return progress
    

def main():
    related_run_name = os.getenv('RUN_NAME')
    if not related_run_name:
        raise RuntimeError('RUN_NAME env var must be set for publishing progress metrics!')

    parser = argparse.ArgumentParser()
    parser.add_argument('--input_dir_path', type=str)
    parser.add_argument('--output_dir_path', type=str)
    parser.add_argument('--input_format', type=str)

    args = parser.parse_args()

    if not args.input_dir_path:
        parser.error("'input_dir_path' is required!")

    input_dir_path = args.input_dir_path
    output_dir_path = args.output_dir_path if args.output_dir_path else '/mnt/output/experiment'
    input_format = args.input_format

    if not os.path.isdir(input_dir_path) or len(os.listdir(input_dir_path)) == 0:
        raise RuntimeError(f"input directory: '{input_dir_path}' does not exist or is empty!")

    progress_thread = Thread(target=publish_progress)
    progress_thread.start()

    try:
        do_batch_inference(server_address=os.getenv('TENSORFLOW_MODEL_SERVER_SVC_NAME', ''),
                           input_dir_path=input_dir_path,
                           output_dir_path=output_dir_path,
                           related_run_name=related_run_name,
                           input_format=input_format)
    except Exception:
        global stop_thread
        stop_thread = True
        raise


if __name__ == '__main__':
    main()
