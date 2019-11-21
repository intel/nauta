# template Command

The overall purpose of this command/subcommands is to manage template packs used by nctl application. This section discusses the following main topics: 

 - [copy Subcommand](#copy-subcommand)
 - [install Subcommand](#install-subcommand)  
 - [list Subcommand](#list-subcommand)
 
 
## copy Subcommand
  
 ### Synopsis
 
Copies a locally existing template pack to a new template pack. Once copied, you can change the description and the version of a newly created template pack, if desired.
 
 ### Syntax
 
 `nctl template copy [options] SRC_TEMPLATE_NAME DEST_TEMPLATE_NAME `
 
 
 ### Arguments
 
 | Name | Required | Description |
 |:--- |:--- |:--- |
 |`SRC_TEMPLATE_NAME` | Yes | This is the name of a template pack that will be copied. This pack must be available locally. Therefore, if a you want to make a copy of a remote template pack, you must first install it locally using the `template install command`. |
 |`DEST_TEMPLATE_NAME` | Yes | This is the name of the copied template pack. If a template pack with a given name exists, the Nauta application displays the information about it and completes its action. |
 
 
 ### Options
 
 | Name | Required | Description | 
 |:--- |:--- |:--- |
 |`-d, --description TEXT` | No | Description of a newly created template pack. If not given, `nctl` asks for a descritpion during copying of the pack. The maximum length of a description is 255 characters; however, if the text is longer than this limit, superfluous characters are cut.|
 |`-ve, --version TEXT`| No | Version of a newly created template pack. If not given, the default `0.1.0` value is used as a version. |
 
 
 ### Returns
 
When a template pack is copied successfully, a confirmation message displays.
If an error occurs during execution of this command, then the cause of the issue is displayed.
     
 ### Example
 
 `nctl template copy -ve 0.2.0 existing-pack new-pack`  
 
 Creates a new template pack named `new-pack` based on a locally available template pack `existing-pack`. The version
 of a newly created pack is set to 0.2.0. You will be asked for a description during _making a copy_ of a template pack.


## install Subcommand 

### <a name="synopsis_install"></a>Synopsis

Installs locally a template pack with a given name. If template pack has been already installed, use of this subcommand
updates the template to the version residing on a remote repository.  

### <a name="syntax_install"></a>Syntax

`nctl experiment install TEMPLATE_NAME`  

### <a name="arguments_install"></a>Arguments
 
 | Name | Required | Description |
 |:--- |:--- |:--- |
 |`TEMPLATE_NAME` | Yes | Name of a template pack which should be installed/updated. |

###  <a name="returns_install"> </a> Returns

When an installation/update is successfully completed, a confirmation message displays.
If an error occurs during execution of this command, then the cause of the issue is displayed.

###  <a name="example_install"> </a> Example

The following command installs/upgrade template with the `template-name` name.

`nctl template install template-name`

## list Subcommand

- [Synopsis](#synopsis_list)  
- [Syntax](#syntax_list)
- [Returns](#returns_list)
- [Example](#example_list)  

### <a name="synopsis_list"></a> Synopsis

Lists template packs. It displays information about packs that are available locally and on a remote repository. 

### <a name="syntax_list"> </a> Syntax

`nctl template list`

#### Additional Remarks

Configuration of the template zoo is stored in the `NAUTA_HOME/config/zoo-repository.config` file. This file 
contains location of a template zoo repository (under the `model-zoo-address` key). Additionally, it can contain
a Git access token also (under the `access-token` key). The access token is needed in case when a template zoo repository
is private and credentials are needed to get access to it. If desired, you can modify both values in case you need to use a different repository with template packs. 

### <a name="returns_list"></a>  Returns

Displays a table with a list of available template packs. Each row contains, besides the name and the description of a template, also 
versions of remote and local template packs. If one of these versions is empty it indicates that this template pack
does not have version of this type.

If an error occurs during execution of this command, then the cause of the issue is displayed.


### <a name="example_list"></a>  Example

`nctl template list`

<!-- language: lang-none -->

    | Template name                     | Template description                            | Local version   | Remote version   |
    |-----------------------------------+-------------------------------------------------+-----------------+------------------|
    | jupyter                           | Pack with Jupyter Notebook for purpose of       | 0.1.0           | 0.1.0            |
    |                                   | interactive sessions                            |                 |                  |
    | jupyter-py2                       | Pack with Jupyter Notebook for purpose of       | 0.1.0           | 0.1.0            |
    |                                   | interactive sessions                            |                 |                  |
    | tf-training-horovod               | A Helm chart for deploying Horovod              | 0.2.1           | 0.2.1            |
    | tf-training-horovod-py2           | A Helm chart for deploying Horovod              | 0.2.1           | 0.2.1            |

----------------------

## Return to Start of Document

* [README](../README.md)

----------------------

