# cancel - cancels training

- [Synopsis](#synopsis)  
- [Arguments](#arguments)  
- [Returns](#returns)
- [Notes](#notes)  
- [Examples](#examples)  
- [Status](#status)

## Synopsis

Cancels training with a name given as a paramater. Format of this command is as follows:

_dlsctl cancel <experiment_name>_

## Arguments

| Name | Obligatory | Description |
|:--- |:--- |:--- |
|_<experiment_name>_ | Yes | name of an experiment to be cancelled |


## Returns

Description of a problem - if any occurs. Otherwise information that training was cancelled sucessfully. 

## Notes


## Examples

_dlsctl cancel t20180423121021851_

Cancels experiment with _t20180423121021851_ name.

## Status

Planned
