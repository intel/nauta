# interact - launches an interactive session with Jupyter notebook

- [Synopsis](#synopsis)  
- [Arguments](#arguments)  
- [Options](#options)
- [Returns](#returns)
- [Examples](#examples)  
- [Status](#status)

## Synopsis

Launches a local browser with Jupyter notebook. If script's name is given as a parameter of a command - this script
is displayed in a notebook. Format of this command is as follows:

_dlsctl interact_

## Arguments

| Name | Obligatory | Description |
|:--- |:--- |:--- |
|_<script_name>_ | No | name of a script which should be put into Jupyter notebook. |

## Options

Table with description of options (if there are options in a certain command)

| Name | Obligatory | Description | 
|:--- |:--- |:--- |
|_-n/-name_ | No | name of a Jupyter notebook's session. If session with a given name already exists - a user is connected to this session. |

## Returns

In case of any problems - it displays a message with a description of causes of problems. Otherwise it launches a default web browser with Jupyter notebook.

## Examples

_dlsctl interact training_script.py_

Launches in a default browser a Jupyter notebook with _training_script.py_ script.

## Status

Planned
