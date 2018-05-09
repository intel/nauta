# view - displays basic details of an experiment

- [Synopsis](#synopsis)  
- [Arguments](#arguments)  
- [Options](#options)
- [Returns](#returns)
- [Notes](#notes)  
- [Examples](#examples)  
- [Status](#status)

## Synopsis

Displays basic details of an experiment - like a name of an experiment, parameters, submission date etc. 
Format of this command is as follows:

_dlsctl view <experiment_name>_

## Arguments

| Name | Obligatory | Description |
|:--- |:--- |:--- |
|_\<experiment_name\>_ | Yes | Name of an experiment to be displayed. |

## Options

| Name | Obligatory | Description | 
|:--- |:--- |:--- |
|_-t/--tensorboard_ | No | exposes _tensorboard_ instance with data from an experiment to a user.  |

## Returns

Displays details of an experiment. If _-t/--tensorboard_ option is given - the command returns also a link to tensorboard's instance with data from an experiment.


## Examples

_dlsctl view experiment_name_2 -t_

Displays details of an _experiment_name_2_ experiment and exposes _tensorboard_ instance with experiment's data to a user.

## Status

Planned
