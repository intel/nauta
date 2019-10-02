# Evaluating Experiments

This section discusses the following main topics: 

 - [Viewing All Experiments Using the CLI](#viewing-all-experiments-using-the-cli)
 - [Viewing a Single Experiment's Details](#viewing-a-single-experiment-details)  
 - [Useful References](#useful-references)  
 
## Viewing All Experiments Using the CLI

To list all experiments you have submitted, run the next command. The possible returned statuses are:

* QUEUED - Experiment has been scheduled, but is not yet running
* RUNNING - Experiment is running
* COMPLETE - Experiment completed successfully
* CANCELLED - Experiment has been cancelled by a user
* FAILED - Experiment has failed
* CREATING - Experiment is being created

**Syntax:** `nctl experiment list [options]`

**Example:** An example experiment list is shown below.  

`nctl experiment list`

The following _example results_ are shown below (scroll right to see full contents).

```

| Experiment   | Parameters           | Metrics                     | Submission date        | Start date             | End date               | Owner   | State    | Template name      |
|--------------+----------------------+-----------------------------+------------------------+------------------------+------------------------+---------+----------+--------------------|
| single       | mnist_single_node.py | accuracy: 0.96875           | 2019-03-20 05:03:12 PM | 2019-03-20 05:04:32 PM | 2019-03-20 05:05:15 PM | user1   | FAILED   | tf-training-single |
|              |                      | global_step: 499            |                        |                        |                        |         |          |                    |
|              |                      | loss: 0.08342029            |                        |                        |                        |         |          |                    |
|              |                      | validation_accuracy: 0.9818 |                        |                        |                        |         |          |                    |
| single2      | mnist_single_node.py | accuracy: 0.953125          | 2019-03-20 05:06:19 PM | 2019-03-20 05:06:24 PM | 2019-03-20 05:07:05 PM | user1   | COMPLETE | tf-training-single |
|              |                      | global_step: 499            |                        |                        |                        |         |          |                    |
|              |                      | loss: 0.078533165           |                        |                        |                        |         |          |                    |
|              |                      | validation_accuracy: 0.9838 |                        |                        |                        |         |          |                    |
```

## Viewing a Single Experiment Details

The primary purpose of the next command is to provide Kubernetes pod-level information and container information for this experiment. This includes the pod ID, the POD status, information about input and output volumes used in this experiment, and CPU and memory resources requested to perform this experiment.

Use the following command to view a single experiment’s details:

**Syntax:** `nctl experiment view [options] EXPERIMENT-NAME`

**Example:** An example experiment view (the example name used is mnist-tb) is shown below.  

`nctl experiment view mnist-tb`

The following _example results_ are shown below (scroll right to see full contents).

```

| Experiment   | Parameters           | Metrics                     | Submission date        | Start date             | End date               | Owner   | State    | Template name      |
|--------------+----------------------+-----------------------------+------------------------+------------------------+------------------------+---------+----------+--------------------|
| mnist-tb     | mnist_single_node.py | accuracy: 1.0               | 2019-03-20 05:11:15 PM | 2019-03-20 05:11:20 PM | 2019-03-20 05:12:10 PM | user1   | COMPLETE | tf-training-single |
|              |                      | global_step: 499            |                        |                        |                        |         |          |                    |
|              |                      | loss: 0.035771053           |                        |                        |                        |         |          |                    |
|              |                      | validation_accuracy: 0.9804 |                        |                        |                        |         |          |                    |

Pods participating in the execution:

| Name              | Uid             | Pod Conditions        | Container Details                                 |
|-------------------+-----------------+-----------------------+---------------------------------------------------|
| mnist-tb-master-0 | ca2ca2c4-4b2a-1 | Initialized: True     | - Name: tensorflow                                |
|                   | 1e9-9c55-525816 |  reason: PodCompleted | - Status: Terminated, Completed                   |
|                   | 060100          | Ready: False          | - Volumes:                                        |
|                   |                 |  reason: PodCompleted |   input-home @ /mnt/input/home                    |
|                   |                 | PodScheduled: True    |   input-public @ /mnt/input/root                  |
|                   |                 |                       |   output-home @ /mnt/output/home                  |
|                   |                 |                       |   output-public @ /mnt/output/root                |
|                   |                 |                       |   output-home @ /mnt/output/experiment            |
|                   |                 |                       |   default-token-4k247 @                           |
|                   |                 |                       |     /var/run/secrets/kubernetes.io/serviceaccount |
|                   |                 |                       |                                                   |
|                   |                 |                       | - Resources:                                      |
|                   |                 |                       |   - Requests:                                     |
|                   |                 |                       |     cpu: 4750m    memory: 4843948078              |
|                   |                 |                       |   - Limits:                                       |
|                   |                 |                       |     cpu: 4750m    memory: 4843948078              |

Resources used by pods:

| Resource type    | Total usage        |
|------------------+--------------------|
| CPU requests:    | 4750m              |
| Memory requests: | 4GiB 523MiB 562KiB |
| CPU limits:      | 4750m              |
| Memory limits:   | 4GiB 523MiB 562KiB |


```

Volumes list include mount mode for each volume (in `<>` brackets), which can be either `ro` (read-only) or `rw` (read-write).

## Useful References 
* [Viewing Experiment Logs and Results Data](view_exp_logs.md)
* [Viewing experiments in TensorBoard](view_exp_logs.md)
* [Viewing Experiment Results from the Nauta Web UI](view_exp_webui.md)


----------------------

## Return to Start of Document

* [README](../README.md)

----------------------
