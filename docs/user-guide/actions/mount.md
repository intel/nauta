# mount Command

The `nctl mount` command displays another command that can be used to either mount or unmount a client's folders on/from a users local machine. See also, [list Subcommand](#list-subcommand-synopsis).

This section discusses the following main topics: 

 - [mount Command Synopsis](#mount-command)
 - [list Subcommand Synopsis](#list-subcommand-synopsis)  
 - [Additional Remarks](#additional-remarks)

## mount Command 

The mount command by itself displays another command that can be used to mount/unmount a client's folders on or from a users local machine. 

### Syntax

`nctl mount [options]`

### Options

| Name | Required | Description | 
|:--- |:--- |:--- |
|`-f, --force`| No | Ignore (most) confirmation prompts during command execution |
|`-v, --verbose`| No | Set verbosity level: <br>`-v` for INFO, <br>`-vv` for DEBUG |
|`-h, --help` | No | Displays help messaging information. |

### Returns 

This command returns another command that can be used to mount a client's folders on a users local machine. It also shows what command should be used to unmount client's folder after it is no longer needed. 

## list Subcommand Synopsis

Displays a list of Nauta related folders mounted on a user's machine. If run using admin credentials, it displays mounts of all users.

### Syntax

`nctl mount list`

### Returns

List of mounted folders. Each row contains additional information (for example, remote and local location) for those mounts. 

**Note:** The data sets displayed by this command depends on operating system used.

## Additional Remarks

This command displays only those mounts that expose Nauta shares. Other mounted folders _are not_ taken into account.


----------------------

## Return to Start of Document

* [README](../README.md)

----------------------
