# Cancelling Experiments

To cancel one or more experiments, use the following command:
 
`$ nctl experiment cancel [Options] EXPERIMENT_NAME`

This command stops and cancels any experiment queued or in progress. Completed experiments cannot be cancelled.  Cancels any experiment based on the name of an experiment/pod/status of a pod. If any such object is found the command queries if these objects (one or more) should be cancelled.

The value of this argument should be created using rules described here. Use this command to cancel one or more experiments with matching or partially-matching names, a matching pod ID, matching pod status, or combinations of these criteria.
For example, the following command will cancel all experiments with a matching or partially matching name:

**Syntax**: `nctl experiment cancel --match EXPERIMENT_NAME`

The following command will cancel all experiments with a matching pod-ID, using one or more comma-separated IDs:

**Syntax**: `nctl experiment cancel –-pod-ids [pod_ID] EXPERIMENT_NAME`

The following command will cancel all experiments with a matching pod-status, using one of the following statuses: [PENDING, RUNNING, SUCCEEDED, FAILED, UNKNOWN]:

`$ nctl experiment cancel --pod-status [PENDING, RUNNING, SUCCEEDED, FAILED, UNKNOWN] EXPERIMENT_NAME`

Any of the above criteria can be combined. 

You can also purge all information concerning any experiment using the `-p` or `--purge` option.
