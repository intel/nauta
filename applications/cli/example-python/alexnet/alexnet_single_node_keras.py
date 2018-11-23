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

import os

import tensorflow as tf
import tensorflow.contrib.keras as keras

tf.app.flags.DEFINE_string('data_dir', './dataset/imagenet', 'training data directory.')

FLAGS = tf.app.flags.FLAGS

N_CATEGORY = 1000
WEIGHT_DECAY = 0.0005
MOMENTUM = 0.9
BATCH_SIZE = 128
LEARNING_RATE = 0.01
DROPOUT = 0.5
ALPHA = 1e-4
BETA = 0.75


class LrCallback(keras.callbacks.Callback):
    def on_batch_end(self, batch, logs=None):
        lr = self.model.optimizer.lr
        decay = self.model.optimizer.decay
        iterations = self.model.optimizer.iterations
        lr_with_decay = lr / (1. + decay * keras.backend.cast(iterations, keras.backend.dtype(decay)))
        print(' Learning rate: {}'.format(keras.backend.eval(lr_with_decay)))


def main(_):
    datagen = keras.preprocessing.image.ImageDataGenerator(data_format='channels_last')
    train_generator = datagen.flow_from_directory(os.path.join(FLAGS.data_dir, 'i1k-extracted/train'),
                                                  target_size=(227, 227),
                                                  batch_size=128,
                                                  class_mode='categorical')

    validation_generator = datagen.flow_from_directory(os.path.join(FLAGS.data_dir, 'i1k-extracted/val'),
                                                       target_size=(227, 227),
                                                       batch_size=128,
                                                       class_mode='categorical')

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

    n = 5
    k = 2

    loss_metric = "binary_crossentropy" if N_CATEGORY == 2 else "categorical_crossentropy"
    model.compile(loss=loss_metric, metrics=["accuracy"],
                  optimizer=keras.optimizers.SGD(lr=LEARNING_RATE, momentum=MOMENTUM, decay=WEIGHT_DECAY))

    res = model.fit_generator(train_generator,
                              epochs=100,
                              steps_per_epoch=1281167 // 128,
                              validation_data=validation_generator, validation_steps=50000 // 128, verbose=1,
                              callbacks=[LrCallback()])


if __name__ == '__main__':
    tf.app.run()
