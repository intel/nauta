# experiment Command

This overall purpose of this command/subcommands is to submit and manage experiments. Following are the subcommands for the dlsctl experiment command.

 - [submit Subcommand](#submit-subcommand)
 - [list Subcommand](#list-subcommand)  
 - [cancel Subcommand](#cancel-subcommand)
 - [view Subcommand](#view-subcommand)
 - [logs Subcommand](#logs-subcommand)
 - [interact Subcommand](#interact-subcommand)
 - [template_list Subcommand](#template_list-subcommand)

 
## submit Subcommand
 
 - [Synopsis](#synopsis)
 - [Syntax](#syntax)
 - [Arguments](#arguments)  
 - [Options](#options)
 - [Returns](#returns)
 - [Examples](#examples)  
  
 ### Synopsis
 
Submits training jobs. We can use this command to submit single and multi-node training jobs (by passing –t parameter with a name of a multi-node pack), and many jobs at once (by passing –pr/-ps parameters).
 
 ### Syntax
 
 `dlsctl experiment submit [options] SCRIPT_LOCATION [-- script_parameters]`
 
 
 ### Arguments
 
 | Name | Required | Description |
 |:--- |:--- |:--- |
 |`SCRIPT_LOCATION` | Yes | Location and name of a python script with a description of training. |
 |`script_parameters` | No | String with a list of parameters that are passed to a training script. All such parameters should be added at the end of command after "--" string |
 
 
 ### Options
 
 | Name | Required | Description | 
 |:--- |:--- |:--- |
 |`-sfl, --script_folder_location`<br>`[folder_name] PATH` | No |Location and name of a folder with additional files used                                   by a script, e.g., other .py files, data, etc. If not given, then its content won't be copied into a the docker image created by the `dlsctl submit` command. `dlsctl` copies all content, preserving its structure, including subfolder(s). |
 |`-t, --template` <br>`[template_name] TEXT`| No | Name of a template that will be used by `dlsctl` to create a description of a job to be submitted. If not given - a default template for single node tensorflow training is used (tf-training). List of available templates can be obtained by issuing `dlsctl experiment template_list command`. |
 |`-n, --name TEXT`| No | Name for this experiment.|
 |`-p, --pack_param` <br> `<TEXT TEXT>…`| No |Additional pack param in format: 'key value' or 'key.subkey.subkey2 value'. For lists use: 'key "['val1', 'val2']"' For maps use: 'key "{'a': 'b'}"'|
 |`-pr, --parameter_range` <br> `[param_name] [definition]` | No | If the parameter is given, `dlsctl` will start as many experiments as there is a combination of parameters passed in `-pr` options. Optional. `[param_name]` is a name of a parameter that is passed to a training script. `[definition]` <br> Contains values of this paramater that are passed to different instance of experiments. `[definition]` can have two forms: <br> - range - `{x...y:step}` - this form says that `dlsctl` will launch a number of experiments equal to a number of values between `x` and `y` (including both values) with step `step`. <br> - set of values - `{x, y, z}` - this form says that `dlsctl` will launch number of experiments equal to a number of values given in this definition.|
 |`-ps, --parameter_set` <br>`[definition]` | No | If this parameter is given, `dlsctl` will launch an experiment with a set of parameters defined in `[definition]` argument. Optional. Format of the `[definition]` argument is as follows : `{[param1_name]: [param1_value], [param2_name]: [param2_value], ..., [paramn_name]:[paramn_value]}`. <br> All parameters given in `[definition]` argument will be passed to a training script under their names stated in this argument. If `ps` parameter is given more than once - `dlsctl` will start as many experiments as there is occurences of this parameter in a call. |
 |`-e, --env TEXT` | No | Set of values of one or several parameters.Environment variables passed to training. User can pass as many environmental variables as it is needed. Each variable should be in such case passed as a separate -e parameter.|
 |`-v, --verbose`| No | Set verbosity level: <br>`-v` for INFO, <br>`-vv` for DEBUG |
 |`-h, --help` | No | Show help message and exit. |

 
 
 #### Additional remarks
 
 For both types of parameters - `-ps` and `-pr` - if parameter stated in their definitions
 is also given in a `[script_parameters]` argument of the `dlsctl` command, then values taken from `-ps`
 and `-pr` are passed to a script.   
 
 If a combination of both paramaters is given, then `dlsctl` launches a number of experiments
 equal to combination of values passed in those paramater. For example, if the following
 combination of parameters is passed to `dlsctl` command:
 
 `-pr param1 "{0.1, 0.2, 0.3}" -ps "{param2: 3, param4: 5}" -ps "{param6: 7}"` 
 
 then the following experiments will be launched:  
 - `param1 = 0.1, param2 = 3, param4 = 5, param6 - not set`
 - `param1 = 0.2, param2 = 3, param4 = 5, param6 - not set`
 - `param1 = 0.3, param2 = 3, param4 = 5, param6 - not set`
 - `param1 = 0.1, param2 = not set, param4 = not set, param6 - 7`
 - `param1 = 0.2, param2 = not set, param4 = not set, param6 - 7`
 - `param1 = 0.3, param2 = not set, param4 = not set, param6 - 7`
 
 
 ### Returns
 
This commmand returns a list of submitted experiments with their names and statuses. In case of problems during submission, the command displays message/messages describing the causes. Errors may cause some experiments to not be created and will be empty. If any error appears, then messages describing it are displayed with experiment's names/statuses. 
  
If one or more of experiment has not been submitted successfully, then the command returns an exit code > 0. The exact  value of the code depends on the cause of error(s) that prevented submitting the experiment(s). Here is a sample output  of `submit` command.
 
 <!-- language: lang-none -->
 
     | Experiment          | Status   |
     +---------------------+----------+
     | t20180423121021851  | Received |
     
 ### Examples
 
 `dlsctl experiment submit mnist_cnn.py -sfl /data -- --data_dir=/app/data --num_gpus=0`  
 
 Starts a single node training job using mnist_cnn.py script located in a folder from which `dlsctl` command was issued. Content of
 the /data folder is copied into docker image (into /app folder - which is a work directory of docker images created using
 tf-training pack). Arguments `--data-dir` and `--num_gpus` are passed to a script.


## list Subcommand

- [Synopsis](#synopsis_list)
- [Syntax](#syntax_list)
- [Options](#options_list)
- [Returns](#returns_list)
- [Example](#example_list)  

### <a name="synopsis_list"></a>Synopsis

Displays a list of all experiments with some basic information for each. Results are
sorted using the date-of-creation of the experiment, starting with the most recent experiment.  

### <a name="syntax_list"></a>Syntax

`dlsctl experiment list [options]`  

### <a name="options_list"> </a>Options

| Name | Required | Description | 
|:--- |:--- |:--- |
|`-a, --all_users`| No | List contains experiments submitted by of all users.|
|`-n, --name` | No | A regular expression to filter list to experiments that match this expression.|
|`-s, --status` | No | QUEUED,  RUNNING,  COMPLETE, CANCELLED, FAILED, CREATING - Lists experiments based on indicated status.|
|`-u, --uninitialized` | No | List uninitialized experiments, that is, experiments without resources submitted for creation.|
|`-c, --count (INT)` | No | An integer, command displays c last rows.|
|`-b, --brief` | No | Print short version of the result table. Only 'name', 'submission date', 'owner' and 'state' columns will be printed.|
 |`-v, --verbose`| No | Set verbosity level: <br>`-v` for INFO, <br>`-vv` for DEBUG |
 |`-h, --help` | No | Show help message and exit. |

###  <a name="returns_list"> </a> Returns

List of experiments matching criteria given in command's options. Each row contains the experiment name and additional data of each experiment, such parameters used for this certain training, time and date when ot was submitted, name of a user which submitted this training and current status of an experiment. Below is an example table returned by this command. 

<!-- language: lang-none -->

    
    | Experiment           | Parameters used     | Metrics       | Time submitted | Username | Status   |
    +----------------------+---------------------+---------------+----------------+----------+----------|
    | exp1-20181122:0830-1 | learningrate: 0.1   | loss: 0.05    |  20181122:0830 | jdoe     | Complete |
    |                      | padding: 2          | accuracy: 0.9 |                |          |          |
    |                      | layers: 10          |               |                |          |          |
    | exp1-20181122:0830-2 | learningrate: 0.01  |               |  20181122:0830 | jdoe     | Running` |
    | exp1-20181122:0830-3 | learningrate: 0.001 |               |  20181122:0830 | jdoe     | Queued   |
        

###  <a name="example_list"> </a> Example

`dlsctl experiment list`

Displays all experiments submitted by a current user

`dlsctl experiment list -n train`

Displays all experiments submitted by a current user and with name starting with `train` word.

## cancel Subcommand

- [Synopsis](#synopsis_cancel)  
- [Syntax](#syntax_cancel)
- [Arguments](#arguments_cancel)  
- [Options](#options_cancel)
- [Returns](#returns_cancel)
- [Example](#example_cancel)  

### <a name="synopsis_cancel"></a> Synopsis

Cancels training chosen based on provided parameters. 

### <a name="syntax_cancel"> </a> Syntax

`dlsctl experiment cancel [options] NAME`

### <a name="arguments_cancel"> </a> Arguments

| Name | Required | Description |
|:--- |:--- |:--- |
|`NAME` | Yes | The name of an experiment/pod/status of a pod to be cancelled. If any such object has been found - the command displays for each of such objects a question whether this object should be cancelled. Value of this argument should be created using rules described [here](interpret_experiment_parameters.md). |

### <a name="options_cancel"></a> Options

| Name | Required | Description | 
|:--- |:--- |:--- |
|`-m, --match TEXT`| No | If given, command searches for experiments matching the value of this option. This option cannot be used along with the NAME argument.|
|`-p, --purge`| No | If given, then all information concerning for identified experiments, completed and currently running, is removed from the system.|
|`-i, --pod-ids` <br> `TEXT`| No | Comma-separated pods IDs. If given, command matches pods by their IDs and deletes them.|
|` -s, --pod-status` <br> `TEXT`| No |One of: 'PENDING', 'RUNNING', 'SUCCEEDED', 'FAILED', or 'UNKNOWN'. If given, command searches pods by their status and deletes them.|
|`-v, --verbose`| No | Set verbosity level: <br>`-v` for INFO, <br>`-vv` for DEBUG |
|`-h, --help` | No | Show help message and exit. |


### <a name="returns_cancel"></a>  Returns

Description of a problem - if any occurs. Otherwise information that training job/jobs was/were cancelled successfully. 

### <a name="example_cancel"></a>  Example

`dlsctl experiment cancel t20180423121021851`

Cancels experiment with `t20180423121021851` name.

## view Subcommand

- [Synopsis](#synopsis_view)
- [Syntax](#syntax_view)
- [Arguments](#arguments_view)  
- [Options](#options_view)
- [Returns](#returns_view)
- [Examples](#example_view)  

### <a name="synopsis_view"></a> Synopsis

Displays basic details of an experiment, such as the name of an experiment, parameters, submission date etc. 

### <a name="syntax_view"></a> Syntax

`dlsctl experiment view [options] EXPERIMENT_NAME`

### <a name="arguments_view"></a> Arguments

| Name | Required | Description |
|:--- |:--- |:--- |
|`EXPERIMENT_NAME` | Yes | Name of an experiment to be displayed. |

### <a name="options_view"></a> Options

| Name | Required | Description | 
|:--- |:--- |:--- |
|`-t, --tensorboard` | No | If given, command exposes a tensorboard's instance with experiment's data. |
|`-u, --username` | No | Name of the user who submitted this experiment. If not given, then only experiments of a current user are shown. |
 |`-v, --verbose`| No | Set verbosity level: <br>`-v` for INFO, <br>`-vv` for DEBUG |
 |`-h, --help` | No | Show help message and exit. |


### <a name="returns_view"></a> Returns

Displays details of an experiment. If `-t/--tensorboard` option is given - the command returns also a link to tensorboard's instance with data from an experiment.


### <a name="example_view"></a>  Example

`dlsctl experiment view experiment_name_2 -t`

Displays details of an `experiment_name_2` experiment and exposes `tensorboard` instance with experiment's data to a user.


## logs Subcommand

- [Synopsis](#synopsis_logs)
- [Syntax](#syntax_logs)
- [Arguments](#arguments_logs)  
- [Options](#options_logs)
- [Returns](#returns_logs)
- [Example](#example_logs)  

### <a name="synopsis_logs"></a> Synopsis

Displays logs from experiments. Logs to be displayed are chosen based on parameters given.

### <a name="syntax_logs"></a>  Syntax

`dlsctl experiment logs [options] EXPERIMENT_NAME`

### <a name="arguments_logs"></a> Arguments

| Name | Required | Description |
|:--- |:--- |:--- |
|`EXPERIMENT_NAME` | Yes | Name of an experiment logs from which will be displayed. Value of this argument should be created using rules described [here](interpret_experiment_parameters.md).  |

### <a name="options_logs"></a> Options

| Name | Required | Description | 
|:--- |:--- |:--- |
|`-s, --min_severity` | No | Minimal severity of logs. Available choices are:<br> - CRITICAL - displays only CRITICAL logs.<br> - ERROR - displays ERROR and CRITICAL logs.<br> - WARNING - displays ERROR, CRITICAL and WARNING logs. <br> - INFO - displays ERROR, CRITICAL, WARNING and INFO.<br> - DEBUG - displays ERROR, CRITICAL, WARNING, INFO and DEBUG. |
|`-sd, --start_date` | No | Retrieve logs produced from this date (format ISO-8061 - yyyy-mm-ddThh:mm:ss).|
|`-ed, --end_date` | No | retrieve logs produced until this date (format ISO-8061 - yyyy-mm-ddThh:mm:ss).|
|`-i, --pod-ids TEXT` | No |Comma-separated pods IDs. If given, then matches pods by their IDs and only logs from these pods from an experiment with `EXPERIMENT_NAME` name will be returned.|
|`- p, --pod_status TEXT` | No |One of: 'PENDING', 'RUNNING', 'SUCCEEDED', 'FAILED', or 'UNKNOWN' - command returns logs with matching status from an experiment and matching EXPERIMENT_NAME.|
|`-m, --match TEXT` | No |  If given, command searches for logs from experiments matching the value of this option. This option cannot be used along with the NAME argument.|
|`-o, --output` | No |  If given, logs are stored in a file with a name derived from a name of an experiment.|
|`--pager` | No | Display logs in interactive pager. Press *q* to exit the pager.|
|`-f, --follow` | No | Specify if logs should be streamed. Only logs from a single experiment can be streamed.|
 |`-v, --verbose`| No | Set verbosity level: <br>`-v` for INFO, <br>`-vv` for DEBUG |
 |`-h, --help` | No | Show help message and exit. |


### <a name="returns_logs"></a> Returns

In case of any problems, a message(s) with description of their cause(s). Otherwise, logs are filtered based on command's parameters.

### <a name="example_logs"></a> Example

`dlsctl experiment logs experiment_name_2 --min_severity DEBUG`

Displays logs from `experiment_name_2` experiment with severity DEBUG.


## interact Subcommand

- [Synopsis](#synopsis_interact)
- [Syntax](#syntax_interact)
- [Options](#options_interact)
- [Returns](#returns_interact)
- [Example](#example_interact)  

### <a name="synopsis_interact"></a> Synopsis

Launches a local browser with Jupyter notebook. If script's name is given as a parameter of a command, then this script
is displayed in a notebook. 

### <a name="syntax_interact"></a> Syntax

`dlsctl experiment interact [options]`

### <a name="options_interact"></a> Options

| Name | Required | Description | 
|:--- |:--- |:--- |
|`-n, --name` | No | Name of a Jupyter notebook's session. If session with a given name already exists, then a user is connected to this session. |
|`-f, --filename` | No | File with a notebook that should be opened in Jupyter notebook. Additional pack param in format: 'key value' or 'key.subkey.subkey2 value'. For lists use: 'key "['val1', 'val2']"' For maps use:'key "{'a': 'b'}"'|
|`-p, --pack_param <TEXT TEXT>...`| No | Additional pack param in format: 'key value' or 'key.subkey.subkey2 value'.<br> For lists use: 'key "['val1', 'val2']"' <br>For maps use: 'key "{'a': 'b'}"' |
|`--no-launch`| No | Run command without a web browser starting, only proxy tunnel is created.|
|`-pn, --port_number INTEGER RANGE` | No | Port on which service will be exposed locally.|
|` -e, --env TEXT` | No | Environment variables passed to Jupyter instance. User can pass as many environmental variables as it is needed. Each variable should be in such case passed as a separate -e paramater.|
|` -t, --template` <br>`[jupyter,jupyter-py2]` | No | Name of a jupyter notebook template used to create a deployment. Supported templates for interact command are: jupyter (python3) and jupyter-py2 (python2).|
 |`-v, --verbose`| No | Set verbosity level: <br>`-v` for INFO, <br>`-vv` for DEBUG |
 |`-h, --help` | No | Show help message and exit. |

### <a name="returns_interact"></a> Returns

In case of any problems, a message provides a description of possible causes. Otherwise the command launches a default web browser with Jupyter notebook, and displays the address under which this session is provided.

### <a name="example_interact"></a> Example

`dlsctl experiment interact training_script.py`

Launches in a default browser a Jupyter notebook with `training_script.py` script.


## template_list Subcommand

- [Synopsis](#synopsis_templist)
- [Syntax](#syntax_templist)
- [Returns](#returns_templist)
- [Examples](#examples_templist)  

### <a name="synopsis_templist"></a>  Synopsis

The command returns a list of templates installed on a client machine. Template contains all details needed 
to properly deploy a training job on a cluster.

### <a name="syntax_templist"></a> Syntax

`dlsctl experiment template_list [options]`

### <a name="options_templist"></a>  Options

| Name | Required | Description | 
|:--- |:--- |:--- |
|`-v, --verbose`| No | Set verbosity level: <br>`-v` for INFO, <br>`-vv` for DEBUG |
|`-h, --help` | No | Show help message and exit. |


### <a name="returns_templist"></a> Returns

List of existing templates, or a "Lack of installed packs." message if there are no templates installed.


### <a name="example_templist"></a> Example

`dlsctl experiment template_list`


