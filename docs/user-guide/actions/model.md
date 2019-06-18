# model Command

The overall purpose of this command/subcommands is to manage model export related tasks. Following are the subcommands for the nctl model command.

 - [status Subcommand](#status-subcommand)
 - [export Subcommand](#export-subcommand)
 - [export-list Subcommand](#export-list-subcommand)
 - [process Subcommand](#process-subcommand)
 
## status Subcommand

### Synopsis
 
Displays a status of an export with a given name.
 
### Syntax
 
 `nctl model status [options] MODEL_NAME`

### Arguments

 | Name | Required | Description |
 |:--- |:--- |:--- |
 |`MODEL_NAME` | Yes | Name of an operation which status a user wants to display. |


### Options

 | Name | Required | Description | 
 |:--- |:--- |:--- |
 |`-s, --status` | No | Status of operation's steps that should be displayed together with other operation's information. |
 |`-u, --username` | No | Name of a user to whom viewed model belongs. If not given - only models of a current user are taken into account |
 

### Returns
 
Command displays information concerning a given operation, like name of an operation and steps belonging to it.

     
### Example
 
 `nctl model status openvinocrtl5`  
 
 
```
Model details:

| Workflow          | Start date           | End date             | Owner      | State     |
|-------------------+----------------------+----------------------+------------+-----------|
| openvinocrtl5     | 2019-02-25T12:21:52Z | 2019-02-25T12:22:56Z | jdoe      | Succeeded |

Model steps:

| Name              | Start date           | End date             | State     |
|-------------------+----------------------+----------------------+-----------|
| openvinocrtl5     | 2019-02-25T12:21:52Z | 2019-02-25T12:22:54Z | Succeeded |
```

Displays information about an operation containing one step

## export Subcommand

### Synopsis
 
Exports an existing model located in the PATH folder to a given FORMAT with given options.   
 
### Syntax
 
 `nctl model [options] export PATH FORMAT [-- workflow options]`
 
 
### Arguments
 
 | Name | Required | Description |
 |:--- |:--- |:--- |
 |`PATH` | Yes | Location of a model that is going to be exported. Models can be stored only in shared folders - this command doesn't handle models located in local folders. |
 |`FORMAT` | Yes | Format of an exported model. List of available formats can be obtained by executing `export-list` command. |
 |`workflow options` | No | String with a list of parameters that are passed to a workflow responsible for exporting a model. All such parameters should be added at the end of the command after `--` string. |
 

### Options
 
 | Name | Required | Description | 
 |:--- |:--- |:--- |
 |`-p, --process [kind]` | No | Kind of a postprocessing workflow template that should be used to process output from an export operation. |
 

### Returns
 
If an export's operation has started successfuly - information about that and a name of an export's operation. In case of problems - short description of their causes.

     
### Example
 
 `nctl model export /mnt/input/home/pretrained_model openvino -- --output ArgMax`  
 
 
```
Successfully created export workflow: openvinocrtl5
```

Exports an existing model located in the `pretrained_model` folder in `input` shared folder.


## export-list Subcommand

### Synopsis
 
Displays a list of available export formats.   
 
### Syntax
 
 `nctl model export-list` 
 

### Returns
 
List of available export formats.
     
### Example
 
 `nctl model export-list`  
 
 
```
| Name     |
|----------|
| openvino |
```

Displays a list of available export formats.

|`-t, --template` <br>`[template_name] TEXT`| No | Name of a template that will be used by `nctl` to create a description of a job to be submitted. If not given, a default template for single node TensorFlow* training is used (tf-training). A list of available templates can be obtained by executing the `nctl template list command` command. |


## process Subcommand

### Synopsis
 
Post-processes an existing model located in the PATH folder using a post-processing workflow named KIND.   
 
### Syntax
 
 `nctl model process PATH FORMAT [-- workflow options]`
 
 
### Arguments
 
 | Name | Required | Description |
 |:--- |:--- |:--- |
 |`PATH` | Yes | Location of a model that is going to be processed. Models can be stored only in shared folders - this command doesn't handle models located in local folders. |
 |`KIND` | Yes | Kind of a postprocessing workflow template that should be used to process a given model. List of available post-processing kinds can be obtained by executing `process-list` command. |
 |`workflow options` | No | String with a list of parameters that are passed to a workflow responsible for post-processing a model. All such parameters should be added at the end of the command after `--` string. |


### Returns
 
If a post-processing operation has started successfuly - information about that and a name of an operation. In case of problems - short description of their causes.

     
### Example
 
 `nctl model process /mnt/input/home/pretrained_model copy-model`  
 
 
```
Successfully created export workflow: copy-modelabc3 

```

Processes an existing model located in the `pretrained_model` folder in `input` shared folder.
