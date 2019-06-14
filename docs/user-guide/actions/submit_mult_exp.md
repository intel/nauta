# Submitting Multiple Experiments

Storage locations for your input and output folders are determined by the mount command. See [Working with Datasets](working_with_datasets.md) and [Mounting Experiment Input to Storage](mount_exp_input.md).

This section describes how to launch multiple experiments using the same script, and discusses the following main topics:

- [Submitting Multiple Individual Experiments](#submitting-multiple-individual-experiments)
- [Parameter Ranges and Parameter Sets](#parameter-ranges-and-parameter-sets)  

## Submitting Multiple Individual Experiments

To submit multiple individual experiments that use the same script, use the following command syntax.

**Syntax:** `nctl exp submit -–parameter-range SCRIPT_NAME [-- script-parameters]`

**Example:** Below is an example command (scroll right to see full contents):  

```
nctl experiment submit -–parameter-range lr "{0.1, 0.2, 0.3}" 
examples/mnist_single_node.py -- --data_dir=/mnt/input/root/public/MNIST
```

Refer to [Working with Datasets](working_with_datasets.md) for instructions on uploading the dataset to the `input_shared` folder.

## Parameter Ranges and Parameter Sets

Parameters can include either:

* `parameter-range` argument that defines the name of a parameter together with its values expressed as either a range or an explicit set of values

   _-Or-_

* `parameter-sets` argument that specifies a number of distinct combinations of parameter values.

An example of this command using `parameter-range` is shown below (scroll right to see full contents).

```
nctl experiment submit --name para-range --parameter-range lr "{0.1, 0.2, 0.3}" examples/mnist_single_node.py -- --data_dir=/mnt/input/root/public/MNIST`
```

The following result displays.

```
Please confirm that the following experiments should be submitted.
| Experiment                       | Parameters       |
|----------------------------------+----------------- |
| paramenter-range-1  |  mnist_single_node.py         |
|                     |  lr=0.1                       |
| paramenter-range-2  |  mnist_single_node.py         |
|                     |  lr=0.2                       |
| paramenter-range-3  |  mnist_single_node.py         |
|                     |  lr=0.3                       |

Do you want to continue? [Y/n]: y

| Experiment          | Parameters                       | State   | Message   |
|---------------------+----------------------------------+---------+-----------|
| paramenter-range-1  | mnist_single_node.py lr=0.1      | QUEUED  |           |
| paramenter-range-2  | mnist_single_node.py lr=0.2      | QUEUED  |           |
| paramenter-range-3  | mnist_single_node.py lr=0.3      | QUEUED  |           |
```

**Note:** Your script _must be_ written to process your input data as it is presented, or conversely, your data _must be_ formatted to be processed by your script. No specific data requirements are made by the Nauta software.

----------------------

## Return to Start of Document

* [README](../README.md)
----------------------
