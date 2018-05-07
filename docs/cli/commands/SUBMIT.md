# submit - submits training job

- [Synopsis](#synopsis)  
- [Arguments](#arguments)  
- [Options](#options)
- [Returns](#returns)
- [Notes](#notes)  
- [Examples](#examples)  
- [Status](#status)

## Synopsis

submits one single-node training job on a kuberenetes cluster. Format of the command is as follows:

_dlsctl submit <script_name> <options> -- <script_arguments>_


## Arguments

| Name | Obligatory | Description |
|:--- |:--- |:--- |
|_<script_name>_ | Yes | name of a python script with a description of training. |
|_<script_arguments>_ | No | string with a list of arguments that are passed to a training script. |


## Options

| Name | Obligatory | Description | 
|:--- |:--- |:--- |
|_-sfl/--script_folder_location<br> <folder_name>_ | No |location of a folder content of which is copied into a docker image created by _dlsctl submit_ command. _dlsctl_ copies the whole content preserving its structure - including subfolder. |
|_-t/--template <br><template_name>_| No | name of a template that will be used by _dlsctl_ to create a description of a job to be submitted. If not given - a default template for single node tensorflow training is used (tf-training).|
|_-pr/--parameter_range <br> <param_name> <definition>_ | No | if the parameter is given, _dlsctl_ will start as many experiments as there is a combination of parameters passed in _-pr_ options. Optional. _<param_name>_ is a name of a paramter that is passed to a training script. _<definition>_ contains values of this paramater that are passed to different instance of experiments. _<definition>_ can have two forms: <br> - range - _{x...y:step}_ - this form says, that _dlsctl_ will launch a number of experiments equal to a number of values between _x_ and _y_ (including both values) with step _step_. <br> - set of values - _{x, y, z}_ - this form says, that _dlsctl_ will launch number of experiments equal to a number of values given in this definition.|
|_-ps/--parameter_set <br><definition>_ | No | if this parameter is given, _dlsctl_ will launch an experiment with a set of parameters defined in _<definition>_ argument. Optional. Format of the _<definition>_ argument is as follows : _{<param1_name>: <param1_value>, <param2_name>: <param2_value>, ..., <paramn_name>:<paramn_value>}_. All parameters given in _<definition>_ argument will be passed to a training script under their names stated in this argument. If _ps_ parameter is given more than once - _dlsctl_ will start as many experiments as there is occurences of this parameter in a call. |


### Additional remarks

For both types of parameters - _-ps_ and _-pr_ - if parameter stated in their definitions
is also given in a _<script_arguments>_ argument of the _dlsctl_ command - values taken from _-ps_
and _-pr_ are passed to a script.   

If a combination of both paramaters is given - _dlsctl_ launches a number of experiments
equal to combination of values passed in those paramater. For example if the following
combination of paramater is passed to _dlsctl_ command:

_-pr param1 {0.1, 0.2, 0.3} -ps {param2: 3, param4: 5} -ps {param6: 7}_ 

the following experiments will be launched:  
- _param1 = 0.1, param2 = 3, param4 = 5, param6 - not set_
- _param1 = 0.2, param2 = 3, param4 = 5, param6 - not set_
- _param1 = 0.3, param2 = 3, param4 = 5, param6 - not set_
- _param1 = 0.1, param2 = not set, param4 = not set, param6 - 7_
- _param1 = 0.2, param2 = not set, param4 = not set, param6 - 7_
- _param1 = 0.3, param2 = not set, param4 = not set, param6 - 7_


## Returns

It returns a list of submitted experiments with their names and statusses. In case of problems during submitting of them command
display also message/messages describing causes of problems. Format of a list depends on chosen options:

- without -s option - statuses and names of launched experiments in a table with the following column names : 
"Experiment" and "Status". If due to errors names of some (or all) experiments haven't been created - they remain empty. If any error appears - messages describing it
are displayed before a table with experiment's names/statuses. 
- with -s option - names of all succesfully submitted experiments. Each name is displayed in a 
separate row. In case when none of submitted experiments was submitted succesfully - command displays nothing.

If at least one of experiments hasn't been submitted with a success - command returns an exit code > 0. Exact 
value of a code depends on a cause of errors that prevented submitting training jobs.

Here is an example output of _submit_ command issued without _-s_ option.

<!-- language: lang-none -->

    | Experiment          | Status   |
    +---------------------+----------+
    | t20180423121021851  | Received |
    
If the same command is issued with _-s_ command, it returns:

<!-- language: lang-none -->

    t20180423121021851

## Notes

## Examples

_dlsctl submit mnist_cnn.py -sfl /data -- --data_dir=/app/data --num_gpus=0_  

Starts a single node training job using mnist_cnn.py script located in a folder from which _dlsctl_ command was issued. Content of
the /data folder is copied into docker image (into /app folder - which is a work directory of docker images created using
tf-training pack). Arguments _--data-dir_ and _--num_gpus_ are passed to a script.

## Status

Under development
