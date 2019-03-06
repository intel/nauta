# mount Command

The `nctl mount` command displays another command that can be used to either mount or unmount a client's folders on/from a user's local machine. See also, [list Subcommand](#list-subcommand).

## Synopsis

The mount command by itself displays another command that can be used to mount/unmount a client's folders on or from a user's local machine. 

## Syntax

`nctl mount [options]`

## Options

| Name | Required | Description | 
|:--- |:--- |:--- |
|`-v, --verbose`| No | Set verbosity level: <br>`-v` for INFO, <br>`-vv` for DEBUG |
|`-h, --help` | No | Show help message and exit. |


## Returns 

This command returns another command that can be used to mount a client's folders on a user's local machine. It also shows what command should be used to unmount client's folder after it is no longer needed. 

## list Subcommand

### Synopsis

Displays a list of Nauta related folders mounted on a user's machine. If run using admin credentials, displays mounts of all users.

### Syntax

`nctl mount list`

### Returns

List of mounted folders. Each row contains additional information (for example: remote and local location) concerning those mounts. Set of data displayed by this command depends on operating system.

### Additional Remarks

This command displays only those mounts that exposing Nauta shares. Other mounted folders _are not_ taken into account.





