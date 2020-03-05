# experiment Command

Use the `experiment` command to submit and manage experiments. This main command also includes the following subcommands:

 - [submit Subcommand](#submit-subcommand)
 - [list Subcommand](#list-subcommand)  
 - [cancel Subcommand](#cancel-subcommand)
 - [view Subcommand](#view-subcommand)
 - [logs Subcommand](#logs-subcommand)
 - [interact Subcommand](#interact-subcommand)
 
 
## submit Subcommand

### Synopsis
 
Use the `submit` subcommand to submit training jobs. Use this command to submit single and multi-node training jobs (by passing –t parameter with a name of a multi-node pack), and many jobs at once (by passing –pr/-ps parameters). If `-n/--name` parameter is not passed, experiment name will be automatically generated, by deriving a new, unique name from training script's name.
 
### Syntax
 
 `nctl experiment submit [options] SCRIPT-LOCATION [-- script-parameters]`
 
### Arguments

| Name | Required | Description |
|:--- |:--- |:--- |
|`SCRIPT-LOCATION` | Yes | Location and name of a Python script with a description of training. |
|`script-parameters` | No | String with a list of parameters that are passed to a training script. All such parameters should be added at the end of command after "--" string. |

## Options

| Name | Required | Description | 
|:--- |:--- |:--- |
|`-sfl, --script-folder-location`<br>`[folder_name] PATH` | No |Location and name of a folder with additional files used    by a script, for example: other .py files,data, and so on. If not given, then its content _will not_ be copied into the Docker image created by the `nctl submit` command. `nctl` copies all content, preserving its structure, including subfolder(s). |
|`-t, --template` <br>`[template_name] TEXT`| No | Name of a template that will be used by `nctl` to create a description of a job to be submitted. If not given, a default template for single node TensorFlow training is used (tf-training). List of available templates can be obtained by issuing the `nctl template list` command. |
|`-n, --name TEXT`| No | Name for this experiment.|
|`-p, --pack-param` <br> `<TEXT TEXT>…`| No |Additional pack parameter in format: `key value` or `key.subkey.subkey2 value`. For lists use: `'key "['val1', 'val2']"'`For maps use: `'key "{'a': 'b'}"'`|
|`-pr, --parameter-range` <br>`TEXT... [definition] <TEXT TEXT>...` | No | If the parameter is given, `nctl` starts as many experiments as there is a combination of parameters passed in `-pr` options Optional`[param_name]` is a name of a parameter that is passed to a training script. `[definition]` <br> <br> Contains values of this parameter that are passed to different instance of experiments. `[definition]` can have two forms: <br> <br> range: `{x...y:step}` This form says that `nctl`will launch a number of experiments equal to a number of values between `x` and `y` (including both values) with step `step`. <br> <br> set of values: `{x, y, z}`This form says that `nctl` will launch number of experiments equal to a number of values given in this definition.|
|`-ps, --parameter-set` <br>`[definition] TEXT` | No | If this parameter is given, `nctl` launches an experiment with a set of parameters that will be passed to experiment's script. Format of the `[definition]` argument is as follows: `{[param1_name]: [param1_value], [param2_name]: [param2_value], ..., [paramn_name]:[paramn_value]}`. <br>  <br> All parameters given in the `[definition]` argument will be passed to a training script under their names stated in this argument. If `ps` parameter is given more than once, `nctl` will start as many experiments as there is occurrences of this parameter in a call. |
|`-e, --env TEXT` | No | This is the environment variable passed to training. You can pass as many environmental variables, as desired. Each variable should be passed as a separate -e parameter.|
|`-r, --requirements PATH` | No | This is the path to the file with experiment's pip requirements. Dependencies listed in this file will be automatically installed using pip. |
|`-f, --force`| No | Force command execution by ignoring (most) confirmation prompts. |
|`-v, --verbose`| No | Set verbosity level: <br>`-v` for INFO <br>`-vv` for DEBUG |
|`-h, --help` | No | Displays help messaging information. |

#### Additional Remarks
 
 For both types of parameters: `-ps` and `-pr`; if, parameter stated in their definitions
 is also given in a `[script_parameters]`argument of the `nctl` command, then values taken from `-ps`
 and `-pr` are passed to a script.   
 
 If a combination of both parameters is given, then `nctl` launches a number of experiments
 equal to combination of values passed in those parameters. For example, if the following
 combination of parameters is passed to `nctl` command:
 
 `-pr param1 "{0.1, 0.2, 0.3}" -ps "{param2: 3, param4: 5}" -ps "{param6: 7}"` 
 
 Then the following experiments will be launched:
 
 ``` 
param1 = 0.1, param2 = 3, param4 = 5, param6 - not set
param1 = 0.2, param2 = 3, param4 = 5, param6 - not set
param1 = 0.3, param2 = 3, param4 = 5, param6 - not set`
param1 = 0.1, param2 = not set, param4 = not set, param6 - 7
param1 = 0.2, param2 = not set, param4 = not set, param6 - 7
param1 = 0.3, param2 = not set, param4 = not set, param6 - 7
 ```
 
### Returns
 
This command returns a list of submitted experiments with their names and statuses. In case of problems during submission, the command displays message/messages describing the causes. Errors may cause some experiments _to not be_ created and will be empty. If any error appears, then messages describing it are displayed with experiment's names/statuses. 
  
If one or more of experiment _has not been_ submitted successfully, then the command returns an exit code: `> 0`. The exact  value of the code depends on the cause of error(s) that prevented submitting the experiment(s).
     
### Example
 
`nctl experiment submit --name para-range --parameter-range lr "{0.1, 0.2, 0.3}" examples/mnist_single_node.py -- --data_dir=/mnt/input/root/public/MNIST`  
 
Starts multiple single node training jobs using `mnist_single_node.py` script located in the examples folder. 
Each training job uses a different learning rate value.

## list Subcommand

### Synopsis

Use the `list` subcommand to display a list of all experiments with some basic information for each, regardless of the owner. Results are sorted using the _date-of-creation_ of the experiment, starting with the most recent experiment.  

### Syntax

`nctl experiment list [options]`  

### Options

| Name | Required | Description | 
|:--- |:--- |:--- |
|`-a, --all_users`| No | List contains experiments submitted by all users.|
|`-n, --name TEXT` | No | A regular expression to filter list to experiments that match this expression.|
|`-s, --status` | No | QUEUED,  RUNNING,  COMPLETE, CANCELLED, FAILED, CREATING - Lists experiments based on indicated status.|
|`-u, --uninitialized` | No | List uninitialized experiments, that is, experiments without resources submitted for creation.|
|`-c, --count` <br> `INTEGER RANGE` | No | An integer, command displays c last rows.|
|`-b, --brief` | No | Print short version of the result table. Only 'name', 'submission date', 'owner' and 'state' columns will be printed.|
|`-f, --force`| No | Force command execution by ignoring (most) confirmation prompts. |
|`-v, --verbose`| No | Set verbosity level: <br>`-v` for INFO, <br>`-vv` for DEBUG |
|`-h, --help` | No | Displays help messaging information. |

### Returns

Displays the list of experiments matching a criteria given in the command's options. Each row contains the experiment name and additional data of each experiment, such parameters used for this certain training, time and date when it was submitted, name of a user which submitted this training and current status of an experiment. The example table below shows the results returned by this command (the brief option is shown). 

```
 
| Experiment                          | Submission date        | Owner | State     |
|--------------+----------------------+---------+----------------------------------|
| mnist-single-node-tb                | 2019-03-13 04:57:58 PM | user1 |  QUEUED   |
| mnist-tb                            | 2019-03-13 05:00:39 PM | user1 |  COMPLETE |
| mnist-tb 2-1                        | 2019-03-13 05:49:59 PM | user1 |  COMPLETE |
| test-experiment                     | 2019-03-13 06:00:39 PM | user1 |  QUEUED   |
| single-experiment                   | 2019-03-13 01:49:59 PM | user1 |  QUEUED   |

```

### Examples

The following command displays all experiments submitted by a current user.

`nctl experiment list`

The following command displays all experiments submitted by a current user and with name starting with `train` word.

`nctl experiment list -n train`

## cancel Subcommand

### Synopsis

Use the `cancel` subcommand to cancel any training chosen based on the provided parameters. 

### Syntax

`nctl experiment cancel [options] NAME`

### Arguments

| Name | Required | Description |
|:--- |:--- |:--- |
|`NAME` | Yes | The name of an _experiment/pod/status_ of a pod to be cancelled. If any such object is found, the command displays a question whether this object should be cancelled. |

### Options

| Name | Required | Description | 
|:--- |:--- |:--- |
|`-m, --match TEXT`| No | If given, the command searches for experiments matching the value of this option. This option _cannot_ be used along with the `NAME` argument.|
|`-p, --purge`| No | If given, then all information concerning for identified experiments, completed and currently running, is removed from the system.|
|`-i, --pod-ids` <br> `TEXT`| No | Comma-separated pods IDs. If given, command matches pods by their IDs and deletes them.|
|` -s, --pod-status` <br> `TEXT`| No |One of: 'PENDING', 'RUNNING', 'SUCCEEDED', 'FAILED', or 'UNKNOWN'. If given, the command searches pods by their status and deletes them.|
|`-f, --force`| No | Force command execution by ignoring (most) confirmation prompts. |
|`-v, --verbose`| No | Set verbosity level: <br>`-v` for INFO, <br>`-vv` for DEBUG |
|`-h, --help` | No | Displays help messaging information. |

### Returns

The description of a problem; if, any problem occurs. Otherwise, displays the information that training job/jobs was/were cancelled successfully.

### Example

`nctl experiment cancel t20180423121021851`

### Outcome

This cancels the experiment with `t20180423121021851` name, as shown in the example.

## view Subcommand

### Synopsis

Use the `view` subcommand to display basic details of an experiment, such as the name of an experiment, parameters, submission date, and so on. 

### Syntax

`nctl experiment view [options] EXPERIMENT-NAME`

### Arguments

| Name | Required | Description |
|:--- |:--- |:--- |
|`EXPERIMENT-NAME` | Yes | Name of an experiment to be displayed. |

### Options

| Name | Required | Description | 
|:--- |:--- |:--- |
|`-tb, --tensorboard` | No | If given, the command displays a TensorBoard with an experiment's data. |
|`-u, --username`<br> `TEXT` | No | Name of the user who submitted this experiment. If not given, then only experiments of a current user are shown. |
|`-f, --force`| No | Force command execution by ignoring (most) confirmation prompts. |
|`-v, --verbose`| No | Set verbosity level: <br>`-v` for INFO, <br>`-vv` for DEBUG |
|`-h, --help` | No | Displays help messaging information. |


### Returns

Displays details of an experiment. If `-tb, --tensorboard` option is given, then the command returns a link to a TensorBoard's instance with data from an experiment.

### Example

`nctl experiment view experiment-name-2 -tb`

Displays details of an `experiment-name-2` experiment and exposes a TensorBoard instance with experiment's data to a user.


## logs Subcommand

### Synopsis

Use the `logs` subcommand to display the logs from experiments. Logs to be displayed are chosen based on parameters given in the command's call.

### Syntax

`nctl experiment logs [options] EXPERIMENT-NAME`

### Arguments

| Name | Required | Description |
|:--- |:--- |:--- |
|`EXPERIMENT-NAME` | Yes | Displays the name of experiment logs. |

### Options

| Name | Required | Description | 
|:--- |:--- |:--- |
|`-s, --min-severity` | No | Minimal severity of logs. Available choices are:<br> **CRITICAL:** Displays only CRITICAL logs.<br> **ERROR:** Displays ERROR and CRITICAL logs.<br> **WARNING:** Displays ERROR, CRITICAL and WARNING logs. <br> **INFO:** Displays ERROR, CRITICAL, WARNING and INFO.<br> **DEBUG:** - Displays ERROR, CRITICAL, WARNING, INFO and DEBUG. |
|`-sd, --start-date` | No | Retrieve logs produced from this date (format ISO-8061 - yyyy-mm-ddThh:mm:ss).|
|`-ed, --end-date` | No | retrieve logs produced until this date (format ISO-8061 - yyyy-mm-ddThh:mm:ss).|
|`-i, --pod-ids TEXT` | No |Comma-separated pods IDs. If given, then matches pods by their IDs and only logs from these pods from an experiment with `EXPERIMENT-NAME` name will be returned.|
|`- p, --pod-status TEXT` | No |One of: 'PENDING', 'RUNNING', 'SUCCEEDED', 'FAILED', or 'UNKNOWN' - command returns logs with matching status from an experiment and matching EXPERIMENT-NAME.|
|`-m, --match TEXT` | No |  If given, command searches for logs from experiments matching the value of this option. This option cannot be used along with the NAME argument.|
|`-o, --output` | No |  If given, logs are stored in a file with a name derived from a name of an experiment.|
|`-pa, --pager` | No | Display logs in interactive pager. Press *q* to exit the pager.|
|`-fl, --follow` | No | Specify if logs should be streamed. Only logs from a single experiment can be streamed.|
|`-f, --force`| No | Force command execution by ignoring (most) confirmation prompts. |
|`-v, --verbose`| No | Set verbosity level: <br>`-v` for INFO, <br>`-vv` for DEBUG |
|`-h, --help` | No | Displays help messaging information. |


### Returns

Should issues arise, a message (or messages) with a description of their cause (or causes) displays. Otherwise, the logs are filtered based on command's parameters.

### Example

`nctl experiment logs experiment-name-2 --min-severity DEBUG`

Displays logs from `experiment-name-2` experiment with severity DEBUG and higher (`INFO`, `WARNING`, and so on).


## interact Subcommand

### Synopsis

Use the `interact` subcommand to launch a local browser with a Jupyter notebook. If a script's name is given as a parameter of the command, then this script is displayed in a notebook. 

### Syntax

`nctl experiment interact [options]`

### Options

| Name | Required | Description | 
|:--- |:--- |:--- |
|`-n, --name TEXT` | No | The name of a Jupyter notebook's session. If a session with a given name already exists, then you are connected to this session. |
|`-fl, --filename TEXT` | No | The file with a notebook that should be opened in Jupyter notebook. |
|`-p, --pack-param <TEXT TEXT>...`| No | Additional pack parameter in format: 'key value' or 'key.subkey.subkey2 value'.<br> For lists use: 'key "['val1', 'val2']"' <br> For maps use: 'key "{'a': 'b'}"' |
|`--no-launch`| No | Run this command without a web browser starting, only proxy tunnel is created.|
|`-pn, --port-number INTEGER RANGE` | No | Port on which service will be exposed locally.|
|` -e, --env TEXT` | No | This is the environment variable passed to Jupyter instance. User can pass as many environmental variables as it is needed. Each variable should be in such case passed as a separate -e parameter.|
|` -t, --template` <br>`[jupyter]` | No | Name of a Jupyter notebook template used to create a deployment. Supported templates for interact command are: jupyter (python3).|
|`-f, --force`| No | Force command execution by ignoring (most) confirmation prompts. |
|`-v, --verbose`| No | Set verbosity level: <br>`-v` for INFO, <br>`-vv` for DEBUG |
|`-h, --help` | No | Displays help messaging information. |

### Returns

Should issues arise, a message (or messages) with a description of their cause (or causes) displays. Otherwise, the command launches a default web browser with a Jupyter notebook, and displays the address under which this session is provided.

### Example

`nctl experiment interact --filename training_script.py`

Launches in a default browser a Jupyter notebook with `training_script.py` script.

----------------------

## Return to Start of Document

* [README](../README.md)
----------------------
