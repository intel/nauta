#
# INTEL CONFIDENTIAL
# Copyright (c) 2018 Intel Corporation
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
#
# No license under any patent, copyright, trade secret or other intellectual
# property right is granted to or conferred upon you by disclosure or delivery
# of the Materials, either expressly, by implication, inducement, estoppel or
# otherwise. Any license under such intellectual property rights must be express
# and approved by Intel in writing.
#

import argparse
import os
from time import sleep
from threading import Thread

import grpc

from tensorflow_serving.apis import predict_pb2, prediction_service_pb2_grpc
from experiment_metrics.api import publish

progress = 0
max_progress = 1

if not os.getenv('RUN_NAME', None):
    raise RuntimeError('RUN_NAME env var must be set for publishing progress metrics!')


def do_batch_inference(server_address, input_dir_path, output_dir_path):
    detected_files = []

    for root, _, files in os.walk(input_dir_path):
        for name in files:
            detected_files.append(os.path.join(root, name))

    global max_progress
    max_progress = len(detected_files)

    channel = grpc.insecure_channel(server_address)
    stub = prediction_service_pb2_grpc.PredictionServiceStub(channel)

    for i, data_file in enumerate(detected_files, start=1):
        request = predict_pb2.PredictRequest()
        with open(data_file, mode='rb') as fi:
            pb_bytes = fi.read()

        try:
            request.ParseFromString(pb_bytes)
        except Exception as ex:
            raise RuntimeError(f"failed to parse {data_file}") from ex

        result = stub.Predict(request, timeout=30.0)  # timeout 30 seconds

        result_pb_serialized: bytes = result.SerializeToString()

        with open(f'{output_dir_path}/{os.path.basename(data_file)}.pb', mode='wb') as fi:
            fi.write(result_pb_serialized)

        global progress
        progress = i
        print(f'progress: {progress}/{max_progress}')


def publish_progress():
    progress_percent = 0
    while progress_percent != 100:
        new_progress_percent = progress/max_progress * 100

        if new_progress_percent != progress_percent:
            progress_percent = new_progress_percent

            metrics = {
                'progress': str(progress_percent)
            }
            publish(metrics)

        sleep(1)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--input_dir_path', type=str)
    parser.add_argument('--output_dir_path', type=str)

    args = parser.parse_args()

    if not args.input_dir_path:
        parser.error("'input_dir_path' is required!")

    input_dir_path = args.input_dir_path
    output_dir_path = args.output_dir_path if args.output_dir_path else '/mnt/output/experiment'

    progress_thread = Thread(target=publish_progress)
    progress_thread.start()

    do_batch_inference(server_address=os.getenv('TENSORFLOW_MODEL_SERVER_SVC_NAME', ''),
                       input_dir_path=input_dir_path,
                       output_dir_path=output_dir_path)

    progress_thread.join()

    # TODO: cleanup of k8s resources after inference


if __name__ == '__main__':
    main()
