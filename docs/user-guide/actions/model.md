# model Command

Use the `model` command to manage model export related tasks. Following are the subcommands for the `nctl model` command. This main command also includes the following subcommands:

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
 |`-u, --username` | No | Name of a user to whom viewed operations belongs. If not given, only models of a current user are taken into account |
 

### Returns
 
Command displays a list of operations with their statuses, dates of start and finish and the users who submitted those operations.

     
### Example
 
 `nctl model status`  
 
 
```
| Operation                                          | Start date           | End date             | Owner     | State     |
|----------------------------------------------------+----------------------+----------------------+-----------+-----------|
| openvino_1                                         | 2019-07-15T11:59:56Z | 2019-07-15T12:00:02Z | jdoe      | Succeeded |
| openvino_2                                         | 2019-07-02T14:39:38Z | 2019-07-02T14:39:47Z | jdoe      | Failed    |
| openvino_3                                         | 2019-07-16T14:29:54Z | 2019-07-16T14:30:00Z | jdoe      | Succeeded |

```

Displays details of 3 model export operations - two of them finished with success, one failed.

## export Subcommand

### Synopsis
 
Exports an existing model located in the PATH folder to a given FORMAT with given options. If `formats` option is given, it displays a list of available export formats.    
 
### Syntax
 
 `nctl model export PATH/formats FORMAT [-- operation options]`
 
 
### Arguments
 
 | Name | Required | Description |
 |:--- |:--- |:--- |
 |`PATH/formats` | Yes | `PATH` - Location of a model that is going to be exported. Models can be stored `only` in shared folders. Furthermore, this command `does not` handle models located in local folders. `formats` - if given, command displays a list of available formats.|
 |`FORMAT` | No | Format of an exported model. List of available formats can be obtained by executing `export formats` command. Required if `PATH` has been given.|
 |`operation options` | No | String with a list of parameters that are passed to a workflow responsible for exporting a model. All such parameters should be added at the end of the command after `--` string. |
 

### Returns
 
Should issues arise, a message (or messages) with a description of their cause (or causes) displays. If an export's operation starts, then the information about that operation and its details displays.
If `formats` option is given - a list of available export formats with a short description of parameters accepted by those formats displays.
     
### Example
 
 `nctl model export /mnt/input/home/pretrained_model openvino -- --output ArgMax`  Please wait for Tensorboard to run
 
 
```
| Operation     | Start date           | End date   | Owner     | State   |
|---------------+----------------------+------------+-----------+---------|
| openvino_1    | 2019-07-17T16:13:40Z |            | jdoe      | Queued  |

Successfully created export workflow

```

Exports an existing model located in the `pretrained_model` folder in `input` shared folder.

 `nctl model export formats`
 
 ```
| Name     | Parameters description                                                       |
|----------+------------------------------------------------------------------------------|
| openvino | --input_shape [x,y,....] - shape of an input                                 |
|          | --input [name] - names of input layers                                       |
|          | --output [name] - names of output layers                                     |
|          | Rest of parameters can be found in a description of OpenVino model optimizer |

```

Displays a list of available export formats with a short description of parameters accepted by them.  


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
|`-m, --match TEXT` | No |  If given, command searches for logs from operations matching the value of this option. This option cannot be used along with the OPERATION-NAME argument.|
|`-o, --output` | No |  If given, logs are stored in a file with a name derived from a name of an experiment.|
|`-pa, --pager` | No | Display logs in interactive pager. Press *q* to exit the pager.|
|`-fl, --follow` | No | Specify if logs should be streamed. Only logs from a single experiment can be streamed.|
|`-f, --force`| No | Ignore (most) confirmation prompts during command execution |
|`-v, --verbose`| No | Set verbosity level: <br>`-v` for INFO, <br>`-vv` for DEBUG |
|`-h, --help` | No | Displays help messaging information. |


### Returns

Should issues arise, a message (or messages) with a description of their cause (or causes) displays. Otherwise, the logs are filtered based on command's parameters.

### Example

`nctl model logs openvino_2`

Displays logs from `openvino_2` model export operation.
