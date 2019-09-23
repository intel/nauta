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

import warnings
warnings.filterwarnings('ignore', category=FutureWarning)
import sys
import threading
import os
import numpy as np
import tensorflow as tf

from tensorflow_serving.apis import predict_pb2


tf.app.flags.DEFINE_integer("concurrency", 1,
                            "maximum number of concurrent inference requests")
tf.app.flags.DEFINE_integer("num_tests", 100, "Number of test images")
tf.app.flags.DEFINE_string("work_dir", "/tmp/mnist_test", "Working directory.")
tf.app.flags.DEFINE_string("input_dir", "/tmp/mnist_test/conversion_out",
                           "Directory which contains results of inference - files 0.pb etc.")

FLAGS = tf.app.flags.FLAGS

# Set of constant names related to served model.
# Look into example mnist conversion and checker scripts to see how these constants are used in TF Serving request
# creation.
# MODEL_NAME = "mnist" - Model name is not specified at this stage. It was already given in request creation
# (conversion stage).
# MODEL_SIGNATURE_NAME = "predict_images" - Not used. Already contained in pb request.
# MODEL_INPUT_NAME = "images" - Not used. Already contained in pb request.
MODEL_OUTPUT_NAME = "scores"


class _ResultCounter(object):
    """Counter for the prediction results."""

    def __init__(self, num_tests, concurrency):
        self._num_tests = num_tests
        self._concurrency = concurrency
        self._error = 0
        self._done = 0
        self._active = 0
        self._condition = threading.Condition()

    def inc_error(self):
        with self._condition:
            self._error += 1

    def inc_done(self):
        with self._condition:
            self._done += 1
            self._condition.notify()

    def dec_active(self):
        with self._condition:
            self._active -= 1
            self._condition.notify()

    def get_error_rate(self):
        with self._condition:
            while self._done != self._num_tests:
                self._condition.wait()
            return self._error / float(self._num_tests)

    def throttle(self):
        with self._condition:
            while self._active == self._concurrency:
                self._condition.wait()
            self._active += 1


def _create_rpc_callback(label, result_counter):
    """
    Creates RPC callback function.

    Args:
        label: The correct label for the predicted example.
        result_counter: Counter for the prediction result.

    Returns:
        The callback function.
    """

    def _callback(result_future):
        """
        Callback function.

        Calculates the statistics for the prediction result.

        Args:
            result_future: Result future of the RPC.
        """
        sys.stdout.write(".")
        sys.stdout.flush()

        response = np.array(result_future.result().outputs[MODEL_OUTPUT_NAME].float_val)
        prediction = np.argmax(response)
        if label != prediction:
            result_counter.inc_error()
        result_counter.inc_done()
        result_counter.dec_active()

    return _callback


def do_inference(work_dir, concurrency, num_tests, input_dir):
    """
    Tests PredictionService with concurrent requests.

    Args:
        work_dir: The full path of working directory for test data set.
        concurrency: Maximum number of concurrent requests.
        num_tests: Number of test images to use.
        input_dir: Path to dir which contains prediction results.

    Returns:
        The classification error rate.

    Raises:
        IOError: An error occurred processing test data set.
    """
    expected_labels = np.load(os.path.join(work_dir, "labels.npy"))
    result_counter = _ResultCounter(num_tests, concurrency)
    for i in range(num_tests):
        result_counter.throttle()

        sys.stdout.write(".")
        sys.stdout.flush()

        with open(os.path.join(input_dir, "{}.pb".format(i)), mode="rb") as pb_file:
            result_pb = pb_file.read()

        resp = predict_pb2.PredictResponse()

        resp.ParseFromString(result_pb)

        response = np.array(resp.outputs[MODEL_OUTPUT_NAME].float_val)
        prediction = np.argmax(response)

        if expected_labels[i] != prediction:
            result_counter.inc_error()
        result_counter.inc_done()
        result_counter.dec_active()

    return result_counter.get_error_rate()


def main(_):
    if FLAGS.num_tests > 10000:
        print("num_tests should not be greater than 10k")
        return

    error_rate = do_inference(FLAGS.work_dir, FLAGS.concurrency, FLAGS.num_tests, FLAGS.input_dir)
    print("\nInference error rate: {}".format((error_rate * 100)))


if __name__ == "__main__":
    tf.compat.v1.app.run()
