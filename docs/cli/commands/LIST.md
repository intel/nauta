# list - displays a list of experiments

- [Synopsis](#synopsis)  
- [Arguments](#arguments)  
- [Options](#options)
- [Returns](#returns)
- [Notes](#notes)  
- [Examples](#examples)  
- [Status](#status)

## Synopsis

Displays a list of experiments with some basic information regarding each of them. Results are
sorted using a date of creation of an experiment - starting from the latest one. The format of this command is as follows:  

_dlsctl list <options>_  


## Options

| Name | Obligatory | Description | 
|:--- |:--- |:--- |
|_-m/--match<br> <experiment_name>_ | No | filters list of experiments by experiment name. _<experiment_name>_ can be a regular expression. If this option is not given - command displays a list of all experiments submitted by a user. |
|_-a/--all_users_| No | list contains experiments of all users.|


## Returns

List of experiments matching criteria given in command's options. Each row contains, except of
experiments name, also additional data of each experiments - like parameters used
for this certain training, time and date when ot was submitted, name of a user 
which submitted this training and current status of an experiment. Below is an
example table returned by this command. 

<!-- language: lang-none -->

    +----------------------+---------------------+---------------+----------------+----------+----------+
    | Experiment           | Parameters used     | Metrics       | Time submitted | Username | Status   |
    +======================+=====================+===============+================+==========+==========|
    | exp1-20181122:0830-1 | learningrate: 0.1   | loss: 0.05    |  20181122:0830 | jdoe     | Complete |
    |                      | padding: 2          | accuracy: 0.9 |                |          |          |
    |                      | layers: 10          |               |                |          |          |
    | exp1-20181122:0830-2 | learningrate: 0.01  |               |  20181122:0830 | jdoe     | Running` |
    | exp1-20181122:0830-3 | learningrate: 0.001 |               |  20181122:0830 | jdoe     | Queued   |
    +----------------------+---------------------+---------------+----------------+----------+----------+
    
### Additional remarks

This command doesn't handle _-s/--silent_ option.

## Notes


## Examples

_dlsctl list_

Displays all experiments submitted by a current user

_dlsctl list -m ^train_

Displays all experiments submitted by a current user and with name starting with _train_ word.

## Status

Planned
