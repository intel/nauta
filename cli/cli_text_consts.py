#
# INTEL CONFIDENTIAL
# Copyright (c) 2018 Intel Corporation
#
# The source code contained or described herein and all documents related to
# the source code ("Material") are owned by Intel Corporation or its suppliers
# or licensors. Title to the Material remains with Intel Corporation or its
# suppliers and licensors. The Material contains trade secrets and proprietary
# and confidential information of Intel or its suppliers and licensors. The
# Material is protected by worldwide copyright and trade secret laws and treaty
# provisions. No part of the Material may be used, copied, reproduced, modified,
# published, uploaded, posted, transmitted, distributed, or disclosed in any way
# without Intel's prior express written permission.
#
# No license under any patent, copyright, trade secret or other intellectual
# property right is granted to or conferred upon you by disclosure or delivery
# of the Materials, either expressly, by implication, inducement, estoppel or
# otherwise. Any license under such intellectual property rights must be express
# and approved by Intel in writing.
#


VERBOSE_RERUN_MSG = "Use -v or -vv option for more info."

VERSION_CMD_TEXTS = {
    "help": "Displays the version of the installed dlsctl application.",
    "initial_platform_version": "Failed to get platform version.",
    "kubectl_int_error_msg": "Platform version check failure may occur for example due to invalid path to kubectl "
                             "config, invalid k8s credentials or k8s cluster being unavailable. Check your "
                             "KUBECONFIG environment variable and make sure that the k8s cluster is online.",
    "other_error_msg": "Unexpected error occurred during platform version check.",
    "table_app_row_name": "dlsctl application",
    "table_platform_row_name": "dls4e platform",
    "table_headers": ["Component", "Version"]
}

MOUNTS_CMD_TEXTS = {
    "help": "Displays a command that can be used to mount client's folders on his/her local machine.",
    "main_msg": """
                Use the following command to mount those folders:
                 - replace <MOUNTPOINT> with a proper location on your local machine)
                 - replace <DLS4E_FOLDER> with one of the following:
                        - input - User's private input folder (read/write)
                          (can be accessed as /mnt/input/home from training script).
                        - output - User's private output folder (read/write)
                          (can be accessed as /mnt/output/home from training script).
                        - input-shared - Shared input folder (read/write)
                          (can be accessed as /mnt/input/root/public from training script).
                        - output-shared - Shared output folder (read/write)
                          (can be accessed as /mnt/output/root/public from training script).
                        - input-output-ro - Full input and output directories, read only.
                Additionally, each experiment has a special folder that can be accessed
                as /mnt/output/experiment from training script. This folder is shared by Samba
                as output/<EXPERIMENT_NAME>.
                --------------------------------------------------------------------
                """,
    "user_is_admin_error_msg": "DLS4E doesn't create shares for administrators. Please execute this command as a "
                               "regular user.",
    "admin_check_error_msg": "Problems detected while verifying that current user is an administrator.",
    "get_mount_command_error_msg": "Error detected while gathering data needed for mounting Samba share."
}

CMDS_COMMON_TEXTS = {
    "invalid_regex_error_msg": "Regular expression provided for name filtering is invalid: {name}",
    "other_error_msg": "Failed to get experiments list."
}

VERIFY_CMD_TEXTS = {
    "help": "Command verifies whether all external components required by dlsctl are installed in proper versions. "
            "If something is missing, the application displays detailed information about it.",
    "kubectl_not_installed_error_msg": "kubectl is not installed.",
    "get_k8s_namespace_error_msg": "Failed to get current Kubernetes namespace.",
    "version_checking_msg": "Checking version of {dependency_name}. Installed version: ({installed_version}). "
                            "Supported version {supported_versions_sign} {expected_version}.",
    "dependency_verification_success_msg": "{dependency_name} verified successfully.",
    "invalid_version_warning_msg": "Warning: the installed version of {dependency_name} ({installed_version}) is "
                                   "not supported, supported version {supported_versions_sign} "
                                   "{expected_version}",
    "dependency_not_installed_error_msg": "{dependency_name} is not installed.",
    "dependency_version_check_error_msg": "Failed to get {dependency_name} version.",
    "dependency_verification_other_error_msg": "{dependency_name} - exception during verification."
}


USER_CMD_TEXTS = {
    "help": "Command for creating/deleting/listing users of the platform. Can only be run by a platform "
            "administrator."
}

USER_LIST_CMD_TEXTS = {
    "help": "List users.",
    "table_headers": ["Name", "Creation date", "Date of last submitted job", "Number of running jobs",
                      "Number of queued jobs"],
    "other_error_msg": "Failed to get users list."
}

USER_CREATE_CMD_TEXTS = {
    "help": "Command used to create a new user on the platform. Can only be run by a platform administrator.",
    "help_l": "If given - content of the generated user's config file is displayed on the screen only.",
    "help_f": "Name of file where user's configuration will be stored. If not given configuration is stored in the "
              "config. file.",
    "add_user_error_msg": "User has not been created.",
    "remove_user_error_msg": "Partially created user has not been removed successfully - please remove the user "
                             "manually.",
    "f_l_options_exclusion_error_msg": "Both -f/--filename and -l/--list_only options cannot be given. Please "
                                       "choose one of them.",
    "name_validation_error_msg": "Error detected while validating user name.",
    "user_not_admin_error_msg": "Only administrators can create new users.",
    "user_already_exists_error_msg": "User already exists.",
    "user_being_removed_error_msg": "User is still being removed.",
    "user_verification_error_msg": "Problems detected while verifying user with given user name.",
    "password_gather_error_msg": "The app encountered problems while gathering user's password.",
    "user_add_error_msg": "Error detected while adding of a user.",
    "user_creation_success_msg": "User {username} has been added successfully.",
    "user_not_ready_error_msg": "User {username} is still not ready.",
    "config_creation_error_msg": "Problems during creation of the kubeconfig with user's configuration.",
    "list_only_header": "Please use the following kubectl config to connect to this user.\n"
                        "----------------------------------------------------------------",
    "config_save_success_msg": "Configuration has been saved to the {filename} file.",
    "config_save_fail_msg": "File with configuration wasn't saved.",
    "config_save_fail_instructions_msg": "Content of the generated config file is as follows. Please copy it "
                                         "to a file manually."
}

USER_DELETE_CMD_TEXTS = {
    "help": "Command used to delete a user from the platform. Can be only run by a platform administrator.",
    "help_pr": "If this option is added, the command removes all of client's artifacts.",
    "user_not_admin_error_msg": "Only administrators can delete users.",
    "user_not_exists_error_msg": "User {username} doesn't exists.",
    "user_being_removed_error_msg": "User is still being removed.",
    "user_presence_verification_error_msg": "Problems during verifying users presence.",
    "delete_confirm_msg": "User {username} is about to be deleted. Do you want to continue?",
    "delete_abort_msg": "Operation of deleting of a user was aborted.",
    "purge_error_msg": "Some artifacts belonging to a user weren't removed.",
    "delete_in_progress_msg": "User is still being deleted. Please check status of this user in a while.",
    "delete_success_msg": "User {username} has been deleted.",
    "proxy_error_log_msg": "Error during closing of a proxy for elasticsearch.",
    "proxy_error_user_msg": "Elasticsearch proxy hasn't been closed properly. Check whether it still exists, if "
                            "yes - close it manually.",
    "other_error_log_msg": "Error during deleting a user of a user.",
    "other_error_user_msg": "User hasn't been deleted due to technical reasons.",
    "deletion_check_presence": "Checking presence of a user that is going to be deleted...",
    "deletion_start_deleting": "Deleting of a user is starting now...",
    "deletion_start_purging": "Purging of a user is starting now...",
    "deletion_verification_of_deleting": "Verifying, whether a user has been deleted properly...",
    "deletion_deleting_namespace": "- deleting user's namespace",
    "deletion_deleting_users_objects": "- deleting user's objects",
    "deletion_deleting_users_experiments": "- deleting user experiments' logs"
}

LAUNCH_CMD_TEXTS = {
    "help": "Command for launching web user-interface or tensorboard.",
    "help_p": "Port on which service will be exposed locally.",
    "help_n": "Run command without a web browser starting, only proxy tunnel is created",
    "webui_help": "Subcommand for launching webUI with credentials",
    "app_proxy_exists_error_msg": "K8s proxy hasn't been closed properly. Check whether it still exists, if yes - "
                                  "close it manually.",
    "app_proxy_other_error_msg": "Other exception during launching web application.",
    "tb_help": "Subcommand for launching tensorboard with credentials",
    "tb_help_tscp": "Local port on which tensorboard service client will be started.",
    "tb_invalid_runs_msg": "There is no data for the following experiments : {invalid_runs}\n"
                           "Tensorboard will present information from the rest of given experiments.",
    "tb_create_error_msg": "Failed to create tensorboard!",
    "tb_waiting_msg": "Please wait for Tensorboard to run...",
    "tb_waiting_for_tb_msg": "Tensorboard instance: {tb_id} still in {tb_status_value} status, waiting for "
                             "RUNNING...",
    "tb_timeout_error_msg": "Tensorboard failed to run - timeout."
}

PREDICT_CMD_TEXTS = {
    "help": "Command for starting, stopping, and managing prediction jobs and instances. To get further help on "
            "commands use COMMAND with -h or --help option."
}

PREDICT_LIST_CMD_TEXTS = {
    "help_a": "Show all prediction instances, regardless of the owner.",
    "help_n": "A regular expression to narrow down list to prediction instances that match this expression.",
    "help_s": "List prediction instances with matching status."
}

PREDICT_LAUNCH_CMD_TEXTS = {
    "help": "Starts a new prediction instance that can be used for performing prediction, classification and "
            "regression tasks on trained model.",
    "help_n": "The name of this prediction instance.",
    "help_m": "Path to saved model that will be used for inference. Model must be located on one of the input or "
              "output system shares (e.g. /mnt/input/saved_model).",
    "instance_start_error_msg": "Failed to create prediction instance.",
    "instance_info_msg": "\nPrediction instance URL (append method verb manually, e.g. :predict):\n"
                         "{inference_instance_url}\n\nAuthorize with following header:\n{authorization_header}",
    "instance_url_error_msg": "Failed to obtain prediction instance URL.",
    "table_headers": ["Prediction instance", "Model Location", "Status"]
}

PREDICT_STREAM_CMD_TEXTS = {
    "help": "Perform stream prediction task on deployed prediction instance.",
    "help_n": "Name of prediction session.",
    "help_d": "Path to JSON data file that will be streamed to prediction instance. Data must be formatted such "
              "that it is compatible with the SignatureDef specified within the model deployed in selected "
              "prediction instance.",
    "help_m": "Method verb that will be used when performing inference. Predict verb is used by default.",
    "instance_not_exists_error_msg": "Prediction instance {name} does not exist.",
    "instance_not_running_error_msg": "Prediction instance {name} is not in {running_code} state.",
    "instance_get_fail_error_msg": "Failed to get prediction instance {name} URL.",
    "json_load_error_msg": "Failed to load {data} data file. Make sure that provided file exists and is in a "
                           "valid JSON format.",
    "inference_other_error_msg": "Failed to perform inference. Reason: {exception}",
    "inference_error_response_msg": "\n Response: {response_text}"
}

PREDICT_CANCEL_CMD_TEXTS = {
    "help": "Cancels prediction instance/s chosen based on criteria given as a parameter.",
    "help_p": "If given, then all information concerning all prediction instances, completed and currently "
              "running, is removed from the system.",
    "help_m": "If given, command searches for prediction instances matching the value of this option.",
    "experiment_name": "prediction instance",
    "experiment_name_plural": "prediction instances",
}

PREDICT_BATCH_CMD_TEXTS = {
    "help": "Uses specified dataset to perform inference. Results stored in output file",
    "help_data": "location of a folder with data that will be used to perform the batch inference. Value should points "
                 "out the location from one of the system's shares.",
    "help_model_location": "Path to saved model that will be used for inference. Model must be located on one of the " 
                           "input or output system shares (e.g. /mnt/input/saved_model).",
    "help_model_name": "Name of a model passed as a servable name. By default it is the name of directory in model's " 
                       "location.",
    "help_name": "name of a predict session",
    "help_output": "location of a folder where outputs from inferences will be stored. Value should points out the "
                   "location from one of the system's shares.",
    "other_instance_creation_error_msg": "Failed to create batch prediction instance.",
    "table_name_header": "Prediction instance",
    "table_model_location_header": "Model location",
    "table_status_header": "Status",
    "table_headers": ["Prediction instance", "Model location", "Status"]
}

EXPERIMENT_CMD_TEXTS = {
    "help": "Command for starting, stopping, and managing training jobs."
}

EXPERIMENT_LIST_CMD_TEXTS = {
    "help_a": "Show all experiments, regardless of the owner.",
    "help_n": "A regular expression to narrow down list to experiments that match this expression.",
    "help_s": "List experiments with matching status."
}

EXPERIMENT_TEMPLATE_LIST_CMD_TEXTS = {
    "help": "Returns a list of available templates that can be used to submit training jobs.",
    "lack_of_packs_error_msg": "Lack of installed packs."
}

EXPERIMENT_LOGS_CMD_TEXTS = {
    "help": "Show logs for a given experiment.",
    "help_s": "Show all events with this specified minimal and greater severity.",
    "help_sd": "Retrieve all logs produced on and after this date (use ISO 8601 date format).",
    "help_ed": "Retrieve all logs produced on and before this date (use ISO 8601 date format).",
    "help_i": "Comma separated list of pod IDs. If provided, only logs from these pods will be returned.",
    "help_p": "Get logs only for pods with given status.",
    "proxy_creation_error_msg": "Error during creation of a proxy for elasticsearch.",
    "logs_get_other_error_msg": "Failed to get experiment logs.",
    "experiment_not_exists_error_msg": "Experiment with name {experiment_name} does not exist.",
    "local_port_occupied_error_msg": "Error during creation of a proxy for elasticsearch. {exe.message}",
    "proxy_close_log_error_msg": "Error during closing of a proxy for elasticsearch.",
    "proxy_close_user_error_msg": "Elasticsearch proxy hasn't been closed properly. Check whether it still exists, if "
                                  "yes - close it manually."
}

EXPERIMENT_SUBMIT_CMD_TEXTS = {
    "help": "Command used to submitting training scripts.",
    "help_n": "Name for this experiment.",
    "help_sfl": "Name of a folder with additional files used by a script, e.g., other .py files, data etc. If not "
                "given - its content won't be copied into an image.",
    "help_t": "Name of a template used to create a deployment. By default, this is a single-node tensorflow training."
              " Template is chosen. List of available templates might be obtained by"
              " Issuing dlsctl experiment template_list command.",
    "help_p": " Additional pack param in format: 'key value' or 'key.subkey.subkey2 value'. For lists use: "
              "'key \"['val1', 'val2']\"' For maps use: 'key \"{'a': 'b'}\"' ",
    "help_pr": "Values (set or range) of a single parameter.",
    "help_ps": "Set of values of one or several parameters.",
    "script_not_found_error_msg": "Cannot find: {script_location}. Make sure that provided path is correct.",
    "default_script_not_found_error_msg": "Cannot find script: {default_script_name} in directory: {script_directory}. "
                                          "If path to directory was passed as submit command argument, then "
                                          "{default_script_name} file has to exist in that directory.",
    "script_dir_not_found_error_msg": "Cannot find: {script_folder_location}. script_folder_location must be a path to "
                                      "existing directory. ",
    "submit_start_log_msg": "Submit - start",
    "submit_start_user_msg": "Submitting experiments.",
    "submit_error_msg": "Problems during submitting experiment: {exception_message}",
    "submit_other_error_msg": "Other problems during submitting experiment.",
    "failed_runs_log_msg": "There are failed runs"
}

EXPERIMENT_INTERACT_CMD_TEXTS = {
    "help": "Launches a local browser with Jupyter Notebook. If the script name argument is given, then script is put "
            "into the opened notebook.",
    "help_n": "The name of this Jupyter Notebook session.",
    "help_f": "File with a notebook that should be opened in Jupyter notebook.",
    "help_pn": "Port on which service will be exposed locally.",
    "help_p": " Additional pack param in format: 'key value' or 'key.subkey.subkey2 value'. For lists use: "
              "'key \"['val1', 'val2']\"' For maps use: 'key \"{'a': 'b'}\"' ",
    "help_no_launch": "Run command without a web browser starting, only proxy tunnel is created",
    "experiment_get_error_msg": "Problems during loading a list of experiments.",
    "name_already_used": "The chosen name ({name}) is already used by an experiment other than Jupyter Notebook. "
                         "Please choose another one.",
    "confirm_experiment_creation": "Experiment with a given name doesn't exist. Should the app continue and create a "
                                   "new one? ",
    "submitting_experiment_user_msg": "Submitting interactive experiment.",
    "submit_error_msg": "Error during starting jupyter notebook session: {exception_message}",
    "submit_other_error_msg": "Other error during starting jupyter notebook session.",
    "session_exists_msg": "Jupyter notebook's session exists. dlsctl connects to this session ...",
    "notebook_state_check_error_msg": "Error during checking state of Jupyter notebook.",
    "attaching_script_not_supported_msg": "Attaching script to existing Jupyter notebook's session is not supported. "
                                          "Please create a new Jupyter notebook's session to attach script.",
    "notebook_not_ready_error_msg": "Jupyter notebook is still not ready. Please try to connect to it by running "
                                    "interact command another time passing a name of a current Jupyter notebook "
                                    "session.",
    "proxy_closing_error_msg": "K8s proxy hasn't been closed properly. Check whether it still exists, if yes - close "
                               "it manually.",
    "session_launch_other_error_msg": "Other exception during launching interact session."
}

EXPERIMENT_CANCEL_CMD_TEXTS = {
    "help": "Cancels experiment/s chosen based on criteria given as a parameter.",
    "help_p": "If given, then all information concerning all experiments, completed and currently running, is removed "
              "from the system.",
    "help_m": "If given, command searches for experiments matching the value of this option. This option cannot be "
              "used along with the NAME argument.",
    "name_m_both_given_error_msg": "Both name and -m option cannot be given. Please choose one of them.",
    "name_m_none_given_error_msg": "Error: Name or -m option must be given. Please pass one of them.",
    "list_runs_error_msg": "Problems during loading a list of {experiment_name_plural}.",
    "lack_of_experiments_error_msg": "Lack of {experiment_name_plural} fulfilling given criteria. Name or match string "
                                     "parameters do not match any existing {experiment_name}. Run 'dlsctl exp list' to "
                                     "find out what are the names of existing {experiment_name_plural}.",
    "experiments_already_cancelled_error_msg": "{experiment_name_plural} fulfilling given criteria have been cancelled "
                                               "already.",
    "already_cancelled_list_header": "The following {experiment_name_plural} have been cancelled already:",
    "can_be_cancelled_list_header": "The following {experiment_name_plural} can still be cancelled:",
    "will_be_cancelled_list_header": "The following {experiment_name_plural} will be cancelled:",
    "will_be_purged_list_header": "The following {experiment_name_plural} will be purged:",
    "confirm_cancel_msg": "Do you want to continue with cancellation of those {experiment_name_plural}?",
    "cancellation_aborted_msg": "Operation of cancellation of {experiment_name_plural} was aborted.",
    "other_cancelling_error_msg": "Error during cancelling an experiment.",
    "proxy_closing_error_log_msg": "Error during closing of a proxy for elasticsearch.",
    "proxy_closing_error_user_msg": "Elasticsearch proxy hasn't been closed properly. Check whether it still exists, "
                                    "if yes - close it manually.",
    "port_occupied_error_log_msg": "Error during creation of proxy - port is occupied.",
    "port_occupied_error_user_msg": "Error during creation of a proxy for elasticsearch. {exception_message}",
    "proxy_open_error_msg": "Error during creation of a proxy for elasticsearch.",
    "successfully_cancelled_list_header": "The following {experiment_name_plural} were cancelled succesfully:",
    "failed_to_cancel_list_header": "The following {experiment_name_plural} weren't cancelled properly:",
    "get_experiment_error_msg": "Error during loading experiment's data.",
    "purging_start_msg": "Purging {run_name} experiment ...",
    "incomplete_purge_error_msg": "Not all {experiment_name}'s components were removed properly.",
    "canceling_runs_start_msg": "Cancelling {run_name} {experiment_name} ...",
    "deleting_related_objects_msg": "Deleting objects related to {run_name} {experiment_name} ...",
    "cancel_setting_status_msg": "Setting {experiment_name} status to CANCELLED ...",
    "incomplete_cancel_error_msg": "Not all components of {run.name} {experiment_name} were deleted ...\nExperiment "
                                   "remains in its previous state."
}

EXPERIMENT_VIEW_CMD_TEXTS = {
    "help": "Displays details of experiment with a given name.",
    "help_t": "If given, then exposes a tensorboard's instance with experiment's data.",
    "container_details_msg": """
                             - Name: {name}
                                - Status: {status}
                                - Volumes:
                                    {volumes}
                                - Resources:
                             {resources}
                             """,
    "experiment_not_found_error_msg": "Experiment \"{experiment_name}\" not found.",
    "pods_participating_list_header": "\nPods participating in the execution:\n",
    "pods_table_headers": ["Name", "Uid", "Status", "Container Details"],
    "view_other_error_msg": "Failed to get experiment.",
    "container_not_created_msg": "Not created",
    "container_running_msg": "Running, ",
    "container_terminated_msg": "Terminated, ",
    "container_waiting_msg": "Waiting, ",
    "container_requests_list_header": "- Requests:\n{}",
    "container_limits_list_header": "- Limits:\n{}"
}

EXPERIMENT_COMMON_TEXTS = {
    "confirm_exp_dir_deletion_msg": "Experiment data directory: {run_environment_path} already exists. It will be "
                                    "deleted in order to proceed with experiment submission. Do you want to continue?",
    "unable_to_continue_exp_submission_error_msg": "Cannot continue experiment submission. Please delete experiment's " 
                                                   "data directory {run_environment_path} manually or use different " 
                                                   "name for experiment.",
    "create_env_msg_prefix": "Experiment's environment hasn't been created. Reason - {reason}",
    "dir_cant_be_copied_error_text": "Additional folder cannot be copied into experiment's folder.",
    "exp_dir_cant_be_created": "Folder with experiments' data cannot be created.",
    "training_script_cant_be_created": "Training script cannot be created.",
    "submit_preparation_error_msg": "Problem during preparation of experiments' data.",
    "local_docker_tunnel_error_msg": "Error during creation of a local docker-host tunnel.",
    "env_creation_error_msg": "Problems during creation of environments.",
    "confirm_submit_msg": "Please confirm that the following experiments should be submitted.",
    "confirm_submit_question_msg": "Do you want to continue?",
    "submission_fail_error_msg": "Experiment submission failed. Try verbose option for more detailed information about "
                                 "failure cause.",
    "proxy_close_error_msg": "Docker proxy hasn't been closed properly. Check whether it still exists, if yes - close " 
                             "it manually.",
    "proxy_open_error_msg": "Error during opening of a proxy for a docker registry.",
    "submit_other_error_msg": "Other error during submitting experiments.",
    "docker_tunnel_close_error_msg": "Local Docker-host tunnel hasn't been closed properly. Check whether it still "
                                     "exists, if yes - close it manually.",
    "draft_templates_not_generated_error_msg": "Draft templates haven't been generated. Reason - {reason}",
    "job_not_deployed_error_msg": "Job hasn't been deployed. Reason - {reason}",
    "incorrect_param_format_error_msg": "Parameter {param_name} has incorrect format.",
    "param_ambiguously_defined": "Parameter {param_name} ambiguously defined.",
    "param_set_incorrect_format_error_msg": "One of -ps options has incorrect format.",
    "experiment_name_too_long_error_msg": "Name given by a user cannot be longer than 30 characters."
}

DRAFT_CMD_TEXTS = {
    "docker_image_not_built": "Docker image hasn't been built.",
    "docker_image_not_sent": "Docker image hasn't been sent to the cluster.",
    "app_not_released": "Application hasn't been released.",
    "deployment_not_created": "Deployment hasn't been created.",
    "pack_not_exists": "Chosen pack doesn't exist."
}

PACKS_TF_TRAINING_TEXTS = {
    "config_not_updated": "Configuration hasn't been updated.",
    "cant_parse_value": "Can not parse value: \"{value}\" to list/dict. Error: {error}"
}

UTIL_SYSTEM_TEXTS = {
    "command_exe_fail_error_msg": "COMMAND execution FAIL: {command}",
    "unsupported_platform_error_msg": "unsupported platform: {sys_platform}, supported: {supported_os}!",
    "port_availability_check_error_msg": "Problem during checking port's availability."
}

UTIL_SOCAT_TEXTS = {
    "socat_container_start_fail_msg": "failed to start socat container! expected status: 'running', got: "
                                      "{container_status}"
}

UTIL_JUPYTER_TEXTS = {
    "ipynb_conversion_error_msg": "Py to Ipynb conversion error."
}

UTIL_LAUNCHER_TEXTS = {
    "local_docker_tunnel_error_msg": "Error during creation of a local docker-host tunnel.",
    "browser_starting_msg": "Browser will start in few seconds. Please wait...",
    "no_web_browser_error_msg": "Cannot find a suitable web browser. Try running this command with --no-launch option.",
    "proxy_close_error_msg": "Error during closing of a proxy for a {app_name}",
    "web_app_lauch_fail_msg": "Failed to launch web application.",
    "go_to_msg": "Go to {url}",
    "proxy_created_msg": "Proxy connection created.\nPress Ctrl-C key to close a port forwarding process...",
    "proxy_created_error_msg": "Error during creation of a proxy for a {app_name}.",
    "proxy_created_extended_error_msg": "Error during creation of a proxy for a {app_name}. {reason}"
}

UTIL_HELM_TEXTS = {
    "helm_release_removal_error_msg": "Error during removal of helm release {release_name}."
}

TENSORBOARD_CLIENT_TEXTS = {
    "invalid_runs_error_msg": "There is no data for the following experiments : {invalid_runs_list}",
    "runs_not_exist_error_msg": "Experiments given as parameters of the command don't exist."
}

UTIL_DOCKER_TEXTS = {
    "tags_get_error_msg": "Error during getting list of tags for an image.",
    "image_delete_error_msg": "Error during deletion of an image."
}

UTIL_DEPENDENCIES_CHECKER_TEXTS = {
    "parse_fail_error_msg": "Failed to parse version({version_field}) from following input: {version_output}",
    "version_cmd_fail_msg": "Failed to run {version_cmd} with args {version_cmd_args}. Output: {output}",
    "dependency_not_installed_error_msg": "{dependency_name} is not installed.",
    "version_get_fail_msg": "Failed to get {dependency_name} version.",
    "invalid_dependency_error_msg": "{dependency_name} installed version: {installed_version}, does not match expected "
                                    "version: {expected_version}"
}

UTIL_CONFIG_TEXTS = {
    "user_dir_not_found_error_msg": "Cannot find {user_path} directory from {config_env_name} env!",
    "dls_ctl_config_dir_not_found_error_msg": "Cannot find {config_dir_name} directory in {binary_config_dir_path} and "
                                              "{user_local_config_dir_path}. Use {config_env_name} env to point "
                                              "{config_dir_name} directory location"
}

PLATFORM_RESOURCES_CUSTOM_MODEL_TEXTS = {
    "invalid_k8s_name": "name must consist of lower case alphanumeric characters, '-' or '.', and must start and end "
                        "with an alphanumeric character "
}

PLATFORM_RESOURCES_EXPERIMENTS_TEXTS = {
    "regex_compilation_fail_msg": "Failed to compile regular expression: {name_filter}",
    "k8s_response_load_error_msg": "preparing load of ExperimentKubernetes response object error - {err}",
    "k8s_dump_preparation_error_msg": "preparing dump of ExperimentKubernetes request object error - {err}",
    "experiment_already_exists_error_msg": " experiment with name: {name} already exist!",
    "experiment_update_error_msg": "Error during patching an Experiment"
}

PLATFORM_RESOURCES_RUNS_TEXTS = {
    "regex_compilation_fail_msg": "Failed to compile regular expression: {name_filter}",
    "k8s_response_load_error_msg": "preparing load of RunKubernetes response object error - {err}",
    "k8s_dump_preparation_error_msg": "preparing dump of RunKubernetes request object error - {err}",
    "run_update_error_msg": "Error during patching a Run"
}

PLATFORM_RESOURCES_USERS_TEXTS = {
    "username_cannot_be_empty_error_msg": "Name of a user cannot be an empty string.",
    "username_too_long_error_msg": "Name of a user cannot be longer than 32 characters.",
    "incorrect_k8s_username_error_msg": "Incorrect k8s user name."
}

UTIL_KUBECTL_TEXTS = {
    "no_available_port_error_msg": "Available port cannot be found.",
    "proxy_creation_other_error_msg": "Other error during creation of port proxy.",
    "proxy_creation_missing_port_error_msg": "Missing port during creation of port proxy.",
    "user_presence_check_error_msg": "Error during checking user's presence.",
    "k8s_object_delete_error_msg": "Error when deleting k8s object: {output}",
    "k8s_cluster_no_connection_error_msg": "Cannot connect to K8S cluster: {output}"
}

UTIL_K8S_INFO_TEXTS = {
    "other_find_namespace_error_msg": "Other find_namespace error",
    "namespace_delete_error_msg": "Error during deleting namespace {namespace}",
    "config_map_access_error_msg": "Problem during accessing ConfigMap : {name}.",
    "lack_of_default_token_error_msg": "Lack of default-token on a list of tokens.",
    "empty_list_of_tokens_error_msg": "Empty list of tokens.",
    "gathering_users_token_error_msg": "Problem during gathering users token.",
    "gathering_password_error_msg": "Error during gathering users password.",
    "lack_of_password_error_msg": "Lack of password."
}

UTIL_K8S_PROXY_TEXTS = {
    "proxy_enter_error_msg": "k8s_proxy - enter - error",
    "proxy_exit_error_msg": "k8s_proxy - exit - error",
    "tunnel_not_ready_error_msg": "connection on {address}:{port} NOT READY!"
}
