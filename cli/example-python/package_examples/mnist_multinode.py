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


import json
import argparse
import os
import time

import tensorflow as tf
from tensorflow.examples.tutorials.mnist import input_data

from experiment_metrics.api import publish


# Output produced by the experiment (summaries, checkpoints etc.) has to be placed in this folder.
EXPERIMENT_OUTPUT_PATH = "/mnt/output/experiment"

FLAGS = tf.app.flags.FLAGS

# Const names for input placeholder and main output node. They are needed for reference in graph restoration. More info
# is in the in-code comments.
INPUT_NAME = "images"
SCORES_NAME = "scores"

# Set of constant names related to served model.
# Look into example mnist conversion and checker scripts to see how these constants are used in TF Serving request
# creation.
# MODEL_NAME = "mnist" - Model name is not specified at this stage. It is given in "predict" commands as an argument.
MODEL_SIGNATURE_NAME = "predict_images"
MODEL_INPUT_NAME = "images"
MODEL_OUTPUT_NAME = "scores"


def parse_tf_config():
    tf_config = os.environ.get("TF_CONFIG")
    if not tf_config:
        raise RuntimeError("TF_CONFIG not set!")

    tf_config_json = json.loads(tf_config)

    cluster = tf_config_json.get("cluster")
    job_name = tf_config_json.get("task", {}).get("type")
    task_index = tf_config_json.get("task", {}).get("index")

    if job_name is None or task_index is None:
        raise RuntimeError("TF_CONFIG invalid!")

    allowed_job_names = ("ps", "worker")

    if job_name not in allowed_job_names:
        raise RuntimeError("bad job name: {job_name}, expected one of: {allowed_job_names}".
                           format(job_name=job_name, allowed_job_names=allowed_job_names))

    return cluster, job_name, task_index


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

    # Name scores op to be able to retrieve it later from saved meta graph.
    scores = tf.nn.softmax(logits, name=SCORES_NAME)

    predictions = tf.argmax(logits, axis=1)

    return logits, scores, predictions


def main(_):
    cluster, job_name, task_index = parse_tf_config()

    # Create a cluster from the parameter server and worker hosts.
    cluster_spec = tf.train.ClusterSpec(cluster)

    # Create and start a server for the local task.
    server = tf.train.Server(cluster_spec,
                             job_name=job_name,
                             task_index=task_index)

    if job_name == "ps":
        server.join()
        return

    # Assigns ops to the local worker by default.
    with tf.device(
        tf.train.replica_device_setter(
            worker_device="/job:worker/task:{task_index}".format(task_index=task_index),
            cluster=cluster
        )
    ):
        # Name images placeholder to be able to retrieve it from saved meta graph.
        images_placeholder = tf.placeholder(tf.float32, [None, 784], name=INPUT_NAME)

        dense_dropout_placeholder = tf.placeholder_with_default(1.0, [])
        labels_placeholder = tf.placeholder(tf.int64, [None])

        logits, scores, predictions = build_net(images_placeholder, dense_dropout_placeholder)

        loss = tf.losses.softmax_cross_entropy(tf.one_hot(labels_placeholder, 10), logits)
        global_step = tf.train.get_or_create_global_step()
        train = tf.train.AdamOptimizer().minimize(loss, global_step=global_step)
        accuracy = tf.reduce_mean(tf.cast(tf.equal(predictions, labels_placeholder), tf.float32))

        tf.summary.scalar("loss", loss)
        tf.summary.scalar("accuracy", accuracy)
        summary_op = tf.summary.merge_all()
        summary_writer = tf.summary.FileWriter(os.path.join(EXPERIMENT_OUTPUT_PATH, "tensorboard"))
        init_op = tf.initialize_all_variables()
        saver = tf.train.Saver()

    # Export meta graph to restore it later when saving.
    tf.train.export_meta_graph("graph.meta", as_text=True)

    is_chief = task_index == 0

    # Create a "supervisor", which oversees the training process.
    sv = tf.train.Supervisor(is_chief=(task_index == 0),
                             logdir=EXPERIMENT_OUTPUT_PATH,
                             init_op=init_op,
                             summary_op=summary_op,
                             saver=None,
                             global_step=global_step,
                             summary_writer=None)

    mnist = input_data.read_data_sets(FLAGS.data_dir)

    # The supervisor takes care of session initialization, restoring from
    # a checkpoint, and closing when done or an error occurs.
    with sv.managed_session(server.target) as sess:
        # Loop until the supervisor shuts down or 500 steps have completed.
        global_step_val = 0
        while not sv.should_stop() and global_step_val < 500:
            # Run a training step asynchronously.
            # See `tf.train.SyncReplicasOptimizer` for additional details on how to
            # perform *synchronous* training.
            images, labels = mnist.train.next_batch(64)
            _, loss_val, accuracy_val, global_step_val, summary_out = sess.run(
                [train, loss, accuracy, global_step, summary_op],
                feed_dict={images_placeholder: images,
                           labels_placeholder: labels,
                           dense_dropout_placeholder: 0.5})

            # Only chief publishes metrics.
            if is_chief:
                # Publish metrics just like in the single node example.
                publish({"loss": str(loss_val), "accuracy": str(accuracy_val), "global_step": str(global_step_val)})

            if global_step_val % 100 == 0:
                print("Step {}, Loss: {}, Accuracy: {}".format(global_step_val, loss_val, accuracy_val))
                saver.save(sess, os.path.join(EXPERIMENT_OUTPUT_PATH, "checkpoints", "model"),
                           global_step=global_step_val)

            if is_chief:
                summary_writer.add_summary(summary_out, global_step=global_step_val)

        # Save model by chief at the end.
        if is_chief:
            saver.save(sess, os.path.join(EXPERIMENT_OUTPUT_PATH, "checkpoints", "model"), global_step=global_step_val)

            tf.get_default_graph()._unsafe_unfinalize()

            builder = tf.saved_model.builder.SavedModelBuilder(
                os.path.join(EXPERIMENT_OUTPUT_PATH, "models", "00001"))

            prediction_signature = (
                tf.saved_model.signature_def_utils.build_signature_def(
                    inputs={MODEL_INPUT_NAME: tf.saved_model.utils.build_tensor_info(images_placeholder)},
                    outputs={MODEL_OUTPUT_NAME: tf.saved_model.utils.build_tensor_info(scores)},
                    method_name=tf.saved_model.signature_constants.PREDICT_METHOD_NAME))

            builder.add_meta_graph_and_variables(
                sess, [tf.saved_model.tag_constants.SERVING],
                signature_def_map={
                    MODEL_SIGNATURE_NAME:
                        prediction_signature
                },
                main_op=tf.tables_initializer(),
                clear_devices=True,
                strip_default_attrs=True)

            builder.save()

    # Model saving can hang whole multinode experiment when done at the end. Sleep to give chief time to save.
    time.sleep(30)

    # Ask for all the services to stop.
    sv.stop()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--data_dir", type=str,
                        default="./datasets/mnist",
                        help="Directory for storing input data")
    FLAGS, _ = parser.parse_known_args()
    tf.app.run()
