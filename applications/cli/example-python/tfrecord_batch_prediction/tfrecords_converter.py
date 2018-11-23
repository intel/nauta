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
