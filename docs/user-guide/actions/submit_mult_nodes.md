# Run an Experiment on Multiple Nodes

This section describes how to submit an experiment to run on multiple processing nodes, to accelerate the job. Storage locations for your input and output folders are determined by the mount command. See [Working with Datasets](working_with_datasets.md).

This experiment uses a template. For more information, refer to [Working with Template Packs](template_packs.md).

To run a multi-node experiment, the script _must_ support it. The following is the generic syntax (scroll right to see full contents).

**Syntax:** 

```
nctl exp submit [options]  SCRIPT-LOCATION --template [MULTINODE-TEMPLATE_NAME] SCRIPT-LOCATION [-- script-parameters]`
```

The template `tf-training-multi` is included with Nauta software. The following is an example command using this template (scroll right to see full contents):

**Syntax:** 

```
nctl experiment submit --name multinodes --template tf-training-multi /examples/mnist_multinode.py -- -- data_dir=/mnt/input/root/public/MNIST`
```

The following result displays showing the queued job.

```
Submitting experiments.   
| Run          | Parameters used        | Status  | Message |
|--------------+------------------------+---------+---------|
| multinodes   |                        | QUEUED  |         |
```

In the above command, to optionally set the number of workers and servers, set these as parameters below. The default values are 3 worker nodes and 1 parameter server. The following parameters are set to 2 worker nodes and 1 parameter server.

```
-p workersCount 2
-p pServersCount 1
```

## Return to Start of Document

* [README](../README.md)

----------------------
**IMPORTANT:** Where you see * for example TensorBoard* this indicates other names and brands may be claimed as the property of others. It _**does not**_ indicate a special character, command, variable, or parameter unless otherwise indicated. 
