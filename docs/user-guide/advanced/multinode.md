# Multi-node training
Deep Learning Studio support multi node training using standard cluster of Tensorflow servers. 
Please refer to Tensorflow documentation for detailed description:
 - https://www.tensorflow.org/deploy/distributed

## Tailoring multi-node training to run on Deep Learning Studio platform

The script should read environment variable TF_CONFIG which contains Tensorflow Job configuration.
The most important values are:

    cluster = tf_config_json.get('cluster')
    job_name = tf_config_json.get('task', {}).get('type')
    task_index = tf_config_json.get('task', {}).get('index')
    
The _job_name_ can be either _ps_ - for parameters server or _worker_ for Worker node.


## Running multi-node training with DLSCTL
The template _multinode-tf-training-tfjob_ should be used for multi-node training jobs. Additionally the pack parameters
can be configure from command line with th _-p_ or _--pack_param_ option

To define number of workers:
    
    -p workersCount 4
    
The default value of workers corresponds to number of physical nodes.

To define number of parameters servers:
    
    -p pServersCount 1

To define logging level for sidecar for parameter server:

    -p psSidecarLoggingLevel DEBUG

This logging level defaults to WARNING and behaves just like setting the logging level in python logger would. Allowed values for this param are: DEBUG, INFO, WARNING, ERROR, CRITICAL. Warning: setting logging level to INFO or DEBUG causes lots of status reports to appear in the experiment log. It might make experiment log very cluttered, so use it with care.
    

## Example

In the following example the _data_ folder contains _mnist_ folder with standard example mnist data files.

    dlsctl experiment submit multinode.py -sfl data -t multinode-tf-training-tfjob -p workersCount 12 -- --data_dir /app
    
    
The training script:

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
    
    import json
    import math
    import os
    
    import tensorflow as tf
    from tensorflow.examples.tutorials.mnist import input_data
    
    # noinspection PyUnresolvedReferences
    tf.app.flags.DEFINE_integer("hidden_units", 100,
                                "Number of units in the hidden layer of the NN")
    # noinspection PyUnresolvedReferences
    tf.app.flags.DEFINE_string("data_dir", "/tmp/mnist-data",
                               "Directory for storing mnist data")
    # noinspection PyUnresolvedReferences
    tf.app.flags.DEFINE_integer("batch_size", 100, "Training batch size")
    
    # noinspection PyUnresolvedReferences
    FLAGS = tf.app.flags.FLAGS
    
    IMAGE_PIXELS = 28
    
    
    def parse_tf_config():
        tf_config = os.environ.get('TF_CONFIG')
        if not tf_config:
            raise RuntimeError('TF_CONFIG not set!')
    
        tf_config_json = json.loads(tf_config)
    
        cluster = tf_config_json.get('cluster')
        job_name = tf_config_json.get('task', {}).get('type')
        task_index = tf_config_json.get('task', {}).get('index')
    
        if job_name is None or task_index is None:
            raise RuntimeError('TF_CONFIG invalid!')
    
        allowed_job_names = ('ps', 'worker')
    
        if job_name not in allowed_job_names:
            raise RuntimeError('bad job name: {job_name}, expected one of: {allowed_job_names}'.
                               format(job_name=job_name, allowed_job_names=allowed_job_names))
    
        return cluster, job_name, task_index
    
    
    def main(_):
        cluster, job_name, task_index = parse_tf_config()
    
        # Create a cluster from the parameter server and worker hosts.
        cluster_spec = tf.train.ClusterSpec(cluster)
    
        # Create and start a server for the local task.
        server = tf.train.Server(cluster_spec,
                                 job_name=job_name,
                                 task_index=task_index)
    
        if job_name == "ps":
            server.join()
            return
    
        # Assigns ops to the local worker by default.
        with tf.device(tf.train.replica_device_setter(
                worker_device="/job:worker/task:{task_index}".format(task_index=task_index),
                cluster=cluster)):
    
            # Variables of the hidden layer
            hid_w = tf.Variable(
                tf.truncated_normal([IMAGE_PIXELS * IMAGE_PIXELS, FLAGS.hidden_units],
                                    stddev=1.0 / IMAGE_PIXELS), name="hid_w")
            hid_b = tf.Variable(tf.zeros([FLAGS.hidden_units]), name="hid_b")
    
            # Variables of the softmax layer
            sm_w = tf.Variable(
                tf.truncated_normal([FLAGS.hidden_units, 10],
                                    stddev=1.0 / math.sqrt(FLAGS.hidden_units)),
                name="sm_w")
            sm_b = tf.Variable(tf.zeros([10]), name="sm_b")
    
            x = tf.placeholder(tf.float32, [None, IMAGE_PIXELS * IMAGE_PIXELS])
            y_ = tf.placeholder(tf.float32, [None, 10])
    
            hid_lin = tf.nn.xw_plus_b(x, hid_w, hid_b)
            hid = tf.nn.relu(hid_lin)
    
            y = tf.nn.softmax(tf.nn.xw_plus_b(hid, sm_w, sm_b))
            loss = -tf.reduce_sum(y_ * tf.log(tf.clip_by_value(y, 1e-10, 1.0)))
    
            global_step = tf.Variable(0)
    
            train_op = tf.train.AdagradOptimizer(0.01).minimize(
                loss, global_step=global_step)
    
            saver = tf.train.Saver()
            summary_op = tf.summary.merge_all()
            init_op = tf.initialize_all_variables()
    
        # Create a "supervisor", which oversees the training process.
        sv = tf.train.Supervisor(is_chief=(task_index == 0),
                                 logdir="/tmp/train_logs",
                                 init_op=init_op,
                                 summary_op=summary_op,
                                 saver=saver,
                                 global_step=global_step,
                                 save_model_secs=600)
    
        mnist = input_data.read_data_sets(FLAGS.data_dir, one_hot=True)
    
        # The supervisor takes care of session initialization, restoring from
        # a checkpoint, and closing when done or an error occurs.
        with sv.managed_session(server.target) as sess:
            # Loop until the supervisor shuts down or 1000000 steps have completed.
            step = 0
            while not sv.should_stop() and step < 10000:
                # Run a training step asynchronously.
                # See `tf.train.SyncReplicasOptimizer` for additional details on how to
                # perform *synchronous* training.
    
                batch_xs, batch_ys = mnist.train.next_batch(FLAGS.batch_size)
                train_feed = {x: batch_xs, y_: batch_ys}
    
                _, step = sess.run([train_op, global_step], feed_dict=train_feed)
                if step % 100 == 0:
                    print("Done step %d" % step)
    
        # Ask for all the services to stop.
        sv.stop()
    
    
    if __name__ == "__main__":
        tf.app.run()
    
