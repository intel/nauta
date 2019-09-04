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
import warnings
warnings.filterwarnings('ignore', category=FutureWarning)
import argparse
import os

import tensorflow as tf

from experiment_metrics.api import publish


# Output produced by the experiment (summaries, checkpoints etc.) has to be placed in this folder.
EXPERIMENT_OUTPUT_PATH = "/mnt/output/experiment"
MODEL_VERSION = 1

FLAGS = None

# Set of constant names related to served model.
# Look into example mnist conversion and checker scripts to see how these constants are used in TF Serving request
# creation.
# MODEL_NAME = "mnist" - Model name is not specified at this stage. It is given in "predict" commands as an argument.
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

    # As previously mentioned summaries are saved to EXPERIMNET_OUTPUT_PATH which makes them accessible by user and
    # tensorboard.
    summary_writer = tf.summary.FileWriter(os.path.join(EXPERIMENT_OUTPUT_PATH, "tensorboard"))

    session = tf.Session()
    session.run(tf.global_variables_initializer())

    saver = tf.train.Saver()

    for i in range(FLAGS.steps):
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

        # Example of nauta metrics usage. Simply construct dict of keys and string values that you want to bind with
        # them and call publish. Old values of the same key will be overwritten.
        publish({"global_step": str(i), "loss": str(loss_val), "accuracy": str(accuracy_val)})

    # Validate trained model on MNIST validation set.
    validation_accuracy_val = session.run(
        accuracy,
        feed_dict={images_placeholder: mnist.validation.images,
                   labels_placeholder: mnist.validation.labels}
    )
    print("Validation accuracy: {}".format(validation_accuracy_val))

    # As previously mentioned checkpoints are saved to EXPERIMNET_OUTPUT_PATH which makes them accessible by user.
    saver.save(session, os.path.join(EXPERIMENT_OUTPUT_PATH, "checkpoints", "model.ckpt"))

    # Publish validation accuracy the same way as before.
    publish({"validation_accuracy": str(validation_accuracy_val)})

    # Save servable model to EXPERIMENT_OUTPUT_PATH to make it accessible to the user.
    if FLAGS.export_dir is not "":
        export_dir = os.path.join(FLAGS.export_dir, str(MODEL_VERSION))
        builder = tf.saved_model.builder.SavedModelBuilder(export_dir)

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
                        help="Directory which contains dataset")
    parser.add_argument("--export_dir", type=str,
                        default="",
                        help="Export directory for model")
    parser.add_argument("--steps", type=int,
                        default=500,
                        help="Number of steps to run training")
    FLAGS, _ = parser.parse_known_args()
    tf.app.run()
