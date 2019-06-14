# template Command

The overall purpose of this command/subcommands is to manage template packs used by nctl application. This section discusses the following main topics: 

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
 
Copies a template pack existing locally to a new one. You can change a desription and a versoin of a newly created template pack.
 
 ### Syntax
 
 `nctl template copy [options] SRC_TEMPLATE_NAME DEST_TEMPLATE_NAME `
 
 
 ### Arguments
 
 | Name | Required | Description |
 |:--- |:--- |:--- |
 |`SRC_TEMPLATE_NAME` | Yes | Name of a template pack that will be copied. This pack must be available locally; so, if a you want to make a copy of a remote template pack, you _must_ first install it locally (using `template install` command. |
 |`DEST_TEMPLATE_NAME` | Yes | Name of the copied template pack. If template pack with a given name exists, application displays an information about it and finishes action. |
 
 
 ### Options
 
 | Name | Required | Description | 
 |:--- |:--- |:--- |
 |`-d, --description TEXT` | No | Description of a newly created template pack. If not given, `nctl` asks for a descritpion during copying of the pack. The maximum length of a description is 255 characters; however, if the text is longer than this limit, superfluous characters are cut.|
 |`-ve, --version TEXT`| No | Version of a newly created template pack. If not given, the default `0.1.0` value is used as a version. |
 
 
 ### Returns
 
In case of success of a copying of a template pack, message about it.
In case of any errors during execution of this command, a proper message containing causes of problems will be displayed.
     
 ### Example
 
 `nctl template -ve 0.2.0 existing-pack new-pack`  
 
 Creates a new template pack: names `new-pack` based on a locally available template pack `existing-pack`. The version
 of a newly created pack is set to 0.2.0. You will be asked for a description during _making a copy_ of a template pack.


## install Subcommand

- [Synopsis](#synopsis_list)
- [Syntax](#syntax_list)
- [Arguments](#arguments)
- [Returns](#returns_list)
- [Example](#example_list)  

### <a name="synopsis_list"></a>Synopsis

Installs locally a template pack with a given name. If template pack has been already installed, use of this subcommand
updates it to the version residing on a remote repository.  

### <a name="syntax_list"></a>Syntax

`nctl experiment install TEMPLATE_NAME`  

### <a name="arguments"></a>Arguments
 
 | Name | Required | Description |
 |:--- |:--- |:--- |
 |`TEMPLATE_NAME` | Yes | Name of a template pack which should be installed/updated. |

###  <a name="returns_list"> </a> Returns

In case of success of installation/update, message about it.
In case of any errors during execution of this command, a proper message containing causes of problems will be displayed.

###  <a name="example_list"> </a> Examples

The following command installs/upgrade template with `template-name` name.

`nctl template template-name`

## list Subcommand

- [Synopsis](#synopsis_cancel)  
- [Syntax](#syntax_cancel)
- [Returns](#returns_cancel)
- [Example](#example_cancel)  

### <a name="synopsis_cancel"></a> Synopsis

Lists template packs. It displays information about pack that are available locally and on a remote repository. 

### <a name="syntax_cancel"> </a> Syntax

`nctl template-list`

#### Additional Remarks

Configuration of the template zoo is stored in the `NAUTA_HOME/config/zoo-repository.config` file. This file 
contains location of a template zoo repository (under the `model-zoo-address` key). Additionally, it can contain
a Git access token also (under the `access-token` key). The access token is needed in case when a template zoo repository
is private and credentials are needed to get access to it. However, you can modify both values in case you need to use a different repository with template packs. 

### <a name="returns_cancel"></a>  Returns

Table with a list of available template packs. Each row contains beside name and description of a template also 
versions of remote and local template packs. If one of these versions is empty it indicates that this template pack
does not have this certain version.

<!-- language: lang-none -->

    | Template name                     | Template description                            | Local version   | Remote version   |
    |-----------------------------------+-------------------------------------------------+-----------------+------------------|
    | jupyter                           | Pack with Jupyter Notebook for purpose of       | 0.1.0           | 0.1.0            |
    |                                   | interactive sessions                            |                 |                  |
    | jupyter-py2                       | Pack with Jupyter Notebook for purpose of       | 0.1.0           | 0.1.0            |
    |                                   | interactive sessions                            |                 |                  |
    | multinode-tf-training-horovod     | A Helm chart for deploying Horovod              | 0.2.1           | 0.2.1            |
    | multinode-tf-training-horovod-py2 | A Helm chart for deploying Horovod              | 0.2.1           | 0.2.1            |


In case of any errors during execution of this command, a proper message containing causes of problems will be displayed. 

### <a name="example_cancel"></a>  Example

`nctl template-list`

----------------------

## Return to Start of Document

* [README](../README.md)

----------------------

