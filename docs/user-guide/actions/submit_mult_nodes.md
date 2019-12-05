# Run an Experiment on Multiple Nodes

This section describes how to submit an experiment to run on multiple processing nodes, to accelerate the job. Storage locations for your input and output folders are determined by the mount command. Refer to [Working with Datasets](working_with_datasets.md) for more information.

This experiment uses a template. For more information, refer to [Working with Template Packs](template_packs.md)

To run a multi-node experiment, the script must support it. The following is the generic syntax (scroll right to see the full contents).

**Syntax:** 

```
nctl experiment submit [options] --template [MULTINODE-TEMPLATE_NAME] SCRIPT-LOCATION [-- script-parameters]
```

The template `tf-training-multi` is included with the Nauta software. The following is an example command using this template (scroll right to see the full contents):

**Example:** 

```
nctl experiment submit --name multinodes --template multinode-tf-training-tfjob examples/mnist_multinode.py -– 
--data_dir=/mnt/input/root/public/MNIST

```

The following result displays showing the queued job.

```
Submitting experiments.
| Name       | Parameters                     | Status   | Message   |
|------------+--------------------------------+----------+-----------|
| multinodes | mnist_multinode.py -- data_dir | QUEUED   |           |
|            | =/mnt/input/root/public/MNIST  |          |           |

```
In the previous command, to optionally set the number of workers and servers, set these as parameters below. The default values are 3 worker nodes and 1 parameter server. The following parameters are set to 2 worker nodes and 1 parameter server.
```
-p workersCount 2
-p pServersCount 1
```

----------------------

## Return to Start of Document

* [README](../README.md)
----------------------
