# BSD 3-Clause License

# Copyright (c) 2019, Frederik Kratzert. Intel Corporation.
# All rights reserved.

# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:

# * Redistributions of source code must retain the above copyright notice, this
#   list of conditions and the following disclaimer.

# * Redistributions in binary form must reproduce the above copyright notice,
#   this list of conditions and the following disclaimer in the documentation
#   and/or other materials provided with the distribution.

# * Neither the name of the copyright holder nor the names of its
#   contributors may be used to endorse or promote products derived from
#   this software without specific prior written permission.

# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
import argparse
import os
import sys
import time

import tensorflow as tf
import tensorflow.contrib.keras as keras

from alexnet_model import AlexNet


# version number of the model
MODEL_VERSION = 1

FLAGS = None


def create_generator(path_train, path_val, batch_size=128):
    datagen = keras.preprocessing.image.ImageDataGenerator(data_format='channels_last')
    train_generator = datagen.flow_from_directory(path_train,
                                                  target_size=(227, 227),
                                                  batch_size=batch_size,
                                                  class_mode='categorical')

    validation_generator = datagen.flow_from_directory(path_val,
                                                       target_size=(227, 227),
                                                       batch_size=batch_size,
                                                       class_mode='categorical')
    return train_generator, validation_generator


def main(_):
    # here we train and validate the model
    if len(sys.argv) < 2:
        print('Example usage: alexnet.py [--training_epoch=20] '
              '[--data_dir=/data/dir] [--export_dir=/output/dir]')
        sys.exit(-1)

    if FLAGS.training_epoch <= 0:
        print('Please specify a positive value for training iteration.')
        sys.exit(-1)

    if FLAGS.batch_size <= 0:
        print('Please specify a positive value for batch size.')
        sys.exit(-1)

    batch_size = FLAGS.batch_size

    print('Loading data...')
    training, testing = create_generator(os.path.join(FLAGS.data_dir, 'i1k-extracted/train'),
                                         os.path.join(FLAGS.data_dir, 'i1k-extracted/val'),
                                         batch_size=batch_size)

    print('Data loaded!')

    display_step = 20
    train_size = training.samples
    n_classes = training.num_classes
    image_size = 227
    img_channel = 3
    num_epochs = FLAGS.training_epoch

    x_flat = tf.placeholder(tf.float32,
                            (None, image_size * image_size * img_channel))
    x_3d = tf.reshape(x_flat, shape=(tf.shape(x_flat)[0], image_size,
                                     image_size, img_channel))
    y = tf.placeholder(tf.float32, [None, n_classes])

    keep_prob = tf.placeholder(tf.float32)

    model = AlexNet(x_3d, keep_prob=keep_prob, num_classes=n_classes)
    model_train = model.fc8
    model_prediction = tf.nn.softmax(model_train)

    cost = tf.reduce_mean(
        tf.nn.softmax_cross_entropy_with_logits(logits=model_train, labels=y))
    global_step = tf.Variable(0, trainable=False, name='global_step')

    lr = tf.train.exponential_decay(0.01, global_step, 100000, 0.1, staircase=True)

    optimizer = tf.train.MomentumOptimizer(learning_rate=lr, momentum=0.9).minimize(cost, global_step=global_step)

    accuracy, update_op = tf.metrics.accuracy(labels=tf.argmax(y, 1), predictions=tf.argmax(model_prediction, 1))

    test_accuracy, test_update_op = tf.metrics.accuracy(labels=tf.argmax(y, 1),
                                                        predictions=tf.argmax(model_prediction, 1))

    start_time = time.time()
    print("Start time is: {}".format(str(start_time)))

    with tf.Session() as sess:
        tf.global_variables_initializer().run()
        tf.local_variables_initializer().run()

        for step in range(int(num_epochs * train_size) // batch_size):

            batch_xs, batch_ys = training.next()

            sess.run(optimizer, feed_dict={x_3d: batch_xs, y: batch_ys, keep_prob: 0.5})
            sess.run(lr)
            if step % display_step == 0:
                acc_up = sess.run([accuracy, update_op],
                                  feed_dict={x_3d: batch_xs, y: batch_ys, keep_prob: 1.})
                acc = sess.run(accuracy,
                               feed_dict={x_3d: batch_xs, y: batch_ys, keep_prob: 1.})
                loss = sess.run(cost, feed_dict={x_3d: batch_xs, y: batch_ys, keep_prob: 1.})
                elapsed_time = time.time() - start_time
                print(" Iter " + str(step) + ", Minibatch Loss= " + "{:.6f}".format(loss) +
                      ", Training Accuracy= " + "{}".format(acc) + " Elapsed time:" + str(elapsed_time))

        stop_time = time.time()
        print("Optimization Finished!")
        print("Training took: {}".format(stop_time-start_time))

        step_test = 1
        acc_list = []

        while step_test * batch_size < testing.samples:
            testing_xs, testing_ys = testing.next()
            acc_up = sess.run([test_accuracy, test_update_op],
                              feed_dict={x_3d: testing_xs, y: testing_ys, keep_prob: 1.})
            acc = sess.run([test_accuracy],
                           feed_dict={x_3d: testing_xs, y: testing_ys, keep_prob: 1.})
            acc_list.extend(acc)
            step_test += 1

        # save model using SavedModelBuilder from TF
        export_path_base = FLAGS.export_dir
        export_path = os.path.join(
            tf.compat.as_bytes(export_path_base),
            tf.compat.as_bytes(str(MODEL_VERSION)))

        print('Exporting trained model to', export_path)
        builder = tf.saved_model.builder.SavedModelBuilder(export_path)

        tensor_info_x = tf.saved_model.utils.build_tensor_info(x_flat)
        tensor_info_y = tf.saved_model.utils.build_tensor_info(model_train)

        prediction_signature = (
            tf.saved_model.signature_def_utils.build_signature_def(
                inputs={'images': tensor_info_x},
                outputs={'scores': tensor_info_y},
                method_name=tf.saved_model.signature_constants.PREDICT_METHOD_NAME))

        legacy_init_op = tf.group(tf.tables_initializer(),
                                  name='legacy_init_op')
        builder.add_meta_graph_and_variables(
            sess, [tf.saved_model.tag_constants.SERVING],
            signature_def_map={
                'predict_images':
                    prediction_signature,
            },
            legacy_init_op=legacy_init_op)

        builder.save()

        print('Done exporting!')
        print("Max batch accuracy is", max(acc_list))
        print("Min batch accuracy is", min(acc_list))
        print("Avg. accuracy:", sum(acc_list) / len(acc_list))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--data_dir", type=str,
                        default="./dataset/imagenet",
                        help="Directory which contains dataset")
    parser.add_argument("--training_epoch", type=int,
                        default=1,
                        help="Number of training epochs")
    parser.add_argument("--batch_size", type=int,
                        default=128,
                        help="Size of image batches")
    parser.add_argument("--export_dir", type=str,
                        default="./output",
                        help="Export directory for model")
    FLAGS, _ = parser.parse_known_args()
    tf.app.run()
