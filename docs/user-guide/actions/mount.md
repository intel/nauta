# mount Command

The `dlsctl mount` command displays another command that can be used to either mount or unmount a client's folders on/from his/her local machine. See also, [list Subcommand](#list-subcommand).

- [Synopsis](#synopsis)  
- [Syntax](#syntax)
- [Options](#options)
- [Returns](#returns)

## Synopsis

The mount command by itself displays another command that can be used to mount/unmount a client's folders on or from his/her local machine. 

## Syntax

`dlsctl mount [options]`

## Options

| Name | Required | Description | 
|:--- |:--- |:--- |
|`-l, --list ` | No |  Displays a list of Intel Dl Studio folders mounted on a local machine. If run using admin credentials, displays mounts of all users. Data displayed by this command depends on the operating system. |
|`-v, --verbose`| No | Set verbosity level: <br>`-v` for INFO, <br>`-vv` for DEBUG |
|`-h, --help` | No | Show help message and exit. |


## Returns 

This command returns another command that can be used to mount a client's folders on his/her local machine. It also shows what command should be used to unmount client's folder after it is not longer needed. 

## list Subcommand

### Synopsis

Displays a list of Intel DL Studio related folders mounted on a user's machine.

### Syntax

`dlsctl mount list`

### Returns
List of mounted folders. Each row contains additional information (i.e. remote and local location) concerning those mounts. Set of data displayed by this command depends on operating system.

### Additional Remarks
This command displays only those mounts that exposing Intel DL Studio shares. Other mounted folders are not taken into account.
