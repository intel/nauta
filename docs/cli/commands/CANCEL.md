# cancel - cancels training

- [Synopsis](#synopsis)  
- [Arguments](#arguments)  
- [Options](#options)
- [Returns](#returns)
- [Examples](#examples)  
- [Status](#status)

## Synopsis

Cancels training chosen based on provided parameters. Format of this command is as follows:

_dlsctl cancel <name>_

## Arguments

| Name | Obligatory | Description |
|:--- |:--- |:--- |
|_<name>_ | Yes | name of an experiment/pod id/status of a pod to be cancelled. Command searches for objects matching given value - starting from names of experiments, pods ids and pods in a given status. If any such object has been found - the command displays for each of such objects a question whether this object should be cancelled. Value given here might contain only a part of an object's name. |

## Options

| Name | Obligatory | Description | 
|:--- |:--- |:--- |
|_-p/--purge_| No | if given - all information concerning experiments is removed from the system.|


## Returns

Description of a problem - if any occurs. Otherwise information that training job/jobs was/were cancelled sucessfully. 

## Examples

_dlsctl cancel t20180423121021851_

Cancels experiment with _t20180423121021851_ name.

## Status

Planned
