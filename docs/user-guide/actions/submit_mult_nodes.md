# Run an Experiment on Multiple Nodes

This section describes how to submit an experiment to run on multiple processing nodes, to accelerate the job. Storage locations for your input and output folders are determined by the mount command. See [Mounting Storage to View Experiment Output](mount_exp_output.md).

To run a multi-node experiment, the script must support it. Following is the generic syntax (line wrap is not intended).

**Syntax:** `dlsctl exp submit [OPTIONS] --template [MULTINODE_TEMPLATE_NAME] SCRIPT_NAME [-- SCRIPT_PARAMETERS]`

The template `multinode-tf-training-tfjob` is included as an example. Following is an example command (line wrap is not intended):

**Execute:** `dlsctl experiment submit --name multinodes --template multinode-tf-training-tfjob ~/mnist_multi_nodes.py -- -- data_dir=/mnt/input/root/public/mnist`

The following result displays showing the queued job.

![](images/multinodes.png)

In the above command, to optionally set the number of workers and servers, set these as parameters below. The default values are 3 worker nodes and 1 (one) parameter server. The following parameters are set to 2 worker nodes and 1 parameter server.

    -p multinode.workers_count 2

    -p multinode.ps_count 1
