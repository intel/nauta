# MIT License
#
# Copyright (c) 2019 Adit Deshpande. Intel Corporation.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

'''
Simple LSTM for sentiment analysis on IMDB reviews dataset originally posted on:
https://github.com/adeshpande3/LSTM-Sentiment-Analysis
'''

import argparse
import datetime
from random import randint
import os
import sys

import numpy as np
import tensorflow as tf

# Constants
TESTING_START = 11499
TESTING_STOP = 13499
TRAINING_START = 1
TRAINING_STOP = 24999
BATCH_SIZE = 24
LSTM_UNITS = 64
NUM_CLASSES = 2
ITERATIONS = 500
MAX_SEQ_LENGTH = 250  # Max number of words in review (time steps)
NUM_DIMENSIONS = 300  # Dimensions for each word vector
DROPOUT = 0.75
TESTING_SIZE = TESTING_STOP - TESTING_START


def main(_):
    # Check for proper directory existence
    if not os.path.exists(FLAGS.data_dir):
        print('Make sure data directory {} exists'.format(FLAGS.data_dir))
        exit(1)

    if FLAGS.export_dir == '':
        FLAGS.export_dir = os.getcwd()

    if not os.path.exists(FLAGS.export_dir):
        print('Make sure output directory {} exists'.format(FLAGS.export_dir))
        exit(1)

    try:
        word_vectors = np.load(os.path.join(FLAGS.data_dir, 'wordVectors.npy'))
        print('Loaded the word vectors!')
    except Exception:
        print('Make sure to provide wordVectors.npy in specified directory')

    # Load pre-computed IDs matrix
    try:
        ids = np.load(os.path.join(FLAGS.data_dir, 'ids_matrix_imdb.npy'))
        print('Loaded the dataset!')
    except Exception:
        print('Make sure to provide ids_matrix_imdb.npy in specified directory')

    # Model definition
    labels = tf.placeholder(tf.float32, [BATCH_SIZE, NUM_CLASSES])
    input_data = tf.placeholder(tf.int32, [BATCH_SIZE, MAX_SEQ_LENGTH])
    keep_prob = tf.placeholder(tf.float32)

    data = tf.Variable(tf.zeros([BATCH_SIZE, MAX_SEQ_LENGTH, NUM_DIMENSIONS]), dtype=tf.float32)
    data = tf.nn.embedding_lookup(word_vectors, input_data)

    lstm_cell = tf.contrib.rnn.BasicLSTMCell(LSTM_UNITS)
    lstm_cell = tf.contrib.rnn.DropoutWrapper(cell=lstm_cell, output_keep_prob=keep_prob)
    value, _ = tf.nn.dynamic_rnn(lstm_cell, data, dtype=tf.float32)

    weight = tf.Variable(tf.truncated_normal([LSTM_UNITS, NUM_CLASSES]))
    bias = tf.Variable(tf.constant(0.1, shape=[NUM_CLASSES]))
    value = tf.transpose(value, [1, 0, 2])
    last = tf.gather(value, int(value.get_shape()[0]) - 1)
    prediction = (tf.matmul(last, weight) + bias)

    correct_pred = tf.equal(tf.argmax(prediction, 1), tf.argmax(labels, 1))
    accuracy = tf.reduce_mean(tf.cast(correct_pred, tf.float32))

    loss = tf.reduce_mean(tf.nn.softmax_cross_entropy_with_logits(logits=prediction, labels=labels))
    optimizer = tf.train.AdamOptimizer().minimize(loss)

    sess = tf.InteractiveSession()

    tf.summary.scalar('Loss', loss)
    tf.summary.scalar('Training accuracy', accuracy)
    merged = tf.summary.merge_all()
    logdir = os.path.join("tensorboard", "{}/".format(datetime.datetime.now().strftime("%Y%m%d-%H%M%S")))
    writer = tf.summary.FileWriter(logdir, sess.graph)

    saver = tf.train.Saver()
    sess.run(tf.global_variables_initializer())

    # helper functions
    def get_train_batch():
        labels = []
        arr = np.zeros([BATCH_SIZE, MAX_SEQ_LENGTH])
        for i in range(BATCH_SIZE):
            if i % 2 == 0:
                num = randint(TRAINING_START, TESTING_START)
                labels.append([1, 0])
            else:
                num = randint(TESTING_STOP, TRAINING_STOP)
                labels.append([0, 1])
            arr[i] = ids[num - 1:num]
        return arr, labels

    def get_test_batch():
        labels = []
        arr = np.zeros([BATCH_SIZE, MAX_SEQ_LENGTH])
        for i in range(BATCH_SIZE):
            num = randint(TESTING_START, TESTING_STOP)
            if num <= 12499:
                labels.append([1, 0])  # Positive
            else:
                labels.append([0, 1])  # Negative
            arr[i] = ids[num - 1:num]
        return arr, labels

    # Training loop
    for i in range(ITERATIONS):
        # Next batch of reviews
        next_batch, next_batch_labels = get_train_batch()
        sess.run(optimizer, {input_data: next_batch, labels: next_batch_labels, keep_prob: DROPOUT})

        # Write summary to Tensorboard
        if i % 50 == 0:
            summary = sess.run(merged, {input_data: next_batch, labels: next_batch_labels, keep_prob: 1.})
            writer.add_summary(summary, i)

        # Log training metrics
        if i % 200 == 0:
            train_acc, train_loss = sess.run([accuracy, loss], {input_data: next_batch, labels: next_batch_labels,
                                                                keep_prob: 1.})
            print('Training accuracy is:', train_acc, 'Loss:', train_loss)

        # Save the network every 10,000 training ITERATIONS
        if i % 100 == 0 and i != 0:
            save_path = saver.save(sess, os.path.join(FLAGS.export_dir, "pretrained_lstm.ckpt"), global_step=i)
            print("Saved to: {}".format(save_path))
    writer.close()

    # Testing loop
    accuracy_list = []

    for i in range(TESTING_SIZE // BATCH_SIZE):
        next_batch, next_batch_labels = get_test_batch()
        temp_accuracy_val = sess.run(accuracy, {input_data: next_batch, labels: next_batch_labels, keep_prob: 1.})
        accuracy_list.append(temp_accuracy_val)

    print('Validation accuracy:', sum(accuracy_list) / len(accuracy_list))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--data_dir', type=str,
                        default='/datasets/imdb',
                        help='Directory which contains dataset')
    parser.add_argument('--export_dir', type=str,
                        default='',
                        help='Directory which contains export data')
    FLAGS, _ = parser.parse_known_args()
    tf.app.run()
