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

import tensorflow as tf

from experiment_metrics.api import publish


# Output produced by the experiment (summaries, checkpoints etc.) has to be placed in this folder.
EXPERIMENT_OUTPUT_PATH = "/mnt/output/experiment"

FLAGS = None

# Set of constant names related to served model.
# Look into example mnist conversion and checker scripts to see how these constants are used in TF Serving request
# creation.
# MODEL_NAME = "mnist" - Model name is not specified at this stage. It is given in "predict" commands as an argument.
MODEL_SIGNATURE_NAME = "predict_images"
MODEL_INPUT_NAME = "images"
MODEL_OUTPUT_NAME = "scores"


def build_net(images_placeholder, dense_dropout_placeholder):
    images_input = tf.reshape(images_placeholder, [-1, 28, 28, 1])

    conv_1 = tf.layers.conv2d(images_input, filters=32, kernel_size=5, activation=tf.nn.relu, padding="same")
    pool_1 = tf.layers.max_pooling2d(conv_1, pool_size=[2, 2], strides=[2, 2], padding="same")

    conv_2 = tf.layers.conv2d(pool_1, filters=64, kernel_size=5, activation=tf.nn.relu, padding="same")
    pool_2 = tf.layers.max_pooling2d(conv_2, pool_size=[2, 2], strides=[2, 2], padding="same")

    dense_input = tf.reshape(pool_2, [-1, 7 * 7 * 64])
    dense_1 = tf.layers.dense(dense_input, 1024, activation=tf.nn.relu)
    dense_1_drop = tf.nn.dropout(dense_1, dense_dropout_placeholder)

    logits = tf.layers.dense(dense_1_drop, 10)
    logits = tf.identity(logits)
    scores = tf.nn.softmax(logits)
    predictions = tf.argmax(logits, axis=1)

    return logits, scores, predictions


def main(_):
    mnist = tf.contrib.learn.datasets.mnist.read_data_sets(FLAGS.data_dir)

    images_placeholder = tf.placeholder(tf.float32, [None, 784])
    dense_dropout_placeholder = tf.placeholder_with_default(1.0, [])
    labels_placeholder = tf.placeholder(tf.int64, [None])

    logits, scores, predictions = build_net(images_placeholder, dense_dropout_placeholder)

    loss = tf.losses.softmax_cross_entropy(tf.one_hot(labels_placeholder, 10), logits)
    train = tf.train.AdamOptimizer().minimize(loss)
    accuracy = tf.reduce_mean(tf.cast(tf.equal(predictions, labels_placeholder), tf.float32))

    tf.summary.scalar("loss", loss)
    tf.summary.scalar("accuracy", accuracy)
    summary_op = tf.summary.merge_all()
    summary_writer = tf.summary.FileWriter(os.path.join(EXPERIMENT_OUTPUT_PATH, "tensorboard"))

    session = tf.Session()
    session.run(tf.global_variables_initializer())

    saver = tf.train.Saver()

    for i in range(500):
        images, labels = mnist.train.next_batch(64)
        _, summary_out, loss_val, accuracy_val = session.run(
            [train, summary_op, loss, accuracy],
            feed_dict={images_placeholder: images,
                       labels_placeholder: labels,
                       dense_dropout_placeholder: 0.5}
        )

        if i % 100 == 0:
            print("Step {}, Loss: {}, Accuracy: {}".format(i, loss_val, accuracy_val))

        summary_writer.add_summary(summary_out, global_step=i)

        # Example of dls4e metrics usage. Simply construct dict of keys and string values that you want to bind with
        # them and call publish. Old values of the same key will be overwritten.
        publish({"global_step": str(i), "loss": str(loss_val), "accuracy": str(accuracy_val)})

    validation_accuracy_val = session.run(
        accuracy,
        feed_dict={images_placeholder: mnist.validation.images,
                   labels_placeholder: mnist.validation.labels}
    )
    print("Validation accuracy: {}".format(validation_accuracy_val))
    saver.save(session, os.path.join(EXPERIMENT_OUTPUT_PATH, "checkpoints", "model.ckpt"))

    # Publish validation accuracy the same way as before.
    publish({"validation_accuracy": str(validation_accuracy_val)})

    builder = tf.saved_model.builder.SavedModelBuilder(os.path.join(EXPERIMENT_OUTPUT_PATH, "models", "00001"))

    prediction_signature = (
        tf.saved_model.signature_def_utils.build_signature_def(
            inputs={MODEL_INPUT_NAME: tf.saved_model.utils.build_tensor_info(images_placeholder)},
            outputs={MODEL_OUTPUT_NAME: tf.saved_model.utils.build_tensor_info(scores)},
            method_name=tf.saved_model.signature_constants.PREDICT_METHOD_NAME))

    builder.add_meta_graph_and_variables(
        session, [tf.saved_model.tag_constants.SERVING],
        signature_def_map={
            MODEL_SIGNATURE_NAME:
                prediction_signature
        },
        main_op=tf.tables_initializer(),
        strip_default_attrs=True)

    builder.save()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--data_dir", type=str,
                        default="/tmp/mnist-data",
                        help="Directory for storing input data")
    FLAGS, _ = parser.parse_known_args()
    tf.app.run()
