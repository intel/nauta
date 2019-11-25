# Getting Started

This section provides brief examples for performing some of the most essential and valuable 
tasks supported by Nauta. 

**Note:** Several commands and training scripts in this section require access to the internet to download data, scripts, and so on.

The section discusses the following main topics: 

 - [Verifying Installation](#verifying-installation)
 - [Overview of nctl Commands](#overview-of-nctl-commands)
 - [Example Experiments](#example-experiments)
 - [Adding Experiment Metrics](#adding-experiment-metrics)
 - [Viewing Experiment Results from the Web UI](#viewing-experiment-results-from-the-web-ui)
 - [Launching Kubernetes Dashboard](#launching-kubernetes-dashboard)
 - [Launching TensorBoard](#launching-tensorboard)
 - [Inference](#inference)
 - [Overview of nctl Commands](#overview-of-nctl-commands)
 - [Viewing Experiment Output Folder](#viewing-experiment-output-folder)
 - [Removing Experiments](#removing-experiments)


## Verifying Installation

Check that the required software packages are available in terminal by PATH and verified that the correct version is used.

### Proxy Environment Variables 

If you are behind a proxy, remember to set your:

* `HTTP_PROXY`, `HTTPS_PROXY` and `NO_PROXY` environment variables

* `http_proxy`, `https_proxy` and `no_proxy` environment variables

### Confirm Installation

To verify your installation has completed, execute the following command: 

`nctl verify`

If any installation issues are found, the command returns information about the cause: which application should be installed and in which version. This command also checks if the CLI can connect to Nauta; and, if port forwarding to Nauta is working correctly. If no issues are found, a message indicates checks were successful. The following examples are the results of this command:

```
This OS is supported.
kubectl verified successfully.
kubectl server verified successfully.
helm client verified successfully.
helm server verified successfully.
git verified successfully.
```

## Overview of nctl Commands

Each `nctl` command has at least three options:

1. `-v, --verbose` - Set verbosity level:
    * `-v` for INFO - Basic logs on INFO/EXCEPTION/ERROR levels are displayed.
    * `-vv` for DEBUG - Detailed logs on INFO/DEBUG/EXCEPTION/ERROR levels are displayed.
2. `-h, --help` - The application displays the usage and options available for a specific command or subcommand.
3. `-f, --force` - Ignore (most) confirmation prompts during command execution.
 
### Accessing Help

To access help for any command, use the `--help` or `-h` parameters. The following command provides a list and brief description of all nctl commands. 

`nctl --help`

The results are shown below.

```
Usage: nctl COMMAND [options] [args]...

  Nauta Client

 Displays additional help information when the -h or --help COMMAND is used.

Options:
  -h, --help  Displays help messaging information.

Commands:
  config, cfg      Set limits and requested resources in templates.          
  experiment, exp  Start, stop, or manage training jobs.   
  launch, l        Launch the web user-interface or TensorBoard. Runs as a process 
                   in the system console until the user stops the process. 
                   To run in the background, add '&' at the end of the line.
  mount, m         Displays a command to mount folders on a local machine.
  predict, p       Start, stop, and manage prediction jobs and instances.
  user, u          Create, delete, or list users of the platform. 
                   Can only be run by a platform administrator.
  verify, ver      Verifies whether all required external components contain 
                   the proper versions installed.
  version, v       Displays the version of the installed nctl application.

```

## Example Experiments

The Nauta installation includes sample training scripts and utility scripts, contained in the `examples` folder, that can be run to demonstrate how to use Nauta. This section describes how to use these scripts. 

### Examples Folder Content

The examples folder in the nctl installation contains these following experiment scripts:

* `mnist_single_node.py` - Training of digit classifier in single node setting
* `mnist_multinode.py` - Training of digit classifier in distributed TensorFlow setting
* `mnist_horovod.py` - Training of digit classifier in Horovod
* `mnist_saved_model.py` - Training of digit classifier with saving the model at the end (requires mnist_input_data.py file)
* `mnist_tensorboard.py` - Training of digit classifier which displays summaries in TensorBoard (requires at least 2Gi of memory)

### Utility Scripts

There are two utility scripts, these are:

`mnist_converter_pb.py` 

`mnist_checker.py`

These utility scripts used for inference process and model verification.

**Note:** Experiment scripts _must be_ written in Python. 

## Submitting an Experiment

Launch training experiments with Nauta using the following:

**Syntax**:

`nctl experiment submit [options] SCRIPT-LOCATION [-- script-parameters]`

**Where:**

* `SCRIPT-LOCATION`: The path and name of the Python script used to perform this experiment.

To submit the example experiments, use the following:

#### Single Node Training

For single node training (template parameter in this case is optional)

`nctl experiment submit -t tf-training-single examples/mnist_single_node.py --name single`

#### Multinode Training

For multinode training:

`nctl experiment submit -t tf-training-multi examples/mnist_multinode.py --name multinode`

#### Horovod Training

For Horovod training:

`nctl experiment submit -t tf-training-horovod examples/mnist_horovod.py --name horovod `

The included example scripts _do not_ require an external data source. The scripts automatically download the MNIST dataset. Templates referenced here have set CPU and Memory requirements. The list of available templates can be obtained by issuing `nctl template list` command.

**Note:** To run TensorBoard, TensorBoard data _must be_ written to a folder in the directory `/mnt/output/experiment`. This example script satisfies this requirement; however, your scripts _must_ meet the same requirement.

The following example shows how to submit a MNIST experiment and write the TensorBoard data to a folder in your NAUTA output folder.

Enter the following command to run this example:

`nctl experiment submit -t tf-training-single examples/mnist_single_node.py --name single`

#### Result of this Command

The execution of the submit command may take a few minutes the first time. When the experiment submission is complete, the following result is displayed:

```

Submitting experiments.
| Experiment   | Parameters           | State   | Message   |
|--------------+----------------------+---------+-----------|
| single       | mnist_single_node.py | QUEUED  |           |

```

#### Viewing Experiment Status

Use the following command to view the status of all your experiments:

**Syntax**: `nctl experiment list [options]`

Execute this command: 

`nctl experiment list --brief`

As shown below, an experiment's status displays. This is an example only. The `--brief` option returns a short version of results, as shown.

```

Submitting experiments.
| Experiment   | Parameters           | State   | Message   |
|--------------+----------------------+---------+-----------|
| single       | mnist_single_node.py | QUEUED  |           |

```
```

| Experiment                          | Submission date        | Owner | State     |
|--------------+----------------------+---------+----------------------------------|
| mnist-single-node-tb                | 2019-03-13 04:57:58 PM | user1 |  QUEUED   |
| mnist-tb                            | 2019-03-13 05:00:39 PM | user1 |  COMPLETE |
| mnist-tb 2-1                        | 2019-03-13 05:49:59 PM | user1 |  COMPLETE |
| test-experiment                     | 2019-03-13 06:00:39 PM | user1 |  QUEUED   |
| single-experiment                   | 2019-03-13 01:49:59 PM | user1 |  QUEUED   |

```
**Note:** Where mnist-tb is shown, this indicates _the name_ of the _experiment_.   

### Monitoring Training

There are four ways to monitor training in Nauta, all which are discussed in the following sections. 

 - [Viewing Experiment Logs](#viewing-experiment-logs)
 - [Adding Experiment Metrics](#adding-experiment-metrics)  
 - [Viewing Experiment Results from the Web UI](#viewing-experiment-results-from-the-web-ui)
 - [Launching TensorBoard](#launching-tensorboard)

### Viewing Experiment Logs 

To view the experiment logs, execute the following command.

**Syntax**: `nctl experiment logs [options] EXPERIMENT-NAME`

Execute this command:

`nctl experiment logs single`

As shown below, a log displays the example results.

```
2019-03-20T16:11:38+00:00 mnist-tb-master-0 Step 0, Loss: 2.3015756607055664, Accuracy: 0.078125
2019-03-20T16:11:44+00:00 mnist-tb-master-0 Step 100, Loss: 0.13010963797569275, Accuracy: 0.921875
2019-03-20T16:11:49+00:00 mnist-tb-master-0 Step 200, Loss: 0.07017017900943756, Accuracy: 0.984375
2019-03-20T16:11:55+00:00 mnist-tb-master-0 Step 300, Loss: 0.08880224078893661, Accuracy: 0.984375
2019-03-20T16:12:00+00:00 mnist-tb-master-0 Step 400, Loss: 0.15115690231323242, Accuracy: 0.953125
2019-03-20T16:12:07+00:00 mnist-tb-master-0 Validation accuracy: 0.980400025844574
```
**Note:** Where mnist-tb is shown in the experiment logs, this indicates _the name_ of the _experiment_.   


## Adding Experiment Metrics

Experiments launched in Nauta can output additional kinds of metrics using the _publish function_ from the experiment metrics API. To see an example of metrics published with the single experiment executed in the above example, execute the following command:

`nctl experiment list`

As shown in the example, an example experiment list is shown (scroll right to see full contents). 

```

| Experiment   | Parameters           | Metrics                     | Submission date        | Start date             | End date               | Owner   | State    | Template name      |
|--------------+----------------------+-----------------------------+------------------------+------------------------+------------------------+---------+----------+--------------------|
| mnist-tb     | mnist_single_node.py |                             | 2019-03-20 05:11:15 PM | 2019-03-20 05:11:20 PM |                        | user1   | RUNNING  | tf-training-single |
| single       | mnist_single_node.py | accuracy: 0.96875           | 2019-03-20 05:03:12 PM | 2019-03-20 05:04:32 PM | 2019-03-20 05:05:15 PM | user1   | FAILED   | tf-training-single |
|              |                      | global_step: 499            |                        |                        |                        |         |          |                    |
|              |                      | loss: 0.08342029            |                        |                        |                        |         |          |                    |
|              |                      | validation_accuracy: 0.9818 |                        |                        |                        |         |          |                    |
| single2      | mnist_single_node.py | accuracy: 0.953125          | 2019-03-20 05:06:19 PM | 2019-03-20 05:06:24 PM | 2019-03-20 05:07:05 PM | user1   | COMPLETE | tf-training-single |
|              |                      | global_step: 499            |                        |                        |                        |         |          |                    |
|              |                      | loss: 0.078533165           |                        |                        |                        |         |          |                    |
|              |                      | validation_accuracy: 0.9838 |                        |                        |                        |         |          |                    |

```
### Adding Experiment Metrics: Instructions

To add metrics to an experiment file you have created, you need to edit the experiment file to use the `experiment_metrics.api` and then publish the accuracy in your experiment file. Execute the following steps: 

1. Add the metrics library API with the following entry in your experiment file:
   `from experiment_metrics.api import publish`

2.	Add metrics for publishing the last step's accuracy by adding this code in the `def feed_dict` definition after the for loops: 

   ```
   metrics = {}
   metrics["accuracy_step_{}".format(i)] = str(acc)
   publish(metrics)
   ```
3.	Save the changes.

4.	Submit the experiment again, but with a different name. 
      
5.	The published metrics can now be viewed. 

    `nctl experiment list`

### Saving Metrics for Multinode Experiments

Storing at the same time two (or more) metrics with the same key from two different nodes may lead to errors (such as losing  some logs) due to conflicting names. To avoid this, adding metrics for multinode experiments should be done using one of the two following methods:

### Method 1

The key of a certain metric should also contain a node identificator from which this metric comes. Creation of such identificator can be done in the following ways:

   * For Horovod multinode training jobs, the result of the `rank()` function provided by the `horovod` package can be used
    as a node's identificator.  
    
   * For `tfjob` multinode training jobs, a user can take all necessary info from the TF_CONFIG environment variable. An example piece of a code creating such identificator, is:
    
### Node Identificator Example

    ```
    tf_config = os.environ.get('TF_CONFIG')
    if not tf_config:
        raise RuntimeError('TF_CONFIG not set!')

    tf_config_json = json.loads(tf_config)

    job_name = tf_config_json.get('task', {}).get('type')
    task_index = tf_config_json.get('task', {}).get('index')
    # final node identificator `node_id = '-'.join(job_name,task_index)`
    ```

### Method 2

Only one node should store metrics. Deciding which node should store metrics can be done in the following ways:  

   * For `horovod` multinode training jobs, the horovod python library provides the `rank()` function that returns a number
of a current worker. _Master_ is marked with the number 0, so only a pod with this number should store logs.

   * For `tfjob` multinode training jobs, because there is no dedicated master node, a user should choose which worker should be responsible for storing metrics. The identificator of a current worker can be obtained as described in _[Method 1](#method-1)_. A user should choose one of such identificators and store logs only from a node having this chosen ID. 
   
## Viewing Experiment Results from the Web UI

The web UI lets you explore the experiments you have submitted. To view your experiments at the web UI, enter the following command at the command prompt:

`nctl launch webui`

**Note:** If you are using CLI through remote access, you will need to setup an X server for tunneling over SSH with port forwarding or use SSH Proxy command tunneling. After establishing a tunnel from the gateway to your local machine, you can use the URL provided by nctl.

An example is shown in the screen below.

![](images/web_ui.png) 


* **Name:** The left-most column lists the experiments by name.
* **Status:** This column reveals experiment’s current status, one of: `QUEUED, RUNNING, COMPLETE, CANCELLED, FAILED, CREATING`.
* **Submission Date:** This column gives the submission date in the format: MM/DD/YYYY, hour:min:second AM/PM.
* **Start Date:** This column shows the experiment start date in the format: MM/DD/YYYY, hour:min:second AM/PM.
* **Duration:** This column shows the duration of execution for this experiment in days, hours, minutes and seconds.
* **Type:** Experiment Type can be Training, Jupyter, or Inference. Training indicates that the experiment was launched from the CLI. Jupyter indicates that the experiment was launched using Jupyter Notebook. Inference means that training is largely complete and you have begun running predictions (Inference) with this model.

You can perform the tasks discussed below in the web UI.

### Expand Experiment Details

Click _listed experiment name_ to see additional details for that experiment. The following details are examples only. 
This screen is divided into two frames: left-side and right-side frames. 

### Left-most Frame

The left-side frame of the experiment shows the resources and submission date and time (as shown in the figure below).

* **Resources** Assigned to that experiment, specifically the assigned pods and their status and container information including the CPU and memory resources assigned.

* The **Submission Date** and time.

![Image](images/UI_Experiment_Details_1.png)

### Right-side Frame
 
The right-side frame of the experiment details windows shows (as shown in the figure below).

* **Start Date:** The day and time this experiment was launched. 
* **End date:** The day and time this experiment was launched. 
*	**Total Duration:** The actual duration this experiment was instantiated.
*	**Parameters:** The experiment script file name and the log directory.
* **Output:** Clickable links to download all logs and view the last 100 log entries. 
 
![Image](images/UI_Experiment_Details_2.png)

### Searching on Experiments

In the **Search** field at the far right of the UI ![](images/search_lense.png), enter a string of alphanumeric characters to match the experiment name or other parameters (such as user), and list only those matching experiments. This Search function lets the user search fields in the entire list, not just the experiment name or parameters. 

### Adding/Deleting Columns

Click **ADD/DELETE COLUMNS** to open a dialogue. Here, the columns currently in use are listed first with 
their check box checked. Scroll down to see more, available columns listed next, unchecked. Click to check and 
uncheck and select the column headings you prefer. Optional column headings include parameters such as Pods, 
End Date, Owner, Template, Time in Queue, and so on.

Column headings also include metrics that have been setup using the Metrics API, for a given experiment, and you 
can select to show those metrics in this display as well.

Column additions and deletions you make are retained between logins.

Refer to [Launching TensorBoard to View Experiments](view_exp_tensorbd.md) for more information.

## Launching Kubernetes Dashboard

Click the **Hamburger Menu** ![](images/hamburger_menu.png) at the far left of the UI to open a left frame. Click **Resources Dashboard** to open the Kubernetes resources dashboard. Refer to [Accessing the Kubernetes Resource Dashboard](accessing_kubernetes.md) for more information.

## Launching TensorBoard

Generally, every file that the training script outputs to `/mnt/output/experiment` (accessed from the perspective of training script launched in Nauta) is accessible from the outside after mounting the output directory with command provided by `nctl mount`.  

Use the following command to launch TensorBoard and to view graphs of this model's results. (Refer to [Working with Datasets](working_with_datasets.md) for more information.) 

When training scripts output Tensorflow summaries to `/mnt/output/experiment`, they can be automatically picked up by TensorBoard instance launched with command:

**Syntax:** nctl launch tensorboard [options] EXPERIMENT-NAME

Execute this command:

`nctl launch tensorboard single`

**Note:** If you are using CLI through remote access, you will need to setup a X server for tunneling over SSH with port forwarding or use SSH Proxy command tunneling. After establishing a tunnel from the gateway to your local machine, you can use the URL provided by nctl.

The following message displays.

```
Please wait for Tensorboard to run... 
Go to http://localhost: 58218
Proxy connection created.
Press Ctrl-C key to close a port forwarding process...

```

The following figure shows the browser display of TensorBoard dashboard with the experiment’s results.

 ![Image](images/tensorboard.png)
 
## Inference

To perform inference testing (using predict batch command in this example) you need to:

1.	Prepare the data for model input.

2.	Acquire a trained model.

3.	Run a prediction instance with trained model on this data.

### Data Preparation

The example `mnist_converter_pb.py` script located in the `examples` folder can be used for data preparation. This script prepares the sample of MNIST test set and converts it to `protobuf` requests acceptable by the served model. This script is run locally and requires `tensorflow`, `numpy`, and `tensorflow_serving` modules. The `mnist_converter_pb.py` script takes two input parameters:

* `--work_dir` which defaults to `/tmp/mnist_test`. It is a path to directory used as `workdir` by this script and `mnist_checker.py`. Downloaded MNIST dataset will be stored there, as well as converted test set sample and labels cached for them.

* `--num_tests` which defaults to 100. It is a number of examples from test set that is converted. The max value is 10000.

Running  the command:

`python examples/mnist_converter_pb.py`

Creates `/tmp/mnist_test/conversion_out folder`, fill it with 100 `protobuf` requests, and cache labels for these requests in `/tmp/mnist_test/labels.npy` file.

### Trained Model

Servable models (as with other training artifacts) can be saved by a training script. As previously mentioned, to access these you have to use the command provided by the `nctl mount` command and mount output storage locally. Example scripts all save servable models in their models subdirectory. To use models like this for inference, you will have to mount input storage too, because models have to be accessible from inside of the cluster. 

For the single experiment example, execute these commands:

```
mkdir -p /mnt/input/single
mkdir /mnt/output
... mount command provided with nctl mount used to mount output storage to /mnt/output
... mount command provided with nctl mount used to mount input storage to /mnt/input
cp /mnt/output/single/models/* -Rf /mnt/input/single/
```
After these steps `/mnt/input/single` should contain:

```
/mnt/input/single/:
00001
/mnt/input/single/00001:
saved_model.pb  variables
/mnt/input/single/00001/variables:
variables.data-00000-of-00001  variables.index
```
### Running Prediction Instance

The following provides a brief example of running inference using the batch command. For more information, refer to [Evaluating Experiments with Inference Testing](inference_testing.md)

Before running the `batch` command, you need to copy `protobuf` requests to input storage, because  they need to be accessed by the prediction instance too. 

Execute these commands:

```
mkdir /mnt/input/data
cp /tmp/mnist_test/conversion_out/* /mnt/input/data

```
Enter the next command to create a prediction instance.

`nctl predict batch -m /mnt/input/home/single -d /mnt/input/home/data --model-name mnist --name single-predict`

The following are the example results of this command: 

```

| Prediction Instance   | Model location        | State     |
|--------------+----------------------+---------+-----------|
| single-predict        | mnt/input/home/single | QUEUED    |

```

Notice the additional **home** directory in path to both model and input data. This is how the path looks from the perspective of the prediction instance. The `mnist_converter_pb.py` creates requests to the MNIST model. `--model-name mnist` is where this MNIST name is given to the prediction instance.

**Note:** Refer to [predict Command](predict.md) for _predict_ command information.

### Prediction Instance Complete

After the prediction instance completes (can be checked using the `predict list` command), you can collect instance responses from output storage. In the example, it contains 100 `protobuf` responses. These can be validated in our case using `mnist_checker.py`. 

Running the following command locally will display the error rate calculated for this model and this sample of the test set:

`python examples/mnist_checker.py --input_dir ~/mnt/output/single-predict`
 
## Viewing Experiment Output Folder

You can use the following steps to mount the output folder and view TensorBoard data files. Mount a folder to your Nauta namespace output directory:

1.	**macOS/Ubuntu:** Mount your `NAUTA` output directory to a local folder. Create a folder for mounting named `my_output_folder`. 

      `mkdir my_output_folder`

2.	To see the correct mount options and command, execute:

       `nctl mount`

3.	Use the mounting command that was displayed to mount Nauta storage to your local machine. The following are examples of mounting the local folder to the Nauta output folder for each OS:

       * **macOS:** `mount_mbfs //'USERNAME:PASSWORD'@CLUSTER-URL/output my_output_folder`
       * **Ubuntu:** `sudo mount.cifs -o username=USERNAME,password=PASSWORD,rw,uid=1000 \ //CLUSTER-URL/output my_output_folder`

4.	Navigate to the mounted location. 
       * **MacOS/Ubuntu only:** Navigate to my_output_folder

5.	See the saved event file by navigating to `mnist-single-node/tensorboard.` Example file: `events.out.tfevents.1542752172.mnist-single-node-master-0`

6.	Unmount Nauta Storage using one of the below commands:
       * **macOS:** `umount output my_output_folder`
       * **Ubuntu:** `sudo umount my_output_folder`
       
To unmount previously mounted Nauta input storage from a local folder/machine refer to [Unmounting Experiment Input to Storage](unmount.md).

For more information on mounting, refer to [Working with Datasets](working_with_datasets.md). To unmount previously mounted Nauta input storage from a local folder/machine refer to [Unmounting Experiment Input to Storage](unmount.md) for more information).

## Removing Experiments

An experiment that has been completed and is no longer needed can be removed from the experiment list using the `cancel` command and its `--purge` option. 

* If `--purge` option _is not_ set in `cancel` command, the experiment will only change status to CANCELLED. 

* If `--purge` option is set in `cancel` command, experiment objects and logs will be irreversibly removed (the experiment’s artifacts will remain in the Nauta storage output folder).

**Note:** For --purge information, refer to [Deleting a User Account](../actions/delete_user.md).

**Syntax:** `nctl experiment cancel [options] EXPERIMENT-NAME`

Enter this command, substituting your experiment name:

 `nctl experiment cancel –-purge <your_experiment>`
 
 ----------------------

## Return to Start of Document

* [README](../README.md)


----------------------




