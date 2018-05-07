# adduser - creates a new DLS4E user

- [Synopsis](#synopsis)  
- [Arguments](#arguments)  
- [Returns](#returns)
- [Notes](#notes)  
- [Examples](#examples)  
- [Status](#status)

## Synopsis

Creates and initializes a new DLS4E user. This command must be executed
when _kubectl_ used by _dlsctl_ command is in a context of k8s administrator. If this command
is executed using a context of other type of a user, it fails.

_dlsctl adduser <user_name>_

  


## Arguments

| Name | Obligatory | Description |
|:--- |:--- |:--- |
|_<user_name>_ | Yes | Name of a user that will be created. This value must a valid OS level user. |

## Returns

In case of any problems - message desribing their cause/causes. In case of a success \- message
that a user has been created. 

## Notes


## Examples

_dlsctl adduser jdoe_

Creates a _jdoe_ user.<br>


## Status

Under development
