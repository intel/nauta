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

batch_size = 24
lstm_units = 64
num_classes = 2
iterations = 100000
max_seq_length = 250  # Max number of words in review (time steps)
num_dimensions = 300  # Dimensions for each word vector
dropout = 0.75
testing_size = TESTING_STOP - TESTING_START


def main(_):
    if not os.path.exists(FLAGS.data_dir):
        print('Make sure directory datasets/imdb exists')
        return

    try:
        word_vectors = np.load(os.path.join(FLAGS.data_dir, 'wordVectors.npy'))
    except Exception:
        print('Make sure to provide wordVectors.npy in specified directory')
        return
    print('Loaded the word vectors!')

    # Load pre-computed IDs matrix
    try:
        ids = np.load(os.path.join(FLAGS.data_dir, 'ids_matrix_imdb.npy'))
    except Exception:
        print('Make sure to provide ids_matrix_imdb.npy in specified directory')
        return
    print('Loaded the dataset!')

    # Model definition
    labels = tf.placeholder(tf.float32, [batch_size, num_classes])
    input_data = tf.placeholder(tf.int32, [batch_size, max_seq_length])
    keep_prob = tf.placeholder(tf.float32)

    data = tf.Variable(tf.zeros([batch_size, max_seq_length, num_dimensions]), dtype=tf.float32)
    data = tf.nn.embedding_lookup(word_vectors, input_data)

    lstm_cell = tf.contrib.rnn.BasicLSTMCell(lstm_units)
    lstm_cell = tf.contrib.rnn.DropoutWrapper(cell=lstm_cell, output_keep_prob=keep_prob)
    value, _ = tf.nn.dynamic_rnn(lstm_cell, data, dtype=tf.float32)

    weight = tf.Variable(tf.truncated_normal([lstm_units, num_classes]))
    bias = tf.Variable(tf.constant(0.1, shape=[num_classes]))
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
    logdir = "tensorboard/" + datetime.datetime.now().strftime("%Y%m%d-%H%M%S") + "/"
    writer = tf.summary.FileWriter(logdir, sess.graph)

    saver = tf.train.Saver()
    sess.run(tf.global_variables_initializer())

    # helper functions
    def get_train_batch():
        labels = []
        arr = np.zeros([batch_size, max_seq_length])
        for i in range(batch_size):
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
        arr = np.zeros([batch_size, max_seq_length])
        for i in range(batch_size):
            num = randint(TESTING_START, TESTING_STOP)
            if num <= 12499:
                labels.append([1, 0])  # Positive
            else:
                labels.append([0, 1])  # Negative
            arr[i] = ids[num - 1:num]
        return arr, labels

    # Training loop
    for i in range(iterations):
        # Next batch of reviews
        next_batch, next_batch_labels = get_train_batch()
        sess.run(optimizer, {input_data: next_batch, labels: next_batch_labels, keep_prob: dropout})

        # Write summary to Tensorboard
        if i % 50 == 0:
            summary = sess.run(merged, {input_data: next_batch, labels: next_batch_labels, keep_prob: 1.})
            writer.add_summary(summary, i)

        # Log training metrics
        if i % 200 == 0:
            train_acc, train_loss = sess.run([accuracy, loss], {input_data: next_batch, labels: next_batch_labels,
                                                                keep_prob: 1.})
            print('Training accuracy is:', train_acc, 'Loss:', train_loss)

        # Save the network every 10,000 training iterations
        if i % 10000 == 0 and i != 0:
            save_path = saver.save(sess, "models/pretrained_lstm.ckpt", global_step=i)
            print("saved to %s" % save_path)
    writer.close()

    # Testing loop
    accuracy_list = []
    for i in range(testing_size // batch_size):
        next_batch, next_batch_labels = get_test_batch()
        temp_accuracy_val = sess.run(accuracy, {input_data: next_batch, labels: next_batch_labels, keep_prob: 1.})
        accuracy_list.append(temp_accuracy_val)

    print('Average testing accuracy is:', sum(accuracy_list) / len(accuracy_list))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--data_dir', type=str,
                        default='/datasets/imdb',
                        help='Directory for storing input data')
    FLAGS, unparsed = parser.parse_known_args()
    tf.app.run(main=main, argv=[sys.argv[0]] + unparsed)
