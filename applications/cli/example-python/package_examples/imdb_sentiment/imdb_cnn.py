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

# based on https://github.com/keras-team/keras/blob/master/examples/imdb_cnn.py


import argparse
import multiprocessing
import os

import keras
from keras.preprocessing import sequence
from keras.models import Sequential
from keras.layers import Dense, Dropout, Activation
from keras.layers import Embedding
from keras.layers import Conv1D, GlobalMaxPooling1D
from keras.datasets import imdb
from keras import backend as K
from keras_preprocessing.sequence import _remove_long_seq
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
                 'loss': str(logs.get('loss'))[:5],  # Reduce precision for shorter metrics
                 'validation_accuracy': str(logs.get('val_acc')),
                 'validation_loss': str(logs.get('val_loss'))[:5]})



def load_data(dataset_path: str = None, num_words=None, skip_top=0, maxlen=None, seed=113, start_char=1, oov_char=2,
              index_from=3):
    print('Loading data...')
    if dataset_path:
        with np.load(dataset_path) as f:
            x_train, labels_train = f['x_train'], f['y_train']
            x_test, labels_test = f['x_test'], f['y_test']

        np.random.seed(seed)
        indices = np.arange(len(x_train))
        np.random.shuffle(indices)
        x_train = x_train[indices]
        labels_train = labels_train[indices]

        indices = np.arange(len(x_test))
        np.random.shuffle(indices)
        x_test = x_test[indices]
        labels_test = labels_test[indices]

        xs = np.concatenate([x_train, x_test])
        labels = np.concatenate([labels_train, labels_test])

        if start_char is not None:
            xs = [[start_char] + [w + index_from for w in x] for x in xs]
        elif index_from:
            xs = [[w + index_from for w in x] for x in xs]

        if maxlen:
            xs, labels = _remove_long_seq(maxlen, xs, labels)
            if not xs:
                raise ValueError('After filtering for sequences shorter than maxlen=' +
                                 str(maxlen) + ', no sequence was kept. '
                                               'Increase maxlen.')
        if not num_words:
            num_words = max([max(x) for x in xs])

        # by convention, use 2 as OOV word
        # reserve 'index_from' (=3 by default) characters:
        # 0 (padding), 1 (start), 2 (OOV)
        if oov_char is not None:
            xs = [[w if (skip_top <= w < num_words) else oov_char for w in x]
                  for x in xs]
        else:
            xs = [[w for w in x if skip_top <= w < num_words]
                  for x in xs]

        idx = len(x_train)
        x_train, y_train = np.array(xs[:idx]), np.array(labels[:idx])
        x_test, y_test = np.array(xs[idx:]), np.array(labels[idx:])

        print(len(x_train), 'train sequences')
        print(len(x_test), 'test sequences')
        return x_train, y_train, x_test, y_test
    else:
        (x_train, y_train), (x_test, y_test) = imdb.load_data(num_words=num_words)
        print(len(x_train), 'train sequences')
        print(len(x_test), 'test sequences')
        return x_train, y_train, x_test, y_test


def preprocess_data(x_train, x_test):
    print('Pad sequences (samples x time)')
    x_train = sequence.pad_sequences(x_train, maxlen=maxlen)
    x_test = sequence.pad_sequences(x_test, maxlen=maxlen)
    print('x_train shape:', x_train.shape)
    print('x_test shape:', x_test.shape)
    return x_train, x_test


def create_model():
    print('Build model...')
    model = Sequential()

    # we start off with an efficient embedding layer which maps
    # our vocab indices into embedding_dims dimensions
    model.add(Embedding(max_features,
                        embedding_dims,
                        input_length=maxlen))
    model.add(Dropout(0.2))

    # we add a Convolution1D, which will learn filters
    # word group filters of size filter_length:
    model.add(Conv1D(filters,
                     kernel_size,
                     padding='valid',
                     activation='relu',
                     strides=1))
    # we use max pooling:
    model.add(GlobalMaxPooling1D())

    # We add a vanilla hidden layer:
    model.add(Dense(hidden_dims))
    model.add(Dropout(0.2))
    model.add(Activation('relu'))

    # We project onto a single unit output layer, and squash it with a sigmoid:
    model.add(Dense(1))
    model.add(Activation('sigmoid'))

    model.compile(loss='binary_crossentropy',
                  optimizer='adam',
                  metrics=['accuracy'])
    return model


def train(model, x_train, y_train, x_test, y_test, output_path: str = None):
    if not output_path:
        output_path = '.'

    print(model.summary())

    callbacks = []
    callbacks.append(TensorflowModelCheckpoint(f'{output_path}/checkpoint-{{epoch}}.h5'))
    callbacks.append(NautaExperimentMetricsCallback())
    callbacks.append(keras.callbacks.TensorBoard(log_dir=f'{output_path}/tensorboard', update_freq=1000,
                                                 histogram_freq=0, write_graph=True))

    model.fit(x_train, y_train,
              batch_size=batch_size,
              epochs=epochs,
              callbacks=callbacks,
              validation_data=(x_test, y_test))

    return model


def save_model(model, output_path: str = None, model_name='keras_imdb_trained_model.h'):
    if not output_path:
        output_path = os.path.join(os.getcwd(), 'saved_models')

    # Save model and weights
    if not os.path.isdir(output_path):
        os.makedirs(output_path)
    model_path = os.path.join(output_path, model_name)
    model.save(model_path)
    print(f'Saved trained model at {model_path}')

    sess = K.get_session()
    tf_model_export_dir = f'{output_path}/imdb_tf_model/1'
    saved_model.simple_save(session=sess, export_dir=tf_model_export_dir,
                            inputs={'x': model.layers[0].input},
                            outputs={'y': model.layers[-1].output})

def parse_args():
    parser = argparse.ArgumentParser('IMDB sentiment classification training script.')
    parser.add_argument('--epochs', default=2)
    parser.add_argument('--batch-size', default=32)
    parser.add_argument('--embedding-dims', default=50)
    parser.add_argument('--filters', default=500)
    parser.add_argument('--kernel-size', default=3)
    parser.add_argument('--hidden-dims', default=250)
    parser.add_argument('--dataset-path', help='Path to IMDB reviews dataset, if not provided, '
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
    os.environ["KMP_BLOCKTIME"] = "0"
    os.environ["KMP_SETTINGS"] = "1"
    os.environ["KMP_AFFINITY"] = "granularity=fine,verbose,compact,1,0"

    # set parameters:
    max_features = 5000
    maxlen = 400
    batch_size = int(args.batch_size)
    embedding_dims = int(args.embedding_dims)
    filters = int(args.filters)
    kernel_size = int(args.kernel_size)
    hidden_dims = int(args.hidden_dims)
    epochs = int(args.epochs)

    x_train, y_train, x_test, y_test = load_data(dataset_path=args.dataset_path, num_words=max_features)
    x_train, x_test = preprocess_data(x_train, x_test)
    model = create_model()
    model = train(model, x_train, y_train, x_test, y_test, output_path=args.output_path)
    save_model(model=model, output_path=args.output_path)
