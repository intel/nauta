# predict - runs inference on previously trained model

- [Synopsis](#synopsis)  
- [Arguments](#arguments)  
- [Options](#options)
- [Returns](#returns)
- [Notes](#notes)  
- [Examples](#examples)  
- [Status](#status)

## Synopsis

Command runs inference based on previously trained models. Format of the command is as follows:

_dlsctl predict_

## Arguments

| Name | Obligatory | Description |
|:--- |:--- |:--- |
|_<path>_ | Yes | location of a trained model |

## Options

Table with description of options (if there are options in a certain command)

| Name | Obligatory | Description | 
|:--- |:--- |:--- |
|_-n/-name_ | No | name used to refer to deployed model. If not given - name is constructed automatically. |


## Returns

In case of any problems - a message with a description of causes of problems.
Otherwise URL to a page with results of inference.

## Examples

_dlsctl predict /models/model-for-prediction_

Launches inference based on model _/models/model-for-prediction_

## Status

planned
