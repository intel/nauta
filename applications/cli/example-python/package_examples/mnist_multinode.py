# Copyright 2019 The TensorFlow Authors, Intel Corporation. All Rights Reserved.
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


import json
import argparse
import os
import time

import tensorflow as tf
from tensorflow.examples.tutorials.mnist import input_data

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
MODEL_SIGNATURE_NAME = "predict_images"
MODEL_INPUT_NAME = "images"
MODEL_OUTPUT_NAME = "scores"
MODEL_VERSION = 1


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
    """ Build example mnist conv net. """
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

def convert_to_session(session):
    while type(session).__name__ != 'Session':
        session = session._sess
    return session

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
        accuracy = tf.reduce_mean(tf.cast(tf.equal(predictions, labels_placeholder), tf.float32))

        tf.summary.scalar("loss", loss)
        tf.summary.scalar("accuracy", accuracy)
        tf.summary.merge_all()

        # As mentioned above summaries will be saved to EXPERIMENT_OUTPUT_PATH so that they can be automatically
        # discovered by tensorboard.
        summary_dir = os.path.join(EXPERIMENT_OUTPUT_PATH, "tensorboard")

        # These ops will be later needed to save servable model.
        tf.global_variables_initializer()
        saver = tf.train.Saver()

    # Export meta graph to restore it later when saving.
    tf.train.export_meta_graph("graph.meta", as_text=True)

    is_chief = task_index == 0

    train_op = tf.train.AdagradOptimizer(0.01).minimize(
        loss, global_step=global_step)
    hooks = [tf.train.StopAtStepHook(last_step=10000)]

    # Read/download dataset locally.
    mnist = input_data.read_data_sets(FLAGS.data_dir)

    with tf.train.MonitoredTrainingSession(master=server.target,
                                           is_chief=(task_index == 0),
                                           hooks=hooks,
                                           summary_dir=summary_dir) as mon_sess:


        step = 0
        while not mon_sess.should_stop() and step < 500:
            batch_xs, batch_ys = mnist.train.next_batch(FLAGS.batch_size)
            train_feed = {images_placeholder: batch_xs, labels_placeholder: batch_ys}

            _, step, accuracy_val = mon_sess.run([train_op, global_step, accuracy], feed_dict=train_feed)
            if step % 100 == 0:
                print("Done step %d" % step)
                print("Accuracy {}".format(accuracy_val))

            # Save model by chief at the end.

        session = convert_to_session(mon_sess)
        if is_chief:
            saver.save(session, os.path.join(EXPERIMENT_OUTPUT_PATH, "checkpoints", "model"), global_step=step)

            # Unfinalize the graph as distributed training process already finalized it and we
            tf.get_default_graph()._unsafe_unfinalize()

            # Save servable model to EXPERIMENT_OUTPUT_PATH to make it accessible to the user.
            export_path = os.path.join(EXPERIMENT_OUTPUT_PATH, str(MODEL_VERSION))
            print('Exporting trained model to', export_path)
            builder = tf.saved_model.builder.SavedModelBuilder(export_path)

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
                clear_devices=True,
                strip_default_attrs=True)

            builder.save()

    # Model saving can hang whole multinode experiment when done at the end. Sleep to give chief time to save.
    time.sleep(30)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--data_dir", type=str,
                        default="./datasets/mnist",
                        help="Directory which contains dataset")
    parser.add_argument("--batch_size", type=int,
                        default=100,
                        help="Training batch size")
    FLAGS, _ = parser.parse_known_args()
    tf.app.run()
