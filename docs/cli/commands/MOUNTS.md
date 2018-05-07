# mounts - mounts a user's directory on a local machine

- [Synopsis](#synopsis)  
- [Arguments](#arguments)  
- [Options](#options)
- [Returns](#returns)
- [Notes](#notes)  
- [Examples](#examples)  
- [Status](#status)

## Synopsis

Command used to perform mounting of a user's directory on a local machine. By defaults, provides detailed 
commands necessary to mount volumes. With --auto flag, performs mounting automatically (with sudo if needed).

_dlsctl mounts_

## Arguments

| Name | Obligatory | Description |
|:--- |:--- |:--- |
|_<mountpath>_ | No | Location under whihc user's directory will be mounted on a local machine. If not given - directory is mounted as a _/mnt/dlshome_.  |

## Options

| Name | Obligatory | Description | 
|:--- |:--- |:--- |
|_--auto_ | No | If given - command mounts user's directory automatically. |

## Returns

If _--auto_ option is not given - command that should be issued by a user to mount his/her directory on a local machine.  
If _--auto_ option is given - information that _mount_ command has been executed is displayed.


## Examples

_dlsctl mounts /mnt/example_folder --auto_

Mounts user's directory automatically under the following location: _/mnt/example_folder_.

## Status

Under development.
