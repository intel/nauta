# config Command

 Use the `config` command to adjust a packs' settings to resources available on a cluster. 

- [Synopsis](#synopsis)  
- [Syntax](#syntax)
- [Options](#options)
- [Returns](#returns)
- [Example](#example)  

### Synopsis

Allows you to change the current system's settings concerning maximum and requested resources used by training jobs initiated by Nauta. The command takes CPU number and memory amount provided (by you) and calculates new values preserving the same coefficient between available resources and resources defined in every template, as it was before execution of this command.     

### Syntax

`nctl config [options]`

### Options

| Name | Required | Description | 
|:--- |:--- |:--- |
|`-c, --cpu` | Yes | Number of CPUs available on a cluster's node with the lowest number of CPU. Value should be given in format accepted by k8s, it can be a plain number or a number followed by 'm' suffix.|
|`-m, --memory` | Yes | This is the amount of a memory available on a cluster's node with the lowest amount of memory. Value should be given in format accepted by k8s: it can be a plain number or a number followed by a one of the following suffixes E, P, T, G, M, K, Ei, Pi, Ti, Gi, Mi, Ki. |
|`-f, --force`| No | Ignore (most) confirmation prompts during command execution |
|`-v, --verbose`| No | Set verbosity level: <br>`-v` for INFO, <br>`-vv` for DEBUG |
|`-h, --help` | No | Displays help messaging information. |

**Note:** Number of CPUs shown should be interpreted according to the following article: [Meaning of CPU](https://kubernetes.io/docs/concepts/configuration/manage-compute-resources-container/#meaning-of-cpu)
and the amount of memory given here should be interpreted according to the following acle: 
[Meaning of Memory](https://kubernetes.io/docs/concepts/configuration/manage-compute-resources-container/#meaning-of-memory).

### Returns

In case of any problems, a message describing the cause/causes of the issue displays. Otherwise message is returned indicating success. 

### Example

`nctl config --cpu 10 --memory 10Gi`

### Outcome

Calculates resources' settings for all packs installed together with `nctl` application. It assumes, that 
the maximal available number of CPU on a node is 10 and that this node provides 1Gb of RAM. Furthermore, limited and requested resources are calculated using those maximal values.

----------------------

## Return to Start of Document

* [README](../README.md)

----------------------
