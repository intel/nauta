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

import tensorflow as tf
import numpy as np
from tensorflow_serving.apis import predict_pb2


tf.app.flags.DEFINE_string("work_dir", "/tmp/mnist_test", "Working directory.")
tf.app.flags.DEFINE_integer("num_tests", 100, "Number of examples to convert.")

FLAGS = tf.app.flags.FLAGS

# Set of constant names related to served model.
# Look into example training scripts to see how these constants are used in model saving.
MODEL_NAME = "mnist"
MODEL_SIGNATURE_NAME = "predict_images"
MODEL_INPUT_NAME = "images"
# MODEL_OUTPUT_NAME = "scores" - not needed here as we only specify requests


def do_conversion(work_dir, num_tests):
    """
    Converts requested number of examples from mnist test set to proto buffer format. Results are saved in a
    conversion_out subdir of workdir.

    Args:
        work_dir: The full path of working directory for test data set.
        num_tests: Number of test images to convert.

    Raises:
        IOError: An error occurred processing test data set.
    """
    conversion_out_path = os.path.join(work_dir, "conversion_out")
    os.makedirs(conversion_out_path, exist_ok=True)

    test_data_set = tf.contrib.learn.datasets.mnist.read_data_sets(work_dir).test
    expected_labels = []

    for i in range(num_tests):
        request = predict_pb2.PredictRequest()
        request.model_spec.name = MODEL_NAME
        request.model_spec.signature_name = MODEL_SIGNATURE_NAME
        image, label = test_data_set.next_batch(1)
        request.inputs[MODEL_INPUT_NAME].CopyFrom(
            tf.contrib.util.make_tensor_proto(image[0], shape=[1, image[0].size])
        )
        ser = request.SerializeToString()
        expected_labels.append(label)

        with open(os.path.join(conversion_out_path, "{}.pb".format(i)), mode='wb') as file:
            file.write(ser)

    expected_labels = np.array(expected_labels)
    np.save(os.path.join(work_dir, "labels"), expected_labels)


def main(_):
    if FLAGS.num_tests > 10000:
        print('num_tests should not be greater than 10k')
        return

    do_conversion(FLAGS.work_dir, FLAGS.num_tests)


if __name__ == '__main__':
    tf.app.run()
