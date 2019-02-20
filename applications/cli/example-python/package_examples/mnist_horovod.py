
# Copyright 2019 Uber Technologies, Inc. Intel Corporation. All Rights Reserved.
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
import argparse

import tensorflow as tf
import horovod.tensorflow as hvd

from experiment_metrics.api import publish

layers = tf.contrib.layers
learn = tf.contrib.learn

# Output produced by the experiment (summaries, checkpoints etc.) has to be placed in this folder.
EXPERIMENT_OUTPUT_PATH = "/mnt/output/experiment"
FILENAMES = ('train-images-idx3-ubyte.gz', 'train-labels-idx1-ubyte.gz',
             't10k-images-idx3-ubyte.gz', 't10k-labels-idx1-ubyte.gz')

# Const names for input placeholder and main output node. They are needed for reference in graph restoration. More info
# is in the in-code comments.
INPUT_NAME = "images"
SCORES_NAME = "scores"

tf.logging.set_verbosity(tf.logging.INFO)

# Set of constant names related to served model.
# Look into example mnist conversion and checker scripts to see how these constants are used in TF Serving request
# creation.
MODEL_SIGNATURE_NAME = "predict_images"
MODEL_INPUT_NAME = "images"
MODEL_OUTPUT_NAME = "scores"


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


def main(_):

    # Horovod: initialize Horovod.
    hvd.init()
    hvd_size = hvd.size()
    print("hvd size: {}".format(hvd_size))

    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--data_dir',
        type=str,
        default='/tensorflow/mnist/',
        help='Directory which contains dataset')
    parser.add_argument(
        '--steps',
        type=int,
        default=100,
        help='steps')

    FLAGS, _ = parser.parse_known_args()

    # Ensure data directory passed to the script contains proper dataset
    dir_content = os.listdir(FLAGS.data_dir)
    for file in FILENAMES:
        if file not in dir_content:
            print("Directory provided by user does not contains proper dataset")
            FLAGS.data_dir = os.path.join(FLAGS.data_dir, "input_data_{}".format(hvd.rank()))
            break

    # Read/download local dataset. Different copy for each process.
    mnist = learn.datasets.mnist.read_data_sets(FLAGS.data_dir)

    # Name images placeholder to be able to retrieve it from saved meta graph.
    images_placeholder = tf.placeholder(tf.float32, [None, 784], name=INPUT_NAME)

    dense_dropout_placeholder = tf.placeholder_with_default(1.0, [])
    labels_placeholder = tf.placeholder(tf.int64, [None])
    logits, scores, predictions = build_net(images_placeholder, dense_dropout_placeholder)

    # Exporting meta graph right now takes care of removing Horovod specific ops before serving. Graph right now
    # also does not contain any training specific ops, so it is optimized for serving too.
    tf.train.export_meta_graph("graph.meta", as_text=True)

    loss = tf.losses.softmax_cross_entropy(tf.one_hot(labels_placeholder, 10), logits)
    accuracy = tf.reduce_mean(tf.cast(tf.equal(predictions, labels_placeholder), tf.float32))

    # Define summary ops to save summaries for later use in tensorboard.
    tf.summary.scalar("accuracy", accuracy)
    tf.summary.scalar("loss", loss)
    summary_op = tf.summary.merge_all()

    # Horovod: adjust learning rate based on number of workers.
    optimizer = tf.train.RMSPropOptimizer(0.001 * hvd.size())

    global_step = tf.contrib.framework.get_or_create_global_step()

    # Wrap standard optimizer in Horovod distributed one.
    train = hvd.DistributedOptimizer(optimizer).minimize(loss, global_step=global_step)

    hooks = [
        # Horovod: BroadcastGlobalVariablesHook broadcasts initial variable states
        # from rank 0 to all other processes. This is necessary to ensure consistent
        # initialization of all workers when training is started with random weights
        # or restored from a checkpoint.
        hvd.BroadcastGlobalVariablesHook(0),

        # Horovod: adjust number of steps based on number of workers.
        tf.train.StopAtStepHook(FLAGS.steps // hvd_size),

        tf.train.LoggingTensorHook(tensors={'step': global_step, 'loss': loss},
                                   every_n_iter=10),
    ]

    # Only master saves summaries.
    if hvd.rank() == 0:
        hooks += [
            # As previously mentioned summaries are saved to EXPERIMENT_OUTPUT_PATH so that they can be discovered by
            # tensorboard.
            tf.train.SummarySaverHook(save_steps=1, output_dir=os.path.join(EXPERIMENT_OUTPUT_PATH, "tensorboard"),
                                      summary_op=summary_op)]

    # Horovod: save checkpoints only on worker 0 to prevent other workers from corrupting them. As previously mentioned
    # checkpoints are saved to EXPERIMNET_OUTPUT_PATH which makes them accessible by user.
    checkpoint_dir = os.path.join(EXPERIMENT_OUTPUT_PATH, "checkpoints") if hvd.rank() == 0 else None

    # The MonitoredTrainingSession takes care of session initialization,
    # restoring from a checkpoint, saving to a checkpoint, and closing when done
    # or an error occurs.
    with tf.train.MonitoredTrainingSession(checkpoint_dir=checkpoint_dir, hooks=hooks) as mon_sess:
        while not mon_sess.should_stop():
            images, labels = mnist.train.next_batch(64)
            _, loss_val, accuracy_val, global_step_val = mon_sess.run(
                [train, loss, accuracy, global_step],
                feed_dict={images_placeholder: images,
                           labels_placeholder: labels,
                           dense_dropout_placeholder: 0.5})

            # Only master publishes metrics.
            if hvd.rank() == 0:
                # Publish metrics just like in the single node example.
                publish({"loss": str(loss_val), "accuracy": str(accuracy_val), "global_step": str(global_step_val)})

    # Save servable model only from Horovod master.
    if hvd.rank() == 0:
        # Create a new graph to import the previously exported one.
        with tf.Graph().as_default():
            # Import previously saved meta graph.
            restorer = tf.train.import_meta_graph("graph.meta")
            with tf.Session() as session:
                checkpoint_file = tf.train.latest_checkpoint(checkpoint_dir)
                restorer.restore(session, checkpoint_file)

                # Get handlers for images placeholder and scores op with names defined before.
                images_placeholder = tf.get_default_graph().get_tensor_by_name(INPUT_NAME + ":0")
                scores = tf.get_default_graph().get_tensor_by_name(SCORES_NAME + ":0")

                # Save servable model to EXPERIMENT_OUTPUT_PATH to make it accessible to the user.
                builder = tf.saved_model.builder.SavedModelBuilder(
                    os.path.join(EXPERIMENT_OUTPUT_PATH, "1"))

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
    tf.app.run()
