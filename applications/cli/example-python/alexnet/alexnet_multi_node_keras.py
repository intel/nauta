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

import os
import time

import tensorflow as tf
import tensorflow.contrib.keras as keras
from tensorflow.python.framework.errors_impl import UnavailableError

#========== MULTI NODE CONFIG ===============#
# Define input flags to identify the job and task
tf.app.flags.DEFINE_string('data_dir', './dataset/imagenet', 'training data directory.')
tf.app.flags.DEFINE_string("job_name", "", "Either 'ps' or 'worker'")
tf.app.flags.DEFINE_integer("task_index", 0, "Index of task within the job")
tf.app.flags.DEFINE_string("ps_hosts", "",
                           "Comma-separated list of hostname:port pairs")
tf.app.flags.DEFINE_string("worker_hosts", "",
                           "Comma-separated list of hostname:port pairs")
FLAGS = tf.app.flags.FLAGS

ps_hosts = FLAGS.ps_hosts.split(",")
worker_hosts = FLAGS.worker_hosts.split(",")

# Create a tensorflow cluster
# Replace localhost with the host names if you are running on multiple hosts
# cluster = tf.train.ClusterSpec({"ps": ["localhost:2222"],
#                                 "worker": [	"localhost:2223",
#                                             "localhost:2224",
#                                             "localhost:2225"]})

cluster = tf.train.ClusterSpec({"ps": ps_hosts, "worker": worker_hosts})


# Start the server
server = tf.train.Server(cluster,
                         job_name=FLAGS.job_name,
                         task_index=FLAGS.task_index)


N_CATEGORY = 1000


def load_data():
    global train_generator
    global validation_generator
    datagen = keras.preprocessing.image.ImageDataGenerator(data_format='channels_last')

    train_generator = datagen.flow_from_directory(os.path.join(FLAGS.data_dir, 'i1k-extracted/train'),
                                                  target_size=(227, 227),
                                                  batch_size=128,
                                                  class_mode='categorical')

    validation_generator = datagen.flow_from_directory(os.path.join(FLAGS.data_dir, 'i1k-extracted/val'),
                                                       target_size=(227, 227),
                                                       batch_size=128,
                                                       class_mode='categorical',
                                                       shuffle=False)


def create_model():
    DROPOUT = 0.5
    model_input = keras.layers.Input(shape=(227, 227, 3))

    # First convolutional Layer (96x11x11)
    z = keras.layers.Conv2D(filters=96, kernel_size=(11, 11), strides=(4, 4), activation="relu")(model_input)
    z = keras.layers.MaxPooling2D(pool_size=(3, 3), strides=(2, 2))(z)
    z = keras.layers.BatchNormalization()(z)

    # Second convolutional Layer (256x5x5)
    z = keras.layers.ZeroPadding2D(padding=(2, 2))(z)
    z = keras.layers.Convolution2D(filters=256, kernel_size=(5, 5), strides=(1, 1), activation="relu")(z)
    z = keras.layers.MaxPooling2D(pool_size=(3, 3), strides=(2, 2))(z)
    z = keras.layers.BatchNormalization()(z)

    # Rest 3 convolutional layers
    z = keras.layers.ZeroPadding2D(padding=(1, 1))(z)
    z = keras.layers.Convolution2D(filters=384, kernel_size=(3, 3), strides=(1, 1), activation="relu")(z)

    z = keras.layers.ZeroPadding2D(padding=(1, 1))(z)
    z = keras.layers.Convolution2D(filters=384, kernel_size=(3, 3), strides=(1, 1), activation="relu")(z)

    z = keras.layers.ZeroPadding2D(padding=(1, 1))(z)
    z = keras.layers.Convolution2D(filters=256, kernel_size=(3, 3), strides=(1, 1), activation="relu")(z)

    z = keras.layers.MaxPooling2D(pool_size=(3, 3), strides=(2, 2))(z)
    z = keras.layers.Flatten()(z)

    z = keras.layers.Dense(4096, activation="relu")(z)
    z = keras.layers.Dropout(DROPOUT)(z)

    z = keras.layers.Dense(4096, activation="relu")(z)
    z = keras.layers.Dropout(DROPOUT)(z)

    final_dim = 1 if N_CATEGORY == 2 else N_CATEGORY
    final_act = "sigmoid" if N_CATEGORY == 2 else "softmax"
    model_output = keras.layers.Dense(final_dim, activation=final_act)(z)

    model = keras.models.Model(model_input, model_output)
    model.summary()
    return model


def create_optimizer(model, targets):
    WEIGHT_DECAY = 0.0005
    MOMENTUM = 0.9
    LEARNING_RATE = 0.01

    predictions = model.output
    loss = tf.reduce_mean(
        keras.losses.categorical_crossentropy(targets, predictions))

    # Keras-like learning rate descent function
    learning_rate = tf.constant(LEARNING_RATE, dtype=tf.float32)
    weight_decay = tf.constant(WEIGHT_DECAY, dtype=tf.float32)

    lr_compute_decay = tf.multiply(tf.cast(global_step, dtype=tf.float32), weight_decay)
    lr_compute_denominator = tf.add(lr_compute_decay, tf.constant(1, dtype=tf.float32))
    lr_compute_multiplier = tf.div(tf.constant(1, dtype=tf.float32), lr_compute_denominator)
    lr_operation = tf.multiply(learning_rate, lr_compute_multiplier)

    optimizer = tf.train.MomentumOptimizer(learning_rate=lr_operation, momentum=MOMENTUM)

    # Barrier to compute gradients after updating moving avg of batch norm
    with tf.control_dependencies(model.updates):
        barrier = tf.no_op(name="update_barrier")

    with tf.control_dependencies([barrier]):
        grads = optimizer.compute_gradients(
            loss,
            model.trainable_weights)
        grad_updates = optimizer.apply_gradients(grads, global_step=global_step)

    with tf.control_dependencies([grad_updates]):
        train_op = tf.identity(loss, name="train")

    accuracy = tf.contrib.metrics.accuracy(labels=tf.argmax(targets, 1),
                                           predictions=tf.argmax(predictions, 1))

    return (train_op, loss, predictions, accuracy, optimizer._learning_rate)


# Train the model (a single step)
def train(train_op, global_step, step, accuracy, learning_rate):
    log_frequency = 20
    start_time = time.time()
    batch_x, batch_y = train_generator.next()
    # perform the operations we defined earlier on batch
    loss_value, step_value = sess.run(
        [train_op, global_step],
        feed_dict={
            model.inputs[0]: batch_x,
            targets: batch_y})
    if step % log_frequency == 0:
        elapsed_time = time.time() - start_time
        acc = sess.run(accuracy, feed_dict={model.inputs[0]: batch_x,
                                            targets: batch_y})

        lr_val = sess.run(learning_rate)

        print("{},".format(time.strftime('%X %x %Z')),
              "Step: %d," % step_value,
              "Iteration: %2d," % step,
              "Cost: %.4f," % loss_value,
              "Accuracy: %.16f" % acc,
              "AvgTime: %3.2fms" % float(elapsed_time * 1000 / log_frequency),
              "Learning rate: %.16f" % lr_val)


def validate(epoch, total_loss, accuracy):
    batch_test_x, batch_test_y = validation_generator.next()
    test_accuracies = []
    test_losses = []
    test_batch_index = 0
    while test_batch_index * 128 < 50000:
        test_batch_loss, test_batch_acc = sess.run([total_loss, accuracy],
                                                   feed_dict={
            model.inputs[0]: batch_test_x,
            targets: batch_test_y})

        test_accuracies.append(test_batch_acc)
        test_losses.append(test_batch_loss)

        test_batch_index += 1

    mean_test_accuracy = sum(test_accuracies) / test_batch_index
    mean_test_loss = sum(test_losses) / test_batch_index

    print('{} Epoch {} ended. '
          'Validation loss: {}'.format(time.strftime('%X %x %Z'), epoch, mean_test_loss))
    print('Validation accuracy: {}%'.format(mean_test_accuracy))


if FLAGS.job_name == "ps":
    server.join()
elif FLAGS.job_name == "worker":
    load_data()

    # Assign operations to local server
    with tf.device(tf.train.replica_device_setter(
            worker_device="/job:worker/task:%d" % FLAGS.task_index,
            cluster=cluster)):
        keras.backend.set_learning_phase(True)
        keras.backend.manual_variable_initialization(True)
        model = create_model()
        targets = tf.placeholder(tf.float32, shape=[None, 1000], name="y-input")
        global_step = tf.get_variable('global_step', [],
                                      initializer=tf.constant_initializer(0),
                                      trainable=False)
        train_op, total_loss, predictions, accuracy, learning_rate = create_optimizer(model, targets)

        init_op = tf.global_variables_initializer()

    saver = tf.train.Saver()
    sv = tf.train.Supervisor(is_chief=(FLAGS.task_index == 0),
                             global_step=global_step,
                             logdir="./output/train_logs",
                             saver=saver,
                             save_model_secs=600,
                             init_op=init_op)

    print("Waiting for other servers")
    with sv.managed_session(server.target) as sess:
        keras.backend.set_session(sess)
        step = 0
        epoch = 1
        while not sv.should_stop() and step < 1000900:
            try:
                train(train_op, global_step, step, accuracy=accuracy, learning_rate=learning_rate)
                step += 1
                if step % 10009 == 0:
                    keras.backend.set_learning_phase(False)
                    validate(epoch, total_loss, accuracy=accuracy)
                    epoch += 1
                    keras.backend.set_learning_phase(True)
            except UnavailableError as e:
                print('WARNING: {}'.format(e))

    sv.stop()
    print("done")
