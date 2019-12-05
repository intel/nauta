# mount Command

Use the `mount` command to display the operating system commands for mounting and unmounting Nauta folders. This main command also includes the following subcommand:

 - [list Subcommand](#list-subcommand)  

**Note:** _mount_ is an operating system command so it might be better to continue using `nctl mount` here. The command displays both the mount and unmount commands.

### Synopsis

The mount command by itself displays another command that can be used to mount/unmount a client's folders on or from a user's local machine. 

### Syntax

`nctl mount [options]`

### Options

| Name | Required | Description | 
|:--- |:--- |:--- |
|`-f, --force`| No | Ignore (most) confirmation prompts during command execution |
|`-v, --verbose`| No | Set verbosity level: <br>`-v` for INFO, <br>`-vv` for DEBUG |
|`-h, --help` | No | Displays help messaging information. |


### Returns 

This command returns another command that can be used to mount a client's folders on a user's local machine. It also shows what command should be used to unmount client's folder after it is no longer needed. 

## list Subcommand 

### Synopsis

Use the `list` subcommand to display a list of Nauta related folders mounted on a user's machine. If run using administrator credentials, it displays the mounts of all users.

### Syntax

`nctl mount list`

### Returns

List of mounted folders. Each row contains additional information (for example: remote and local location) concerning those mounts. Set of data displayed by this command depends on the operating system.

## Additional Remarks

This command displays only those mounts that expose Nauta shares. Other mounted folders _are not_ taken into account.

----------------------

## Return to Start of Document

* [README](../README.md)
----------------------
