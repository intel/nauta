# Copyright 2016 Google Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================


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
