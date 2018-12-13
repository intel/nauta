# user Commands

Use this command to create, delete, and manage users.

 - [create Subcommand](#create-subcommand)  
 - [delete Subcommand](#delete-subcommand)
 - [list Subcommand](#list-subcommand)

## create Subcommand

- [Synopsis](#synopsis)  
- [Syntax](#syntax)
- [Arguments](#arguments)  
- [Options](#options)
- [Returns](#returns)
- [Notes](#notes)
- [Examples](#examples)  

### Synopsis

Creates and initializes a new DLS4E user. This command must be executed when `kubectl` used by `dlsctl` command entered by a k8s administrator. If this command is executed by someone other than a k8s administrator, it fails. By default this command saves a configuration of a newly created user to a file. The format of this file is compliant with a format of `kubectl`  configuration files.

### Syntax

`dlsctl user create [options] USERNAME`

### Arguments

| Name | Required | Description |
|:--- |:--- |:--- |
|`USER_NAME` | Yes | Name of a user that will be created. This value must a valid OS level user. |

### Options

| Name | Required | Description | 
|:--- |:--- |:--- |
|`-l, --list_only` | No | If given - content of the generated user's config file is displayed on the screen only. <br> If not given - file with configuration is saved on disk.|
|`-f, --filename` <br> `TEXT`  | No | Name of file where user's configuration will be stored. If not given <br> configuration is stored in the `config.<username>` file.|
|`-v, --verbose`| No | Set verbosity level: <br>`-v` for INFO, <br>`-vv` for DEBUG |
|`-h, --help` | No | Show help message and exit. |


### Additional remarks

In case of any errors during saving of a file with a configuration - the command displays a content of the configuration file on the screen - even if `-l` option wasn't chosen.  

If an admin tries to create a user with a name that was used previously by a deleted user - it may happen, that 
the `create` command displays information that the previous user is still being deleted - even if the previous
user is not listed on a list of existing users. In this case the operation of a creation of a new user should be
postponed for a while - until all user's objects are removed.

### Returns

In case of any problems - message describing their cause/causes. Otherwise message is returned indicating success. If -list_only option was given - the command displays also a content of a configuration file. 

### Notes

User name must meet the following rules:
1) Cannot be longer than 32 characters.
2) Cannot be an empty string.
3) Must conform to kubernetes naming convention - can contain only lower case alphanumeric 
characters and "-" and "."

### Example

`dlsctl user create jdoe`

Creates user `jdoe`.

## delete Subcommand

- [Synopsis](#synopsis_delete)
- [Syntax](#syntax_delete)
- [Arguments](#arguments_delete)  
- [Options](#options_delete)
- [Returns](#returns_delete)
- [Examples](#examples_delete)  

### <a name="synopsis_delete"></a>Synopsis

This command deletes a user with a given name. If option `-p`, `--purge` was used - it also removes all artifacts related to that removed user, such as the content of user's folders and data of experiments and runs.

Before removing a user, the commands asks for a final confirmation. If user chooses `Yes` - chosen user is deleted.  
Deletion of a user may take a while to be fully completed. The command requires up to 60 seconds for a complete
removal of user. If after this time user hasn't been deleted completely - the command displays information that a
user is still being deleted. In this case the user won't be listed on a list of existing users, but there is no
possibility to create a user with the same name until the command completes and the user is deleted.

### <a name="syntax_delete"></a> Syntax

` dlsctl user delete [options] USERNAME`

### <a name="arguments_delete"></a>Arguments

| Name | Required | Description |
|:--- |:--- |:--- |
|`USERNAME` | Yes | Name of a user who to be removed from the Intel DL Studio user accounts. |

### <a name="options_delete"></a>Options

| Name | Required | Description | 
|:--- |:--- |:--- |
|`-p, --purge` | No | Removes all artifacts related to that user. |
|`-v, --verbose`| No | Set verbosity level: <br>`-v` for INFO, <br>`-vv` for DEBUG |
|`-h, --help` | No | Show help message and exit. |


### <a name="returns_delete"></a>Returns

A message regarding the command's completion. In case of any problems - short description of their causes.


### <a name="examples_delete"></a> Examples

`dlsctl user delete jdoe -p`

Removes `jdoe` user with all his/her artifacts.

## list Subcommand

- [Synopsis](#synopsis_list)
- [Syntax](#syntax_list)
- [Arguments](#arguments_list)  
- [Options](#options_list)

### <a name="synopsis_list"></a>Synopsis

Lists all currently configured users.


### <a name="syntax_list"></a>Syntax

`dlsctl user list [options]`

### <a name="arguments_list"></a>Arguments

None.

### <a name="options_list"></a>Options

| Name | Required | Description | 
|:--- |:--- |:--- |
|`-c, --count` <br> `INTEGER RANGE` | No | If given - command displays c last rows. |
|`-v, --verbose`| No | Set verbosity level: <br>`-v` for INFO, <br>`-vv` for DEBUG |
|`-h, --help` | No | Show help message and exit. |





