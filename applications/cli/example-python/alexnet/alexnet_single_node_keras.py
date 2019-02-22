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
