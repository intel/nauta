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

import json
import math
import os

import tensorflow as tf
from tensorflow.examples.tutorials.mnist import input_data

# noinspection PyUnresolvedReferences
tf.app.flags.DEFINE_integer("hidden_units", 100,
                            "Number of units in the hidden layer of the NN")
# noinspection PyUnresolvedReferences
tf.app.flags.DEFINE_string("data_dir", "/tmp/mnist-data",
                           "Directory for storing mnist data")
# noinspection PyUnresolvedReferences
tf.app.flags.DEFINE_integer("batch_size", 100, "Training batch size")

# noinspection PyUnresolvedReferences
FLAGS = tf.app.flags.FLAGS

IMAGE_PIXELS = 28


def parse_tf_config():
    tf_config = os.environ.get('TF_CONFIG')
    if not tf_config:
        raise RuntimeError('TF_CONFIG not set!')

    tf_config_json = json.loads(tf_config)

    cluster = tf_config_json.get('cluster')
    job_name = tf_config_json.get('task', {}).get('type')
    task_index = tf_config_json.get('task', {}).get('index')

    if job_name is None or task_index is None:
        raise RuntimeError('TF_CONFIG invalid!')

    allowed_job_names = ('ps', 'worker')

    if job_name not in allowed_job_names:
        raise RuntimeError('bad job name: {job_name}, expected one of: {allowed_job_names}'.
                           format(job_name=job_name, allowed_job_names=allowed_job_names))

    return cluster, job_name, task_index


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
    with tf.device(tf.train.replica_device_setter(
            worker_device="/job:worker/task:{task_index}".format(task_index=task_index),
            cluster=cluster)):

        # Variables of the hidden layer
        hid_w = tf.Variable(
            tf.truncated_normal([IMAGE_PIXELS * IMAGE_PIXELS, FLAGS.hidden_units],
                                stddev=1.0 / IMAGE_PIXELS), name="hid_w")
        hid_b = tf.Variable(tf.zeros([FLAGS.hidden_units]), name="hid_b")

        # Variables of the softmax layer
        sm_w = tf.Variable(
            tf.truncated_normal([FLAGS.hidden_units, 10],
                                stddev=1.0 / math.sqrt(FLAGS.hidden_units)),
            name="sm_w")
        sm_b = tf.Variable(tf.zeros([10]), name="sm_b")

        x = tf.placeholder(tf.float32, [None, IMAGE_PIXELS * IMAGE_PIXELS])
        y_ = tf.placeholder(tf.float32, [None, 10])

        hid_lin = tf.nn.xw_plus_b(x, hid_w, hid_b)
        hid = tf.nn.relu(hid_lin)

        y = tf.nn.softmax(tf.nn.xw_plus_b(hid, sm_w, sm_b))
        loss = -tf.reduce_sum(y_ * tf.log(tf.clip_by_value(y, 1e-10, 1.0)))

        global_step = tf.Variable(0)

        train_op = tf.train.AdagradOptimizer(0.01).minimize(
            loss, global_step=global_step)

        saver = tf.train.Saver()
        summary_op = tf.summary.merge_all()
        init_op = tf.initialize_all_variables()

    # Create a "supervisor", which oversees the training process.
    sv = tf.train.Supervisor(is_chief=(task_index == 0),
                             logdir="/tmp/train_logs",
                             init_op=init_op,
                             summary_op=summary_op,
                             saver=saver,
                             global_step=global_step,
                             save_model_secs=600)

    mnist = input_data.read_data_sets(FLAGS.data_dir, one_hot=True)

    # The supervisor takes care of session initialization, restoring from
    # a checkpoint, and closing when done or an error occurs.
    with sv.managed_session(server.target) as sess:
        # Loop until the supervisor shuts down or 1000000 steps have completed.
        step = 0
        while not sv.should_stop() and step < 10000:
            # Run a training step asynchronously.
            # See `tf.train.SyncReplicasOptimizer` for additional details on how to
            # perform *synchronous* training.

            batch_xs, batch_ys = mnist.train.next_batch(FLAGS.batch_size)
            train_feed = {x: batch_xs, y_: batch_ys}

            _, step = sess.run([train_op, global_step], feed_dict=train_feed)
            if step % 100 == 0:
                print("Done step %d" % step)

    # Ask for all the services to stop.
    sv.stop()


if __name__ == "__main__":
    tf.app.run()
