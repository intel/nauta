# Cancelling Experiments

The `nctl experiment cancel` command stops and cancels any experiment queued or in progress. Furthermore, the command also cancels any experiment based on the name of an _experiment/pod/status_ of a pod. If any such an object is found, the command queries if these objects (one or more) should be cancelled.

This section discusses the following main topics: 

- [Cancelling One or More Experiments](#cancelling-one-or-more-experiments)  
- [Cancelling All Experiments with a Matching Pod-ID](#cancelling-all-experiments-with-a-matching-pod-id)  
- [Cancelling All Experiments with a Matching Pod-Status](#cancelling-all-experiments-with-a-matching-pod-status)  


## Cancelling One or More Experiments

To cancel one or more experiments, execute the following command:
 
`nctl experiment cancel [Options] EXPERIMENT-NAME`

The value of this argument should be created using rules described here. Use this command to cancel one or more experiments with matching or partially-matching names, a matching pod ID, matching pod status, or combinations of these criteria.
For example, the following command will cancel all experiments with a matching or partially matching name:

**Syntax**: `nctl experiment cancel --match EXPERIMENT-NAME`

## Cancelling All Experiments with a Matching Pod-ID

The following command will cancel all experiments with a matching pod-ID, using one or more comma-separated IDs:

**Syntax**: `nctl experiment cancel –-pod-ids [pod_ID] EXPERIMENT-NAME`

## Cancelling All Experiments with a Matching Pod-Status

The following command will cancel all experiments with a matching pod-status, using one of the following statuses: [PENDING, RUNNING, SUCCEEDED, FAILED, UNKNOWN]:

`nctl experiment cancel --pod-status [PENDING, RUNNING, SUCCEEDED, FAILED, UNKNOWN] EXPERIMENT-NAME`

Any of the above criteria can be combined. 

You can also purge all information concerning any experiment using the `-p` or `--purge` option. For _purge_ information, refer to [Purging](../actions/delete_user.md).

----------------------

## Return to Start of Document

* [README](../README.md)

----------------------

