# model Command

Use the `model` command to manage model export related tasks. Use the `model` command to manage model export related tasks. The `model`command has the following subcommands:

 - [status Subcommand](#status-subcommand)
 - [export Subcommand](#export-subcommand)
 - [logs Subcommand](#logs-subcommand)
 
## status Subcommand

### Synopsis
 
Displays a list of model export operations with their statuses, dates of start and finish, and the users who submitted those operations.
 
### Syntax
 
 `nctl model status [options]`
 

### Options

| Name | Required | Description | 
|:--- |:--- |:--- |
|`-u, --username` | No | Name of a user to whom viewed operations belongs. If not given, only models of a current user are taken into account. |
|`-f, --force`| No | Force command execution by ignoring (most) confirmation prompts |
|`-v, --verbose`| No | Set verbosity level: <br>`-v` for INFO, <br>`-vv` for DEBUG |
|`-h, --help` | No | Displays help messaging information. |
 

### Returns
 
This command displays a list of operations with their statuses, dates of start and finish, and displays the users who submitted those operations.

     
### Example
 
 `nctl model status`  
 
 
```
| Operation                                          | Start date           | End date             | Owner     | State     |
|----------------------------------------------------+----------------------+----------------------+-----------+-----------|
| openvino_1                                         | 2019-07-15T11:59:56Z | 2019-07-15T12:00:02Z | jdoe      | Succeeded |
| openvino_2                                         | 2019-07-02T14:39:38Z | 2019-07-02T14:39:47Z | jdoe      | Failed    |
| openvino_3                                         | 2019-07-16T14:29:54Z | 2019-07-16T14:30:00Z | jdoe      | Succeeded |

```

Displays details of 3 model export operations: two of them finished with success, one failed.

## export Subcommand

### Synopsis
 
Exports an existing model located in the `PATH` folder to a given `FORMAT` with given options. If the`formats` option is given, it displays a list of available export formats.    

### Syntax
 
 `nctl model export PATH/formats FORMAT [-- operation options]`
  
 ### Options

| Name | Required | Description | 
|:--- |:--- |:--- |
|`-u, --username` | No | Name of a user to whom viewed operations belongs. If not given, only models of a current user are taken into account. |
|`-f, --force`| No | Force command execution by ignoring (most) confirmation prompts |
|`-v, --verbose`| No | Set verbosity level: <br>`-v` for INFO, <br>`-vv` for DEBUG |
|`-h, --help` | No | Displays help messaging information. |
 
### Arguments
 
 | Name | Required | Description |
 |:--- |:--- |:--- |
 |`PATH/formats` | Yes | `PATH` - The location of a model that is going to be exported. Models can be stored `only` in shared folders. Furthermore, this command _does not_ handle models located in local folders. The formats command (if given) displays a list of available formats.|
 |`FORMAT` | No | Format of an exported model. List of available formats can be obtained by executing `export formats` command. Required if `PATH` has been given.|
 |`operation options` | No | String with a list of parameters that are passed to a workflow responsible for exporting a model. All such parameters should be added at the end of the command after `--` string. |
 

### Returns
 
Should issues occur, a message (or messages) with a description of their cause (or causes) displays. If an export's operation starts, then the related operation information and its details displays.
If `formats` option is given, a list of available export formats with a short description of parameters accepted by those formats displays.
     
### Example 1

 Wait for Tensorboard to run.
 
 `nctl model export /mnt/input/home/pretrained_model openvino -- --output ArgMax` 
 
### Output 1

```
| Operation     | Start date           | End date   | Owner     | State   |
|---------------+----------------------+------------+-----------+---------|
| openvino_1    | 2019-07-17T16:13:40Z |            | jdoe      | Queued  |

Successfully created export workflow

```

### Example 2

Exports an existing model located in the `pretrained_model` folder in `input` shared folder.

 `nctl model export formats`
 
 ### Output 2
 
 Displays a list of available export formats with a short description of parameters accepted by them.  
 
 ```
| Name     | Parameters description                                                       |
|----------+------------------------------------------------------------------------------|
| openvino | --input_shape [x,y,....] - shape of an input                                 |
|          | --input [name] - names of input layers                                       |
|          | --output [name] - names of output layers                                     |
|          | Rest of parameters can be found in a description of OpenVino model optimizer |

```

## logs Subcommand

### Synopsis

The `logs` subcommand displays logs from a model export operation. Logs to be displayed are chosen based on parameters given in the command's call.

### Syntax

`nctl model logs [options] OPERATION-NAME`

### Arguments

| Name | Required | Description |
|:--- |:--- |:--- |
|`OPERATION-NAME` | Yes | Name of an operation for which logs are displayed. |

### Options

| Name | Required | Description | 
|:--- |:--- |:--- |
|`-sd, --start-date` | No | Retrieve logs produced from this date (format ISO-8061 - yyyy-mm-ddThh:mm:ss).|
|`-ed, --end-date` | No | retrieve logs produced until this date (format ISO-8061 - yyyy-mm-ddThh:mm:ss).|
|`-m, --match TEXT` | No |  If given, this command searches for logs from operations matching the value of this option. This option cannot be used along with the OPERATION-NAME argument.|
|`-o, --output` | No |  If given, the logs are stored in a file with a name derived from a name of an experiment.|
|`-pa, --pager` | No | Display the logs in interactive pager. Press *q* to exit the pager.|
|`-fl, --follow` | No | Specifies if the logs should be streamed. Only logs from a single experiment can be streamed.|
|`-f, --force`| No | Force command execution by ignoring (most) confirmation prompts. |
|`-v, --verbose`| No | Set verbosity level: <br>`-v` for INFO, <br>`-vv` for DEBUG |
|`-h, --help` | No | Displays help messaging information. |


### Returns

Should issues occur, a message (or messages) containing a description of their cause (or causes) displays. Otherwise, the logs are filtered based on command's parameters.

### Example

`nctl model logs openvino_2`

Displays logs from `openvino_2` model export operation.

----------------------

## Return to Start of Document

* [README](../README.md)
----------------------
