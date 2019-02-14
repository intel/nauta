# config Command

 Use this command to adjust packs' settings to resources available on a cluster.

- [Synopsis](#synopsis)  
- [Syntax](#syntax)
- [Options](#options)
- [Returns](#returns)
- [Examples](#examples)  

### Synopsis

 Allows a user to change the current system's settings concerning maximum and requested resources used by training jobs initiated by Nauta. The command
takes cpu number and memory amount provided by a user and calculates new values preserving the same coefficient between available resources and
resources defined in every template like it was before execution of this command.     

### Syntax

`nctl config [options]`

### Options

| Name | Required | Description | 
|:--- |:--- |:--- |
|`-c, --cpu` | Yes | Number of cpus available on a cluster's node with the lowest number of cpu. Value should be given in format accepted by k8s - it can be a plain number or a number followed by 'm' suffix.|
|`-m, --memory` | Yes | Amount of a memory available on a cluster's node with the lowest amount of memory. Value should be given in format accepted by k8s - it can be a plain number or a number followed by a one of the following suffixes E, P, T, G, M, K, Ei, Pi, Ti, Gi, Mi, Ki. |
|`-v, --verbose`| No | Set verbosity level: <br>`-v` for INFO, <br>`-vv` for DEBUG |
|`-h, --help` | No | Show help message and exit. |

**Note**  
Number of cpu given here should be interpreted according to https://kubernetes.io/docs/concepts/configuration/manage-compute-resources-container/#meaning-of-cpu.
Amount of memory given here should be interpreted according to https://kubernetes.io/docs/concepts/configuration/manage-compute-resources-container/#meaning-of-memory.


### Returns

In case of any problems - message describing their cause/causes. Otherwise message is returned indicating success. 

### Example

`nctl config --cpu 10 --memory 1Gi`

Calculates resources' settings for all packs installed together with nctl application. It assumes, that 
the maximal available number of cpu on a node is 10 and that this node provides 1Gb of ram. Limited and requested 
resources are calculated using those maximal values.