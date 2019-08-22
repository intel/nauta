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

from keras.datasets import mnist
import sys
import numpy
import tensorflow

tensorflow.app.flags.DEFINE_string('image_id', '0', 'Image id from mnist.')
FLAGS = tensorflow.app.flags.FLAGS


def main(_):
    if len(sys.argv) < 1 or sys.argv[-1].startswith('-'):
        print('Usage: generate_json.py [--image_id=x]')

    (x_train, y_train), (x_test, y_test) = mnist.load_data()

    test_image = x_train[int(FLAGS.image_id)].reshape(784).astype(numpy.float32)
    test_image = numpy.multiply(test_image, 1.0 / 255.0)

    with open('input.json', 'w') as output:
        output.write('{"instances": [%s]}' % (test_image.tolist()))

    print("Input should be recognized as %d. Saving to input.json..." % y_train[int(FLAGS.image_id)])


if __name__ == '__main__':
    tensorflow.app.run()
