# template Command

Use the `template` command to manage the template packs used by nctl application. This main command also includes the following subcommands:

 - [copy Subcommand](#copy-subcommand)
 - [install Subcommand](#install-subcommand)  
 - [list Subcommand](#list-subcommand)
 
 
## copy Subcommand
 
 - [Synopsis](#synopsis)
 - [Syntax](#syntax)
 - [Arguments](#arguments)  
 - [Options](#options)
 - [Returns](#returns)
 - [Examples](#examples)  
  
 ### Synopsis
 
This subcommand Copies a locally existing template pack to a new template pack. Once copied, you can change the description and the version of a newly created template pack, if desired.
 
 ### Syntax
 
 `nctl template copy [options] SRC_TEMPLATE_NAME DEST_TEMPLATE_NAME `
 
 
 ### Arguments
 
 | Name | Required | Description |
 |:--- |:--- |:--- |
 |`SRC_TEMPLATE_NAME` | Yes |  This is the name of a template pack that will be copied. This pack _must be_ available locally. Therefore, if a you want to make a copy of a remote template pack, _you must_ first install it locally using the `template install command`. |
 |`DEST_TEMPLATE_NAME` | Yes | This is the name of the copied template pack. If a template pack with a given name exists, the Nauta application displays the information about it and completes its action. |
 
 
 ### Options
 
 | Name | Required | Description | 
 |:--- |:--- |:--- |
 |`-d, --description TEXT` | No | A description of a newly created template pack. If not given, `nctl` asks for a descritpion during copying of the pack. The maximum length of a description is 255 characters. As a result, if longer text is used, superfluous characters are cut.|
 |`-ve, --version TEXT`| No | The version of a newly created template pack. If not given, the default `0.1.0` value is used as a version. |
 
 
 ### Returns
 
When a template pack is copied successfully, a confirmation message displays. If an error occurs during execution of this command, the cause of the issue displays.
     
 ### Example
 
`nctl template -ve 0.2.0 existing-pack new-pack`  
 
This subcommand creates a new template pack named `new-pack` based on a locally available template pack `existing-pack`. The version of a newly created pack is set to 0.2.0. You will be asked for a description during _making a copy_ of a template pack.

## install Subcommand

- [Synopsis](#synopsis_list)
- [Syntax](#syntax_list)
- [Arguments](#arguments)
- [Returns](#returns_list)
- [Example](#example_list)  

### <a name="synopsis_list"></a>Synopsis

This subcommand installs a template pack locally with a given name. If the template pack has been already installed, use of this subcommand to update the template to the version residing on a remote repository.  

### <a name="syntax_list"></a>Syntax

`nctl experiment install TEMPLATE_NAME`  

### <a name="arguments"></a>Arguments
 
 | Name | Required | Description |
 |:--- |:--- |:--- |
 |`TEMPLATE_NAME` | Yes | The name of a template pack that should be installed/updated, as required. |

###  <a name="returns_list"> </a> Returns

When an installation/update is successfully completed, a confirmation message displays. If an error occurs during execution of this command, the cause of the issue displays.

###  <a name="example_list"> </a> Examples

The following command installs/upgrade template with `template-name` name.

`nctl template template-name`

## list Subcommand

- [Synopsis](#synopsis_cancel)  
- [Syntax](#syntax_cancel)
- [Returns](#returns_cancel)
- [Example](#example_cancel)  

### <a name="synopsis_cancel"></a> Synopsis

This subcommand lists the template packs and displays information about the available local packs on a remote repository. 

### <a name="syntax_cancel"> </a> Syntax

`nctl template list`

#### Additional Remarks

The configuration of the _template zoo_ is stored in the `NAUTA_HOME/config/zoo-repository.config` file. This file 
contains location of a template zoo repository (under the `model-zoo-address` key). 

Additionally, it can contain also a git access token (under the `access-token` key). The access token is needed in case when a template zoo repository is private, and credentials are needed to get access to it. A user can modify both values if needed to use a different repository with template packs. 

### <a name="returns_cancel"></a>  Returns

The table lists the available template packs. Each row contains beside name and description of a template and also 
the versions of remote and local template packs. If one of these versions is empty, this indicates that this template pack
_does not_ have this certain version.

<!-- language: lang-none -->

    | Template name                     | Template description                            | Local version   | Remote version   |
    |-----------------------------------+-------------------------------------------------+-----------------+------------------|
    | jupyter                           | Pack with Jupyter Notebook for purpose of       | 0.1.0           | 0.1.0            |
    |                                   | interactive sessions                            |                 |                  |
    | jupyter-py2                       | Pack with Jupyter Notebook for purpose of       | 0.1.0           | 0.1.0            |
    |                                   | interactive sessions                            |                 |                  |
    | multinode-tf-training-horovod     | A Helm chart for deploying Horovod              | 0.2.1           | 0.2.1            |
    | multinode-tf-training-horovod-py2 | A Helm chart for deploying Horovod              | 0.2.1           | 0.2.1            |


 If an error occurs during execution of this command, the cause of the issue displays.

### <a name="example_cancel"></a>  Example

`nctl template list`

----------------------

## Return to Start of Document

* [README](../README.md)
----------------------


