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
import os
import sys
import tensorflow as tf


def _bytes_feature(value):
    return tf.train.Feature(bytes_list=tf.train.BytesList(value=[value]))


parser = argparse.ArgumentParser()
parser.add_argument('--input_dir', type=str, required=True)
parser.add_argument('--output_file', type=str, required=True)

args = parser.parse_args()

files_to_convert = []

for root, _, files in os.walk(args.input_dir):
    for name in files:
        files_to_convert.append(os.path.join(root, name))

with tf.python_io.TFRecordWriter(args.output_file) as writer:
    for filename in files_to_convert:
        with open(filename, mode='rb') as fi:
            pb_bytes = fi.read()

        example = tf.train.Example(features=tf.train.Features(feature={
        'data_pb': _bytes_feature(pb_bytes),
        'label': _bytes_feature(bytes(os.path.basename(filename), 'utf_8'))}))

        writer.write(example.SerializeToString())
