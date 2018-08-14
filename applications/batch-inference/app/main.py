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

import os

import grpc

from tensorflow_serving.apis import predict_pb2, prediction_service_pb2


def do_batch_inference(server_address, input_dir_path, output_dir_path):
    detected_files = []

    for root, _, files in os.walk(input_dir_path):
        for name in files:
            detected_files.append(os.path.join(root, name))

    len_detected_files = len(detected_files)

    channel = grpc.insecure_channel(server_address)
    stub = prediction_service_pb2.PredictionServiceStub(channel)

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

        print(f'progress: {i}/{len_detected_files}')


def main():
    # TODO: parametrize input_dir_path, output_dir_path from dlsctl predict command
    do_batch_inference(server_address=os.getenv('TENSORFLOW_MODEL_SERVER_SVC_NAME', ''),
                       input_dir_path='/mnt/input/home/data',
                       output_dir_path='/mnt/output/experiment')

    # TODO: cleanup of k8s resources after inference


if __name__ == '__main__':
    main()
