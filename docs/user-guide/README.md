# DLS4E Command Line Interface (dlsctl)

## Requirements

* kubectl >= 1.10
* helm **==** 2.9.1
* docker >= 18.03.0-ce

These tools need to be installed on system, available in terminal by PATH and verified that correct version is used.
Note: docker can contain kubectl binary in a version that's not supported. Please verify that PATH environment variable has correct order of paths and that the kubectl from docker package is not used.

Remember about setting `http_proxy`, `https_proxy` and `no_proxy` environment variables, if you're behind
proxy.

Recommended shell environment for dlsctl is bash.

## **dlsctl** commands

#### License acceptance
At first run of any dlsctl command there is a confirmation displayed:
```
DO NOT ACCESS, COPY OR PERFORM ANY PORTION OF THE PRE-RELEASE SOFTWARE UNTIL YOU HAVE READ AND ACCEPTED THE TERMS AND 
CONDITIONS OF THIS AGREEMENT LICENSE.TXT . BY COPYING, ACCESSING, OR PERFORMING THE PRE-RELEASE SOFTWARE, YOU AGREE TO 
BE LEGALLY BOUND BY THE TERMS AND CONDITIONS OF THIS AGREEMENT. Agree? [y/N]:
```
You need to accept that to continue using CLI, by putting 'y' or 'yes'. The default answer is 'no', so pressing just
Enter is not enough.

#### General options/flags
 Here is a list of flags/options that can used with any command from a list of commands given below:  
 _-v/-vv/--verbose_ </b> - verbose. If this option is given, application displays on a console logs from execution of a certain command. If _-v_ option is
 given - basic logs on INFO/EXCEPTION/ERROR levels are displayed. If _-vv_ option (it may contain more vs - for example _-vvv_)
 is given - detailed logs on INFO/DEBUG/EXCEPTION/ERROR levels are displayed.  

 _-s_ - silent. If the option is given - all commands that return some kind of ids (for example submit command returns a name of a
 submitted experiment) return it in a plain format (without any tables or paramater names - just plain id). Detailed description of
 how this flag is interpreted by a certain command can be found in a description of commands.

#### Format of messages returned by commands

If option -s isn't given - _dlsctl_ command returns its outcome in a tabluar format. If except of outcome of the command
additional messages are also returned - they appear before the table with output.
If option -s is given - _dlsctl_ command returns only its outcome, additional messages are hidden. Outcome in this case is
displayed as a plain text - without any names etc. More details concerning formatting of output using this option
can be found in a description of a _-s_ option and in description of certain commands.

Here is an example output of _experiment submit_ command:
<!-- language: lang-none -->

    dlsctl submit training.py
    
    
    | Experiment         | Status   |
    +--------------------+----------+
    | t20180423121021851 | Received |

    dlsctl experiment submit error_training.py

    Missing pod name during creation of registry port proxy.<br>

    | Experiment         | Status   |
    +--------------------+----------+
    | t20180423121021851 | Error    |
    

    dlsctl experiment submit -s error_training.py</i> </li>

    t20180423121021851


#### Interpretation of parameters describing experiments

Some commands accept parameters describing experiments/pods on which a certain operation should be executed. Examples
of such commands are - list, logs and cancel - user must pass to them information about objects on which commands should
do their work. Mentioned commands accept description of objects in the following format:

_<-m> <pod:>name \<status:status_name>_

__Where:__

-_\<-m>_ - optional, if given, string that follows this flag is treated as a regular expression  
-_\<pod>_ - optional, if given, the string after ":" is interpreted as a pod name  
-_name_ - optional, name of a pod or experiment (depending on whether <pod> suffix has been added)  
-_\<status:status_name>_- optional, if given, list is filtered based on a given status - _status_name_ is a status of a pod.
At least one of the parts mentioned above must be passed to a commend.

__Examples:__  
_-m pod:pod_name*_ - all experiments located on pods which names start with "pod_name"  
_-m exp_name* status:failed_ - all experiments with names starting with "exp_name" and whose pods are in status "failed"  
_pod:pod_name status:failed_ - all experiments located on a pod with a "pod_name" if this pod is in status "failed"
_status:failed_ - all experiments located on pods that failed

#### CLI logs configuration
Logs produced by _dlsctl_ are saved by default to /logs folder in _dlsctl_ configuration directory (e.g. ~/dls_ctl_config/logs/). Inspection of these logs may be helpful during troubleshooting. Log files are kept for 30 days by default, older files will be automatically deleted. Logging settings may be changed using following environment variables:
- DLS_CTL_LOG_DISABLE - if set, logging to a file will be disabled (e.g. `DLS_CTL_LOG_DISABLE=true`)
- DLS_CTL_LOG_RETENTION - configure log retention threshold in days (e.g. `DLS_CTL_LOG_RETENTION=7`), default value is 30
- DLS_CTL_LOG_DIRECTORY - configure custom directory where logs will be saved (e.g. `DLS_CTL_LOG_DIRECTORY=~/my-log-directory`), directory will be created if it does not exist. Default value is `<dlsctl configuration directory>/logs`
- DLS_CTL_LOG_LEVEL - configure minimal log level (e.g. `DLS_CTL_LOG_LEVEL=ERROR`), default value is DEBUG
- DLS_CTL_FILE_LOG_LEVEL - log level for logs stored in a file - default value is DEBUG   

#### Autocompletion
The _dlsctl_ application provides autocompletion functionality on Linux operating system with bash. To
turn on this functionality, a user should run the set-autocompletion.sh script, which is located in 
a folder with _dlsctl_ application. After executing this script a user must logoff and then log in again 
for the changes to take effect.

### List of actions

- [experiment](actions/experiment.md) - training and managing training jobs 
- [launch](actions/launch.md) - launching browser for Web UI and Tensorboard
- [predict](actions/predict.md) - deploy and m,anage inference on trained model
- [user](actions/user.md) - adding/deleting/listing users of the system 
- [verify](actions/verify.md) - verifies installation of _dlsctl_ application
- [version](actions/version.md) - displays version of _dlsctl_ application


# Advanced topics
- [Multi node training](advanced/multinode.md)
- [Installing custom libraries](advanced/customlibs.md)
- [Controlling packs parameters](advanced/packs.md)
