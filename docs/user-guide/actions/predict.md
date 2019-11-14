# predict Command

Use this command to start, stop, and manage prediction jobs. This section discusses the following main topics:

 - [batch Subcommand](#batch-subcommand)
 - [cancel Subcommand](#cancel-subcommand)
 - [launch Subcommand](#launch-subcommand)
 - [list Subcommand](#list-subcommand)
 - [stream Subcommand](#stream-subcommand)
  
## batch Subcommand
 
### Synopsis

Starts a new batch instance that will perform prediction on provided data. Uses a specified dataset to perform inference. Results are stored in an output file.


### Syntax

`nctl predict batch [options]`
 
### Options

| Name | Required | Description | 
|:--- |:--- |:--- |
|`-n, --name TEXT`| No | Name of predict session.|
|`-m, --model-location` <br> `TEXT`| Yes | Path to saved model that will be used for inference. Model must be located on one of the input or output system shares (e.g. /mnt/input/saved_model). Model content will be copied into an image. |
|`-l, --local_model_location PATH`| Yes | Local path to saved model that will be used for inference. Model content will be copied into an image. |
|`-d, --data TEXT`| Yes | Location of a folder with data that will be used to perform the batch inference. Value should point out the location from one the system's shared folder.|
|`-o, --output TEXT`| No | Location of a folder where outputs from inferences will be stored. Value should point out the location from one of the system's shared folder.|
|`-mn, --model-name TEXT`| No | Name of a model passed as a servable name. By default it is the name of the directory in model's location.|
|`-tr, --tf-record`| No |If given, the batch prediction accepts files in `TFRecord` formats. Otherwise files should be delivered in `protobuf` format.|
|`-rt, --runtime`| No | Determine runtime for prediction. Supported runtimes are 'Tensorflow serving' (tfserving) and 'OpenVINO Model Server (ovms). Default runtime is 'tfserving'.|
|`-f, --force`| No | Ignore (most) confirmation prompts during command execution |
|`-v, --verbose`| No | Set verbosity level: <br>`-v` for INFO, <br>`-vv` for DEBUG |
|`-h, --help` | No | Displays help messaging information. |


### Returns

Description of a problem, if any occurs. Otherwise information that the predict job was submitted. 

**Note**: Refer to [Batch Inference Example](batch_inf_example.md) for a detailed example of this command.

## cancel Subcommand

### Synopsis

This command `cancels` prediction instance(s) chosen based on criteria given as a parameter.

### Syntax

`nctl predict cancel [options] [name]`

### Arguments

| Name | Required | Description |
|:--- |:--- |:--- |
|`NAME` | No | Name of predict instance to be cancelled. The [name] argument value can be empty when `match` option is used.|

### Options

| Name | Required | Description | 
|:--- |:--- |:--- |
|`-m, --match TEXT`| No | If given, the command searches for prediction instances matching the value of this option.|
|`-p, --purge`| No | If given, then all information concerning all prediction instances, completed and currently running, is removed from the system.|
|`-f, --force`| No | Ignore (most) confirmation prompts during command execution |
|`-v, --verbose`| No | Set verbosity level: <br>`-v` for INFO, <br>`-vv` for DEBUG |
|`-h, --help` | No | Displays help messaging information. |


### Returns

The description of a problem; if, any problem occurs. Otherwise information that training job/jobs was/were cancelled successfully. 

## launch Subcommand

### Synopsis

The `launch` subcommand starts  a new prediction instance that can be used for performing prediction, classification and regression tasks on a trained model. The created prediction instance is for streaming prediction only.

### Syntax

`nctl predict launch [options]`

### Options

| Name | Required | Description | 
|:--- |:--- |:--- |
|`-n, --name TEXT`| No | The name of this prediction instance.|
|`-m, --model-location` <br> `TEXT`| Yes | Path to saved model that will be used for inference. Model must be located on one of the input or output system shares (e.g. /mnt/input/home/saved_model).|
|`-l, --local_model_location`<br> `PATH`| No | Local path to saved model that will be used for inference. Model content will be copied into an image. 
|`-mn, --model-name TEXT`| No | Name of a model passed as a servable name. By default it is the name of directory in model's location. |
|`-rt, --runtime`| No | Determine runtime for prediction. Supported runtimes are 'Tensorflow serving' (tfserving) and 'OpenVINO Model Server (ovms). Default runtime is 'tfserving'.|
|`-f, --force`| No | Ignore (most) confirmation prompts during command execution |
|`-v, --verbose`| No | Set verbosity level: <br>`-v` for INFO, <br>`-vv` for DEBUG |
|`-h, --help` | No | Displays help messaging information. |

### Returns

Prediction instance URL and authorization token, as well as information about the experiment  (name, model location, state).

### Example

```
    nctl predict l -n test -m /mnt/input/home/experiment1
    
    | Prediction instance   | Model Location               | Status   |
    |-----------------------+------------------------------+----------|
    | test                  | /mnt/input/home/experiment1  | QUEUED   |

    Prediction instance URL (append method verb manually, e.g. :predict):
    https://192.168.0.1:8443/api/v1/namespaces/jdoe/services/test/proxy/v1/models/home

    Authorize with following header:
    Authorization: Bearer abcdefghijklmnopqrst0123456789

```

## list Subcommand

### Synopsis

The `list` subcommand displays a list of inference instances with some basic information regarding each of them. Results are
sorted using a date of creation starting with the most recent, and filtered by optional criteria.

### Syntax

`nctl predict list [options]`  

### Options

| Name | Required | Description | 
|:--- |:--- |:--- |
|`-a, --all_users`| No | Show all prediction instances, regardless of the owner.|
|`-n, --name TEXT`| No | A regular expression to narrow down list to prediction instances that match this expression.|
|`-s, --status [QUEUED, RUNNING, COMPLETE, CANCELLED, FAILED, CREATING]`| No | A regular expression to filter list to prediction instances with matching status.|
|`-u, --uninitialized`| No | List uninitialized prediction instances: for example, prediction instances without resources submitted for creation.|
|`-c/--count` <br> `INTEGER RANGE`| No | If given, command displays c most-recent rows.|
|`-b, --brief`| No | Print short version of the result table. Only 'name', 'submission date', 'owner' and 'state' columns will be printed.|
|`-f, --force`| No | Ignore (most) confirmation prompts during command execution |
|`-v, --verbose`| No | Set verbosity level: <br>`-v` for INFO, <br>`-vv` for DEBUG |
|`-h, --help` | No | Displays help messaging information. |

### Returns

List of inference instances.

## view Subcommand

### Synopsis

The `view` subcommand displays basic details of an prediction instance, such as the name of an experiment, parameters, submission date, and so on. 

### Syntax

`nctl predict view [options] PREDICTION_INSTANCE_NAME`

### Arguments

| Name | Required | Description |
|:--- |:--- |:--- |
|`PREDICTION_INSTANCE_NAME` | Yes | Name of an predictions instance for which details will be displayed. |

### Options

| Name | Required | Description | 
|:--- |:--- |:--- |
|`-u, --username`<br> `TEXT` | No | Name of the user who submitted this prediction instance. If not given, then only prediction instances of a current user are shown. |
|`-f, --force`| No | Ignore (most) confirmation prompts during command execution |
|`-v, --verbose`| No | Set verbosity level: <br>`-v` for INFO, <br>`-vv` for DEBUG |
|`-h, --help` | No | Displays help messaging information. |


### Returns

Displays details of an prediction instance.
### Example

`nctl predict view prediction-instance-2`

Displays details of an `prediction-instance-2` prediction instance.

## stream Subcommand
 
### Synopsis

The `stream` subcommand performs stream inference task on launched prediction instance. 

### Syntax

`nctl predict stream [options]`  

### Options

| Name | Required | Description | 
|:--- |:--- |:--- |
|`-n, --name TEXT`| Yes | Name of prediction session.|
|`-d, --data PATH`| Yes | Path to JSON data file that will be streamed to prediction instance. Data must be formatted such that it is compatible with the SignatureDef specified within the model deployed in the selected prediction instance.|
|`-m, --method-verb [classify, regress, predict]`| No | Method verb that will be used when performing inference. Predict verb is used by default.|
|`-f, --force`| No | Ignore (most) confirmation prompts during command execution |
|`-v, --verbose`| No | Set verbosity level: <br>`-v` for INFO, <br>`-vv` for DEBUG |
|`-h, --help` | No | Displays help messaging information. |


----------------------

## Return to Start of Document

* [README](../README.md)
----------------------
