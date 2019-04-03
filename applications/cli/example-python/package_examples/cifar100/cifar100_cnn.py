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


import argparse
import multiprocessing
import os
from keras.datasets.cifar import load_batch

import keras
from keras.models import Sequential
from keras.layers import Dense, Dropout, Activation, Flatten
from keras.layers import Conv2D, MaxPooling2D
import keras.backend as K
from tensorflow import saved_model
import tensorflow as tf
import numpy as np

try:
    from experiment_metrics.api import publish
except ImportError:
    print("Nauta's Experiment metrics library not found.")
    publish = print  # If experiment_metrics.api is not available, simply bind publish to print function


class TensorflowModelCheckpoint(keras.callbacks.ModelCheckpoint):
    """
    A simple extension of keras.callbacks.ModelCheckpoint that saves model also in TensorFlow checkpoint format.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.saver = tf.train.Saver()

    def on_epoch_end(self, epoch, logs=None):
        super().on_epoch_end(epoch, logs)
        sess = keras.backend.get_session()
        self.saver.save(sess, self.filepath.replace('{epoch}', str(epoch)).replace('h5', 'ckpt'))


class NautaExperimentMetricsCallback(keras.callbacks.Callback):
    def on_epoch_end(self, epoch, logs: dict = None):
        publish({'accuracy': str(logs.get('acc')),
                 'loss': str(logs.get('loss')),
                 'validation_accuracy': str(logs.get('val_acc')),
                 'validation_loss': str(logs.get('val_loss'))})


def load_data(dataset_path: str = None, label_mode='fine'):
    if dataset_path:
        fpath = os.path.join(dataset_path, 'train')
        x_train, y_train = load_batch(fpath, label_key=label_mode + '_labels')

        fpath = os.path.join(dataset_path, 'test')
        x_test, y_test = load_batch(fpath, label_key=label_mode + '_labels')

        y_train = np.reshape(y_train, (len(y_train), 1))
        y_test = np.reshape(y_test, (len(y_test), 1))

        if K.image_data_format() == 'channels_last':
            x_train = x_train.transpose(0, 2, 3, 1)
            x_test = x_test.transpose(0, 2, 3, 1)

        return x_train, y_train, x_test, y_test
    else:
        (x_train, y_train), (x_test, y_test) = keras.datasets.cifar100.load_data(label_mode='fine')
        return x_train, y_train, x_test, y_test


def create_model(input_shape, num_classes=100) -> keras.Model:
    """
    A simple convolutional neural network based on Keras' CIFAR10 example
    (https://github.com/keras-team/keras/blob/master/examples/cifar10_cnn.py), adjusted to work on CIFAR100 dataset.
    ELU activation function should give best performance results according to
    Fast and Accurate Deep Network Learning by Exponential Linear Units (ELUs) (https://arxiv.org/abs/1511.07289).
    :param input_shape: image input shape
    :param num_classes: number of image classes
    """
    model = Sequential()
    model.add(Conv2D(64, (3, 3), padding='same',
                     input_shape=input_shape))
    model.add(Activation('elu'))
    model.add(Conv2D(64, (3, 3)))
    model.add(Activation('elu'))
    model.add(MaxPooling2D(pool_size=(2, 2)))
    model.add(Dropout(0.25))

    model.add(Conv2D(128, (3, 3), padding='same'))
    model.add(Activation('elu'))
    model.add(Conv2D(128, (3, 3)))
    model.add(Activation('elu'))
    model.add(MaxPooling2D(pool_size=(2, 2)))
    model.add(Dropout(0.25))

    model.add(Flatten())
    model.add(Dense(512))
    model.add(Activation('elu'))
    model.add(Dropout(0.5))
    model.add(Dense(num_classes))
    model.add(Activation('softmax'))
    return model


def train(dataset_path: str = None, batch_size=256, epochs=100, use_horovod=False,
          output_path=None, model_name='keras_cifar100_trained_model.h5'):
    x_train, y_train, x_test, y_test = load_data(dataset_path)
    print('x_train shape:', x_train.shape)
    print(x_train.shape[0], 'train samples')
    print(x_test.shape[0], 'test samples')

    num_classes = 100

    if not output_path:
        output_path = os.path.join(os.getcwd(), 'saved_models')

    # Convert class vectors to binary class matrices.
    y_train = keras.utils.to_categorical(y_train, num_classes)
    y_test = keras.utils.to_categorical(y_test, num_classes)

    model = create_model(input_shape=x_train.shape[1:], num_classes=num_classes)
    if use_horovod:
        import horovod.keras as hvd
        hvd.init()
        opt = keras.optimizers.rmsprop(lr=0.0001 * hvd.size(), decay=1e-6)
        opt = hvd.DistributedOptimizer(opt)
        with tf.Graph().as_default():
            inference_model = create_model(input_shape=x_train.shape[1:], num_classes=num_classes)
            inference_dummy_opt = keras.optimizers.rmsprop(lr=0.0001, decay=1e-6)
            inference_model.compile(loss='categorical_crossentropy', optimizer=inference_dummy_opt,
                                    metrics=['accuracy'])
    else:
        opt = keras.optimizers.rmsprop(lr=0.0001, decay=1e-6)
        inference_model = model

    # Compile and export inference model graph
    serve_graph_file = f'{output_path}/servegraph.meta'
    tf.train.export_meta_graph(serve_graph_file, as_text=True)

    model.compile(loss='categorical_crossentropy', optimizer=opt, metrics=['accuracy'])

    x_train = x_train.astype('float32')
    x_test = x_test.astype('float32')
    x_train /= 255
    x_test /= 255

    model.summary()

    callbacks = []
    if use_horovod:
        callbacks.append(hvd.callbacks.BroadcastGlobalVariablesCallback(0))
    # Save checkpoints/metrics only on first worker
    if not use_horovod or hvd.rank() == 0:
        callbacks.append(TensorflowModelCheckpoint(f'{output_path}/checkpoint-{{epoch}}.h5'))
        callbacks.append(NautaExperimentMetricsCallback())
        callbacks.append(keras.callbacks.TensorBoard(log_dir=f'{output_path}/tensorboard', update_freq=1000,
                                             histogram_freq=0, write_graph=True))


    model.fit(x_train, y_train, batch_size=batch_size, epochs=epochs, validation_data=(x_test, y_test),
              shuffle=True, callbacks=callbacks)

    # Save model and weights
    if not os.path.isdir(output_path):
        os.makedirs(output_path)
    model_path = os.path.join(output_path, model_name)
    model.save(model_path)
    print(f'Saved trained model at {model_path}')

    # Save model in Tensorflow Serving compatible format
    # https://gist.github.com/dmwendt/ed2779f07aa849eda2e1756cd3b9fcb0
    if not use_horovod or hvd.rank() == 0:
        # Now save the model for inference.
        # First, load the parameters from the latest checkpoint file.
        checkpoint_file = tf.train.latest_checkpoint(output_path)
        tf_model_export_dir = f'{output_path}/cifar100_tf_model/1'
        # Create a new graph to import the previously exported one.
        with tf.Graph().as_default():
            # Import the saved graph.
            restorer = tf.train.import_meta_graph(serve_graph_file)
            with tf.Session() as sess:
                restorer.restore(sess, checkpoint_file)
                saved_model.simple_save(session=sess, export_dir=tf_model_export_dir,
                                        inputs={'x': inference_model.layers[0].input},
                                        outputs={'y': inference_model.layers[-1].output})
        print(f'Saved trained model in TF format at {tf_model_export_dir}')

    # Score trained model.
    scores = model.evaluate(x_test, y_test, verbose=1)
    print('Test loss:', scores[0])
    print('Test accuracy:', scores[1])


def parse_args():
    parser = argparse.ArgumentParser(description='CIFAR100 CNN training script.')
    parser.add_argument('--epochs', default=100, type=int)
    parser.add_argument('--batch-size', default=256, type=int)
    parser.add_argument('--data-augmentation', help='Use real time data augmentatio',
                        default=False, action='store_true')
    parser.add_argument('--use-horovod', help='Use horovod in order to distribute training',
                        default=False, action='store_true')
    parser.add_argument('--dataset-path', help='Path to CIFAR100 dataset, if not provided, '
                                               'dataset will be downloaded automatically.',
                        default=None, type=str)
    parser.add_argument('--output-path', help='Path to where checkpoints/metrics/models will be saved.',
                        default=None, type=str)
    parser.add_argument('--cpu-count', help='Number of physical CPU cores on the machine. '
                                            'If not passed, script will try to obtain CPU count automatically.',
                        default=None)
    return parser.parse_args()


if __name__ == '__main__':
    args = parse_args()
    # performance settings
    if not args.cpu_count:
        args.cpu_count = multiprocessing.cpu_count()
    config = tf.ConfigProto(intra_op_parallelism_threads=int(args.cpu_count), inter_op_parallelism_threads=2,
                            allow_soft_placement=True, device_count={'CPU': int(args.cpu_count)})
    session = tf.Session(config=config)
    K.set_session(session)
    os.environ["OMP_NUM_THREADS"] = str(args.cpu_count)
    os.environ["KMP_BLOCKTIME"] = "30"
    os.environ["KMP_SETTINGS"] = "1"
    os.environ["KMP_AFFINITY"] = "granularity=fine,verbose,compact,1,0"
    train(dataset_path=args.dataset_path, epochs=args.epochs, batch_size=args.batch_size, use_horovod=args.use_horovod,
          output_path=args.output_path)
