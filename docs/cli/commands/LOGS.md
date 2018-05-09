# logs - displays logs from experiments

- [Synopsis](#synopsis)  
- [Arguments](#arguments)  
- [Options](#options)
- [Returns](#returns)
- [Notes](#notes)  
- [Examples](#examples)  
- [Status](#status)

## Synopsis

Displays logs from experiments - logs to be displayed are chosen based on parameters given in 
command's call. Format of this command is as follows:

_dlsctl logs <experiment_name>_

## Arguments

| Name | Obligatory | Description |
|:--- |:--- |:--- |
|_<experiment_name>_ | Yes | name of an experiment logs from which will be displayed |

## Options

Table with description of options (if there are options in a certain command)

| Name | Obligatory | Description | 
|:--- |:--- |:--- |
|_--min_severity_ | No | minimal severity of logs. Available choices are<br> - CRITICAL - displays only CRITICAL logs <br> - ERROR - displays ERROR and CRITICAL logs <br> - WARNING - displays ERROR, CRITICAL and WARNING logs <br> - INFO - displays ERROR, CRITICAL, WARNING and INFO<br> - DEBUG - displays ERROR, CRITICAL, WARNING, INFO and DEBUG |
|_--start_date_ | No | retrieve logs produced from this date (format ISO-8061 - yyyy-mm-ddThh:mm:ss)|
|_--end_date_ | No | retrieve logs produced until this date (format ISO-8061 - yyyy-mm-ddThh:mm:ss)|
|_--pod-ids_ | No | comma separated list of pod IDs, if provided, only logs from these pods from an experiment with _<experiment_name>_ name will be returned|
|_--pod_status_ | No | if given - get logs from an experiment with an _<experiment_name>_ name only for pods with given status|

## Returns

In case of any problems - message with description of their causes. Otherwise logs filtered based on command's parameters.

## Examples

_dlsctl logs experiment_name_2 --min_severity DEBUG_

Displays logs from _experiment_name_2_ experiment with severity DEBUG.

## Status

Under development
