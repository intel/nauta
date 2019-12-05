# template Command

Use the `template` command to manage the template packs used by nctl application. This main command also includes the following subcommands:

 - [copy Subcommand](#copy-subcommand)
 - [install Subcommand](#install-subcommand)  
 - [list Subcommand](#list-subcommand)
  
## copy Subcommand
  
### Synopsis
 
Use the `copy` subcommand to copy a locally existing template pack to a new template pack. Once copied, you can change the description and the version of a newly created template pack, if desired.
 
### Syntax
 
`nctl template copy [options] SRC_TEMPLATE_NAME DEST_TEMPLATE_NAME `
 
### Arguments
 
| Name | Required | Description |
|:--- |:--- |:--- |
|`SRC_TEMPLATE_NAME` | Yes |  This is the name of a template pack that will be copied. This pack _must be_ available locally. Therefore, if a you want to make a copy of a remote template pack, _you must_ first install it locally using the `template install command`. |
|`DEST_TEMPLATE_NAME` | Yes | This is the name of the copied template pack. If a template pack with a given name exists, the Nauta application displays the information about it and completes its action. |
 
### Options
 
 Name | Required | Description | 
:--- |:--- |:--- |
|`-d, --description TEXT` | No | A description of a newly created template pack. If not given, `nctl` asks for a description during copying of the pack. The maximum length of a description is 255 characters. As a result, if longer text is used, superfluous characters are cut.|
|`-ve, --version TEXT`| No | The version of a newly created template pack. If not given, the default `0.1.0` value is used as a version. |
|`-f, --force`| No | Force command execution by ignoring (most) confirmation prompts |
|`-v, --verbose`| No | Set verbosity level: <br>`-v` for INFO, <br>`-vv` for DEBUG |
|`-h, --help` | No | Displays help messaging information. |
 
 
### Returns
 
When a template pack is copied successfully, a confirmation message displays. If an error occurs during execution of this command, the cause of the issue displays.
     
### Example
 
`nctl template copy --version 0.2.0 existing-pack new-pack`  

### Additional Remarks
 
Use the subcommand to create a new template pack named `new-pack` based on a locally available template pack `existing-pack`. The version of a newly created pack is set to 0.2.0. You will be asked for a description during _making a copy_ of a template pack.

## install Subcommand

### Synopsis

Use the `install` subcommand to install a template pack locally with a given name. If the template pack has been already installed, use this subcommand to update the template to the version residing on a remote repository.  

### Syntax

`nctl template install TEMPLATE_NAME`  

### Arguments
 
| Name | Required | Description |
|:--- |:--- |:--- |
|`TEMPLATE_NAME` | Yes | The name of a template pack that should be installed/updated, as required. |

### Returns

When an installation/update is successfully completed, a confirmation message displays. If an error occurs during execution of this command, the cause of the issue displays.

### Example

`nctl template install template-name`

 ### Options
 
| Name | Required | Description | 
|:--- |:--- |:--- |
|`-f, --force`| No | Force command execution by ignoring (most) confirmation prompts |
|`-v, --verbose`| No | Set verbosity level: <br>`-v` for INFO, <br>`-vv` for DEBUG |
|`-h, --help` | No | Displays help messaging information. |

### Additional Remarks

The following command installs/upgrade template with `template-name` name.

## list Subcommand

### Synopsis

Use the `list` subcommand to list the template packs and display information about the available local packs on a remote repository. 

### Syntax

`nctl template list`


| Name | Required | Description | 
|:--- |:--- |:--- |
|`-f, --force`| No | Force command execution by ignoring (most) confirmation prompts |
|`-v, --verbose`| No | Set verbosity level: <br>`-v` for INFO, <br>`-vv` for DEBUG |
|`-h, --help` | No | Displays help messaging information. |

### Additional Remarks

The configuration of the _template zoo_ is stored in the `NAUTA_HOME/config/zoo-repository.config` file. This file 
contains location of a template zoo repository (under the `model-zoo-address` key). 

Additionally, it can contain also a git access token (under the `access-token` key). The access token is needed in case when a template zoo repository is private, and credentials are needed to get access to it. A user can modify both values if needed to use a different repository with template packs. 

### Returns

The table lists the available template packs. Each row contains the name and the description of a template (as well as 
the versions) of remote and local template packs. If one of these versions is empty, this indicates that this template pack
_does not_ have this certain version.


```

| Template name             | Template description                              | Local version   | Remote version   |
|---------------------------+---------------------------------------------------+-----------------+------------------|
| jupyter                   | An interactive session based on Jupyter Notebook  | 0.1.0           | 0.1.0            |
|                           | using Python 3.                                   |                 |                  |
|                           |                                                   |                 |                  | 
| openvino-inference-batch  | An OpenVINO model server inference job for batch  | 0.1.0           | 0.1.0            |
|                           | predictions.                                      |                 |                  |
|                           |                                                   |                 |                  |  
| openvino-inference-stream | An OpenVINO model server inference job for        | 0.1.0           | 0.1.0            |
|                           | streaming predictions on a deployed instance.     |                 |                  |
|                           |                                                   |                 |                  | 
| pytorch-training          | A PyTorch multi-node training job using Python 3. | 0.0.1           | 0.0.1            |
|                           |                                                   |                 |                  | 
| tf-inference-batch        | A TensorFlow Serving inference job for batch      | 0.1.0           | 0.1.0            |
|                           | predictions.                                      |                 |                  |
|                           |                                                   |                 |                  | 
| tf-inference-stream       | A TensorFlow Serving inference job for streaming  | 0.1.0           | 0.1.0            |
|                           | predictions on a deployed instance.               |                 |                  |
|                           |                                                   |                 |                  | 
| tf-training-horovod       | A TensorFlow multi-node training job based on     | 0.2.2           | 0.2.2            |
|                           | Horovod using Python 3.                           |                 |                  |
|                           |                                                   |                 |                  | 
| tf-training-multi         | A TensorFlow multi-node training job based on     | 0.1.0           | 0.1.0            |
|                           | TfJob using Python 3.                             |                 |                  |
|                           |                                                   |                 |                  | 
| tf-training-single        | A TensorFlow single-node training job based on    | 0.1.0           | 0.1.0            |
|                           | TfJob using Python 3.                             |                 |                  |
```

**Note:** If an error occurs during execution of this command, the cause of the issue displays.

----------------------

## Return to Start of Document

* [README](../README.md)
----------------------
