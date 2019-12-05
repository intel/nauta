# Evaluating Experiments

This section discusses the following main topics: 

 - [Viewing All Experiments Using the CLI](#viewing-all-experiments-using-the-cli)
 - [Viewing a Single Experiments Details](#viewing-a-single-experiments-details)
 - [Useful References](#useful-references)
 
## Viewing All Experiments Using the CLI

To list all experiments you have submitted, run the `nctl experiment`command and desired option. The possible returned statuses are:

* **QUEUED:** Experiment has been scheduled, but _is not yet_ running
* **RUNNING:** Experiment is running
* **COMPLETE:** Experiment completed successfully
* **CANCELLED:** Experiment has been cancelled by a user
* **FAILED:** Experiment has failed
* **CREATING:** Experiment is being created

**Syntax:** `nctl experiment list [options]`

**Example:** An example experiment list is shown below using the list option.  

`nctl experiment list`

The following _example results_ are shown below (scroll right to see full contents).

```

| Name                             | Parameters                     | Metrics                     | Submission date        | Start date             | Duration    | Owner   | Status    | Template name               | Template version   |
|----------------------------------+--------------------------------+-----------------------------+------------------------+------------------------+-------------+---------+-----------+-----------------------------+--------------------|
| mnist-sing-209-19-08-26-18-03-43 | mnist_single_node.py           |                             | 2019-08-26 06:05:05 PM |                        |             | user1   | CANCELLED | tf-training-tfjob           | 0.1.0              |
| multinode                        | mnist_multinode.py             |                             | 2019-08-26 06:06:32 PM |                        |             | user1   | QUEUED    | multinode-tf-training-tfjob | 0.1.0              |
| multinodes                       | mnist_multinode.py -- data_dir |                             | 2019-09-19 01:38:33 AM |                        |             | user1   | QUEUED    | multinode-tf-training-tfjob | 0.1.0              |
|                                  | =/mnt/input/root/public/MNIST  |                             |                        |                        |             |         |           |                             |                    |
| para-range-1                     | mnist_single_node.py lr=0.1 -- |                             | 2019-09-19 01:25:21 AM |                        |             | user1   | QUEUED    | tf-training-tfjob           | 0.1.0              |
|                                  | data_dir=/mnt/input/root/publi |                             |                        |                        |             |         |           |                             |                    |
|                                  | c/MNIST                        |                             |                        |                        |             |         |           |                             |                    |
| para-range-2                     | mnist_single_node.py lr=0.2 -- |                             | 2019-09-19 01:25:23 AM |                        |             | user1   | QUEUED    | tf-training-tfjob           | 0.1.0              |
|                                  | data_dir=/mnt/input/root/publi |                             |                        |                        |             |         |           |                             |                    |
|                                  | c/MNIST                        |                             |                        |                        |             |         |           |                             |                    |
| para-range-3                     | mnist_single_node.py lr=0.3 -- |                             | 2019-09-19 01:25:23 AM |                        |             | user1   | QUEUED    | tf-training-tfjob           | 0.1.0              |
|                                  | data_dir=/mnt/input/root/publi |                             |                        |                        |             |         |           |                             |                    |
|                                  | c/MNIST                        |                             |                        |                        |             |         |           |                             |                    |
| pytorch                          | mnist_multinode.py             |                             | 2019-08-26 06:58:01 PM |                        |             | user1   | QUEUED    | multinode-tf-training-tfjob | 0.1.0              |
| single                           | mnist_single_node.py           |                             | 2019-08-26 06:05:32 PM |                        |             | user1   | QUEUED    | tf-training-tfjob           | 0.1.0              |
| single2                          | mnist_single_node.py           | accuracy: 0.96875           | 2019-09-20 05:31:06 PM | 2019-09-20 05:31:14 PM | 0d 0h 1m 6s | user1   | COMPLETE  | tf-training-tfjob           | 0.1.0              |
|                                  |                                | global_step: 499            |                        |                        |             |         |           |                             |                    |
|                                  |                                | loss: 0.058229897           |                        |                        |             |         |           |                             |                    |
|                                  |                                | validation_accuracy: 0.9832 |                        |                        |             |         |           |                             |                    |


```

### Viewing a Single Experiments Details

The primary purpose of the next command is to provide Kubernetes pod-level information and container information for this experiment. This includes the pod ID, the POD status, information about input and output volumes used in this experiment, and CPU and memory resources requested to perform this experiment.

Use the following command to view a single experiment’s details:

**Syntax:** `nctl experiment view [options] EXPERIMENT-NAME`

**Example:** An example experiment view (the example name used is `single`) is shown below.  

`nctl experiment view single`

The following _example results_ are shown below (scroll right to see the full contents).

```

| Name   | Parameters           | Metrics   | Submission date        | Start date   | Duration   | Owner   | Status   | Template name     | Template version   |
|--------+----------------------+-----------+------------------------+--------------+------------+---------+----------+-------------------+--------------------|
| single | mnist_single_node.py |           | 2019-08-26 06:05:32 PM |              |            | user1   | QUEUED   | tf-training-tfjob | 0.1.0              |


Pods participating in the execution:

| Name            | Uid             | Pod Conditions                   | Container Details                                 |
|-----------------+-----------------+----------------------------------+---------------------------------------------------|
| single-master-0 | 55101ad9-c81b-1 | reason: Unschedulable,           | - Name: tensorflow                                |
|                 | 1e9-a56e-525816 |  message: 1/1 tasks in gang      | - Status: Not created                             |
|                 | 040500          |   unschedulable: 0/1 nodes are   | - Volumes:                                        |
|                 |                 |   available, 1 insufficient cpu, |   input-home <ro> @ /mnt/input/home               |
|                 |                 |   1 insufficient memory.         |   input-public <ro> @ /mnt/input/root             |
|                 |                 |                                  |   output-home <rw> @ /mnt/output/home             |
|                 |                 |                                  |   output-public <ro> @ /mnt/output/root           |
|                 |                 |                                  |   output-public <rw> @ /mnt/output/root/public    |
|                 |                 |                                  |   input-public <rw> @ /mnt/input/root/public      |
|                 |                 |                                  |   output-home <rw> @ /mnt/output/experiment       |
|                 |                 |                                  |   default-token-96ssz <ro> @                      |
|                 |                 |                                  |     /var/run/secrets/kubernetes.io/serviceaccount |
|                 |                 |                                  |                                                   |
|                 |                 |                                  | - Resources:                                      |
|                 |                 |                                  |   - Requests:                                     |
|                 |                 |                                  |     cpu: 19000m    memory: 93604421089            |
|                 |                 |                                  |   - Limits:                                       |
|                 |                 |                                  |     cpu: 19000m    memory: 93604421089            |

Resources used by pods:

| Resource type    | Total usage         |
|------------------+---------------------|
| CPU requests:    | 19000m              |
| Memory requests: | 87GiB 180MiB 135KiB |
| CPU limits:      | 19000m              |
| Memory limits:   | 87GiB 180MiB 135KiB |

Experiment is in QUEUED state due to insufficient number of cpus.


```

The volumes list includes the mount mode for each volume (in `<>` brackets), which can be either `ro` (read-only) or `rw` (read-write).

## Useful References 
* [Viewing Experiment Logs and Results Data](view_exp_logs.md)
* [Viewing experiments in TensorBoard](view_exp_tensorbd.md)
* [Viewing Experiment Results from the Nauta Web UI](view_exp_webui.md)


----------------------

## Return to Start of Document

* [README](../README.md)
----------------------
