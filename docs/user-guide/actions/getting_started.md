# Getting Started

This section provides brief examples for performing some of the most essential and valuable tasks supported by Nauta. 

**Note:** Several commands and training scripts in this section require access to the internet to download data, scripts, and so on.

The section discusses the following main topics:

 - [Verifying Installation](#verifying-installation)
 - [Overview of nctl Commands](#overview-of-nctl-commands)
 - [Submitting an Experiment](#submitting-an-experiment)
 - [Adding Experiment Metrics](#adding-experiment-metrics)
 - [Viewing Experiment Results from the Web UI](#viewing-experiment-results-from-the-web-ui)
 - [Launching Kubernetes Dashboard](#launching-kubernetes-dashboard)
 - [Launching TensorBoard](#launching-tensorboard)
 - [Inference](#inference)
 - [Viewing Experiment Output Folder](#viewing-experiment-output-folder)
 - [Removing Experiments](#removing-experiments)

## Verifying Installation

Check that the required software packages are available in the terminal by PATH and verify that the correct version is used.

### Proxy Environment Variables 

If you are behind a proxy, remember to set your:

* `HTTP_PROXY`, `HTTPS_PROXY` and `NO_PROXY` environment variables

* `http_proxy`, `https_proxy` and `no_proxy` environment variables

### Confirm Installation

Execute the following command to verify your installation has completed: 

`nctl verify`

### Confirmation Message

If any installation issues are found, the command returns information about the cause: which application should be installed and in which version. This command also checks if the CLI can connect to Nauta; and, if port forwarding to Nauta is working correctly. If no issues are found, a message indicates that the checks were successful. The following examples are the results of this command:
 
```
This OS is supported.
kubectl verified successfully.
helm client verified successfully.
git verified successfully.
helm server verified successfully.
kubectl server verified successfully.
packs resources' correctness verified successfully.
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

#### Help Command Output

The results are shown below.

```
Usage: nctl COMMAND [options] [args]...

    Nauta Client

  Displays additional help information when the -h or --help COMMAND is
  used.

Options:
  -h, --help  Displays help messaging information.

Commands:
  config, cfg      Set limits and requested resources in templates.
  experiment, exp  Start, stop, or manage training jobs.
  launch, l        Launch the web user-interface or TensorBoard. Runs as a
                   process in the system console until the user stops the
                   process. To run in the background, add '&' at the end of
                   the line.
  model, mo        Manage the processing, conversion, and packaging of models.
  mount, m         Displays a command that can be used to mount a client's
                   folder on their local machine.
  predict, p       Start, stop, and manage prediction jobs and instances.
  template, tmp    Manage experiment templates used by the system.
  user, u          Create, delete, or list users of the platform. Can only be
                   run by a platform administrator.
  verify, ver      Verifies if all required external components contain the
                   proper installed versions.
  version, v       Displays the version of the installed nctl application.

```

## Example Experiments

The Nauta installation includes sample training scripts and utility scripts, contained in the `examples` folder, that can be run to demonstrate how to use Nauta. This section describes how to use these scripts. 

### Examples Folder Content

The examples folder in the nctl installation contains these following experiment scripts:

* `mnist_checker.py` - This a utility script used for the inference process and model verification.
* `mnist_converter_pb.py` - This a utility script used for the inference process and model verification.
* `mnist_horovod.py` - Training of digit classifier in Horovod.
* `mnist_input_data.py` - Functions for downloading and reading mnist data.
* `mnist_single_node.py` - Training of digit classifier in single node setting  (requires `mnist_inut_data.py` file).
* `mnist_multinode.py` - Training of digit classifier in distributed TensorFlow setting.
* `mnist_saved_model.py` - Training of digit classifier with saving the model at the end (requires `mnist_tensorboard.py` file).

Additional example scripts for various neural networks  are included and have been validated on the Nauta platform.

### Utility Scripts

The following are the utility scripts used for the inference process and model verification:

* `mnist_converter_pb.py` 

* `mnist_checker.py`

**Note:** Experiment scripts _must be_ written in Python.  

## Submitting an Experiment

Launch the training experiments with Nauta using the following:

**Syntax**:

`nctl experiment submit [options] SCRIPT-LOCATION [-- script-parameters]`

**Where:** The path and name of the Python script used to perform this experiment.

`-- SCRIPT-LOCATION` 

### Example Experiments

To submit the example experiments, use the following:

#### Single Node Training

For single node training (template parameter in this case is optional), use the following: 

`nctl experiment submit --template  tf-training-single examples/mnist_single_node.py --name single`

#### Multinode Training

For multinode training, use the following:

`nctl experiment submit --template tf-training-multi examples/mnist_multinode.py --name multinode`

#### Horovod Training

For Horovod training, use the following:

`nctl experiment submit --template tf-training-horovod examples/mnist_horovod.py --name horovod`

The included example scripts _do not_ require an external data source. The scripts automatically download the MNIST dataset. Templates referenced here have set CPU and Memory requirements. The list of available templates can be obtained by issuing `nctl experiment template-list` command.

**Note:** To run TensorBoard, TensorBoard data _must be_ written to a folder in the directory `/mnt/output/experiment`. This example script satisfies this requirement; however, your scripts _must_ meet the same requirement.

The following example shows how to submit a MNIST experiment and write the TensorBoard data to a folder in your Nauta output folder. 

Enter the following command to run this example:

`nctl experiment submit --template tf-training-single examples/mnist_single_node.py --name single`

#### Result of this Command

The execution of the submit command may take a few minutes the first time. When the experiment submission is completed, the following result is displayed:

```

Submitting experiments.
| Experiment   | Parameters           | State   | Message   |
|--------------+----------------------+---------+-----------|
| single       | mnist_single_node.py | QUEUED  |           |

```

#### Running an Experiment using PyTorch Framework

Nauta provides a separate template with the PyTorch framework, which is named `pytorch-training`. If you want to run an experiment based on a PyTorch framework, pass the `pytorch-training` value as the `-t / --template` option when executing the `experiment submit` command.

 **Example:** 

```
nctl experiment submit --name pytorch --template pytorch-training examples/pytorch_mnist.py
```

#### Result of this Command

The previous command runs an experiment using the `pytorch_mnist.py` example delivered together with the `nctl` application. The following result displays showing the queued job.

 ```
Submitting experiments.   
| Name    | Parameters         | Status   | Message   |
|---------+--------------------+----------+-----------|
| pytorch | pytorch_mnist.py   | QUEUED   |           |
```

#### Viewing Experiment Status

Use the following command to view the status of all your experiments:

**Syntax**: `nctl experiment list [options]`

Execute this command: 

`nctl experiment list --brief`

As shown below, an experiment's status displays. This is an example only. The `--brief` option returns a short version of results as shown. 

```
| Name                             | Submission date        | Owner   | Status    |
|----------------------------------+------------------------+---------+-----------|
| mnist-sing-209-19-08-26-18-03-43 | 2019-08-26 06:05:05 PM | user1   | CANCELLED |
| multinode                        | 2019-08-26 06:06:32 PM | user1   | QUEUED    |
| multinodes                       | 2019-09-19 01:38:33 AM | user1   | QUEUED    |
| para-range-1                     | 2019-09-19 01:25:21 AM | user1   | QUEUED    |
| para-range-2                     | 2019-09-19 01:25:23 AM | user1   | QUEUED    |
| para-range-3                     | 2019-09-19 01:25:23 AM | user1   | QUEUED    |
| pytorch                          | 2019-08-26 06:58:01 PM | user1   | QUEUED    |
| single                           | 2019-08-26 06:05:32 PM | user1   | QUEUED    |
| single2                          | 2019-09-20 05:31:06 PM | user1   | COMPLETE  |

```
### Monitoring Training

There are four ways to monitor training in Nauta, all which are discussed in the following sections. 
 
 - [Viewing Experiment Logs](#viewing-experiment-logs)
 - [Adding Experiment Metrics](#adding-experiment-metrics)  
 - [Viewing Experiment Results from the Web UI](#viewing-experiment-results-from-the-web-ui)
 - [Launching TensorBoard](#launching-tensorboard)

### Viewing Experiment Logs 

To view the experiment logs, execute the following command.

**Syntax:** `nctl experiment logs [options] EXPERIMENT-NAME`

Execute this command:

`nctl experiment logs single`

As shown below, a log displays the example results.

```
2019-03-20T16:11:38+00:00 single-master-0 Step 0, Loss: 2.3015756607055664, Accuracy: 0.078125
2019-03-20T16:11:44+00:00 single-master-0 Step 100, Loss: 0.13010963797569275, Accuracy: 0.921875
2019-03-20T16:11:49+00:00 single-master-0 Step 200, Loss: 0.07017017900943756, Accuracy: 0.984375
2019-03-20T16:11:55+00:00 single-master-0 Step 300, Loss: 0.08880224078893661, Accuracy: 0.984375
2019-03-20T16:12:00+00:00 single-master-0 Step 400, Loss: 0.15115690231323242, Accuracy: 0.953125
2019-03-20T16:12:07+00:00 single-master-0 Validation accuracy: 0.980400025844574
```

## Adding Experiment Metrics

Experiments launched in Nauta can output additional kinds of metrics using the _publish function_ from the experiment metrics API. Execute the following command to see an example of metrics published with the single experiment executed in the above example, and execute the following command:

`nctl experiment list`

As shown, an example experiment list is shown (scroll right to see the full contents). 

```

| Name                             | Parameters                     | Metrics                     | Submission date        | Start date             | Duration    | Owner   | Status    | Template name               | Template version   |
|----------------------------------+--------------------------------+-----------------------------+------------------------+------------------------+-------------+---------+-----------+-----------------------------+--------------------|
| generate-model                   | mnist_saved_model.py           |                             | 2019-09-30 09:23:28 PM |                        |             | user1   | QUEUED    | tf-training-tfjob           | 0.1.0              |
|                                  | /mnt/output/experiment         |                             |                        |                        |             |         |           |                             |                    |
| mnist-sing-209-19-08-26-18-03-43 | mnist_single_node.py           |                             | 2019-08-26 06:05:05 PM |                        |             | user1   | CANCELLED | tf-training-tfjob           | 0.1.0              |
| multinode                        | mnist_multinode.py             |                             | 2019-08-26 06:06:32 PM |                        |             | user1   | QUEUED    | multinode-tf-training-tfjob | 0.1.0              |
| multinodes                       | mnist_multinode.py -- data_dir |                             | 2019-09-19 01:38:33 AM |                        |             | user1   | QUEUED    | multinode-tf-training-tfjob | 0.1.0              |
|                                  | =/mnt/input/root/public/MNIST  |                             |                        |                        |             |         |           |                             |                    |
| para-range-1                     | mnist_single_node.py lr=0.1 -- |                             | 2019-09-19 01:25:21 AM |                        |             | user1   | QUEUED    | tf-training-tfjob           | 0.1.0              |
|                                  | data_dir=/mnt/input/root/publi |                             |                        |                        |             |         |           |                             |                    |
|                                  | c/MNIST                        |                             |                        |                        |             |         |           |                             |                    |
| para-range-2                     | mnist_single_node.py lr=0.2 -- |                             | 2019-09-19 01:25:23 AM |                        |             | user1   | QUEUED    | tf-training-tfjob           | 0.1.0              |
|                                  | data_dir=/mnt/input/root/publi |                             |                        |                        |             |         |           |                             |                    |
|                                  | c/MNIST                        |                             |                        |                        |             |         |           |                             |                    |
| para-range-3                     | mnist_single_node.py lr=0.3 -- |                             | 2019-09-19 01:25:23 AM |                        |             | user1   | QUEUED    | tf-training-tfjob           | 0.1.0              |
|                                  | data_dir=/mnt/input/root/publi |                             |                        |                        |             |         |           |                             |                    |
|                                  | c/MNIST                        |                             |                        |                        |             |         |           |                             |                    |
| pytorch                          | mnist_multinode.py             |                             | 2019-08-26 06:58:01 PM |                        |             | user1   | QUEUED    | multinode-tf-training-tfjob | 0.1.0              |
| pytorch2                         | pytorch_mnist.py               |                             | 2019-09-30 11:15:12 PM |                        |             | user1   | QUEUED    | pytorch                     | 0.0.1              |
| single                           | mnist_single_node.py           |                             | 2019-08-26 06:05:32 PM |                        |             | user1   | QUEUED    | tf-training-tfjob           | 0.1.0              |
| single2                          | mnist_single_node.py           | accuracy: 0.96875           | 2019-09-20 05:31:06 PM | 2019-09-20 05:31:14 PM | 0d 0h 1m 6s | user1   | COMPLETE  | tf-training-tfjob           | 0.1.0              |
|                                  |                                | global_step: 499            |                        |                        |             |         |           |                             |                    |
|                                  |                                | loss: 0.058229897           |                        |                        |             |         |           |                             |                    |
|                                  |                                | validation_accuracy: 0.9832 |                        |                        |             |         |           |                             |                    |

```

### Adding Experiment Metrics: Instructions

To add metrics to an experiment, you need to edit the experiment script to use the `experiment_metrics.api` and then publish the metric that you wish to display. Complete the following steps in the script to publish a metric: 

1. Add the metrics library API with the following entry in your experiment script:

   `from experiment_metrics.api import publish`

2.	To add a metric, publish `dict key` and the string value.  Using the validation accuracy metric as an example, the metric is published in the `mnist_single_node.py` example.

    `publish({"validation_accuracy": str(validation_accuracy_val)})`
  
3.	Save the changes.

4.	Submit the experiment again, but with a different name. 
      
5.	The published metrics can now be viewed. 

    `nctl experiment list`

### Saving Metrics for Multinode Experiments

Storing at the same time two (or more) metrics with the same key from two different nodes may lead to errors (such as losing  some logs) due to conflicting names. To avoid this, adding metrics for multinode experiments should be done using one of the two following methods: _[Method 1](#method-1)_ or _[Method 2](#method-2)_.

### Method 1  

The key of a certain metric should also contain a node identifier from which this metric derives. To create an identifier, use one of the following:

   * For horovod multinode training jobs, result of the `rank()` function provided by the `horovod` package can be used
    as a node's identifier.  
    
   * For `tfjob` multinode training jobs, you can take all necessary info from the `TF_CONFIG` environment variable. An example piece of a code creating such identifier, is:
    
 ### Node Identifier Example

    ```
    
    tf_config = os.environ.get('TF_CONFIG')
    if not tf_config:
        raise RuntimeError('TF_CONFIG not set!')

    tf_config_json = json.loads(tf_config)

    job_name = tf_config_json.get('task', {}).get('type')
    task_index = tf_config_json.get('task', {}).get('index')
    # final node identifier `node_id = '-'.join(job_name,task_index)
    
    ```

### Method 2

Only one node should store metrics. Use the following to decide which node should store metrics:  

* For `horovod` multinode training jobs, the horovod python library provides the `rank()` function that returns a number
of a current worker. _Master_ is marked with the number `0`, so only a pod with this number should store logs.

* For `tfjob` multinode training jobs, as there is _no_ dedicated master node. Therefore, a user should choose which worker should be responsible for storing metrics. The identifier of a current worker can be obtained, as described in _[Method 1](#method-1)_. Furthermore, a user should choose an identifier and store the logs, but only from a node that has this chosen ID. 
   
## Viewing Experiment Results from the Web UI

The web UI lets you explore the experiments you have submitted. To view your experiments at the web UI, execute the following command at the command prompt:

`nctl launch webui`

The following screen displays (this is an example only).

![](images/web_ui.png) 

**Note:** If you are using CLI through remote access, you will need to setup a X server for tunneling over SSH with port forwarding or use SSH Proxy command tunneling. After establishing a tunnel from the gateway to your local machine, you can use the URL provided by `nctl` command.

### Web UI Columns 

* **Name:** The left-most column lists the experiments by name.
* **Status:** This column reveals experiment’s current status, one of: `QUEUED, RUNNING, COMPLETE, CANCELLED, FAILED, CREATING`.
* **Submission Date:** This column gives the submission date in the format: MM/DD/YYYY, hour:min:second AM/PM.
* **Start Date:** This column shows the experiment start date in the format: MM/DD/YYYY, hour:min:second AM/PM.
* **Duration:** This column shows the duration of execution for this experiment in days, hours, minutes and seconds.
* **Type:** Experiment Type can be Training, Jupyter, or Inference. Training indicates that the experiment was launched from the CLI. Jupyter indicates that the experiment was launched using Jupyter Notebook. 

**Note:** You can perform the tasks discussed below at the Nauta web UI.

### Expand Experiment Details

Click the _listed experiment name_ to see additional details for that experiment. The following details are examples only. 
This screen is divided into left and right-side frames. 

### Left-side Frame

The left-side frame of the experiment details window shows Resources and Submission Date (as shown in the figure below).

* **Resources** assigned to that experiment, specifically the assigned pods and their status and container information including the CPU and memory resources assigned.

* Displays the **Submission Date** and time.

![Image](images/UI_Experiment_Details_1.png)
 
### Right-side Frame
 
The right-side frame of the experiment details window shows Start Date, End Date, Total Duration, Parameters, and Output (as shown in the figure below).

* **Start Date:** The day and time this experiment was launched. 
* **End date:** The day and time this experiment was launched. 
*	**Total Duration:** The actual duration this experiment was instantiated.
*	**Parameters:** The experiment script file name and the log directory.
* **Output:** Clickable links to download all logs and view the last 100 log entries. 
 
![Image](images/UI_Experiment_Details_2.png)

### Searching on Experiments

In the **Search** field at the far right of the UI ![](images/search_lense.png), enter a string of alphanumeric characters to match the experiment name or other parameters (such as user), and list only those matching experiments. This Search function lets the user search fields in the entire list, _not_ just the experiment name or parameters. 

## Adding and Deleting Columns

### ADD/DELETE COLUMNS Button

Click **ADD/DELETE COLUMNS** to open a dialogue. Here, the columns currently in use are listed first with 
their check box checked. Scroll down to see more, available columns listed next, unchecked. 

### Check/Uncheck Column Headings

Click to check and uncheck and select the column headings you prefer. Optional column headings include parameters, such as Pods, End Date, Owner, Template, Time in Queue, and so on.

### Column Heading Metrics

Column headings also include metrics that have been setup using the Metrics API, for a given experiment, and you 
can select to show those metrics in this display as well.

### Column Additions and Deletions

Column additions and deletions you make are retained between logins. 

## Launching Kubernetes Dashboard

1. Click the **Hamburger Menu** ![](images/hamburger_menu.png) at the far left of the UI to open a left frame. 
2. Click **Resources Dashboard** to open the Kubernetes resources dashboard. 

   **Note:** Refer to [Accessing the Kubernetes Resource Dashboard](accessing_kubernetes.md).

## Launching TensorBoard

Generally, every file that the training script outputs to `/mnt/output/experiment` (accessed from the perspective of training script launched in Nauta) is accessible from the outside after mounting the output directory with command provided by `nctl mount`. 

Use the following command to launch TensorBoard and to view graphs of this model's results. Refer to [Working with Datasets](working_with_datasets.md) for more information.

When training scripts output TensorFlow summaries to `/mnt/output/experiment`, they can be automatically picked up by the Tensorboard instance launched with this command:

**Syntax:** 

`nctl launch tensorboard [options] EXPERIMENT-NAME`

Execute the following command:

`nctl launch tensorboard single`

**Note:** If you are using CLI through remote access, you will need to setup an X server for tunneling over SSH with port forwarding or use SSH Proxy command tunneling. After establishing a tunnel from the gateway to your local machine, use the URL provided by nctl.

The following message displays the example port number.

```
Please wait for Tensorboard to run... 
Go to http://localhost: 58218
Proxy connection created.
Press Ctrl-C key to close a port forwarding process...
```
 
The following figure shows the browser display of TensorBoard dashboard with the experiment’s results.

 ![Image](images/tensorboard.png)
 
## Inference

To perform inference testing (using predict batch command in this example), you need to:

1.	Prepare the data for model input.

2.	Acquire a trained model.

3.	Run a prediction instance with trained model on this data.

### Data Preparation

The example `mnist_converter_pb.py` script, located in the `examples` folder, can be used for data preparation. This script prepares the sample of the MNIST test set and converts it to `protobuf` requests acceptable by the served model. This script is run locally and requires `tensorflow`, `numpy`, and `tensorflow_serving` modules. The `mnist_converter_pb.py` script takes two input parameters:

* `--work_dir` which defaults to `/tmp/mnist_test`. It is a path to directory used as `workdir` by this script and `mnist_checker.py`. The downloaded MNIST dataset is stored there, as well as the converted test set sample and labels cached for them.

* `--num_tests` which defaults to 100. It is a number of examples from test set which will be converted. The maximum value is 10000.

Execute the following command:

`python examples/mnist_converter_pb.py`

Creates the `/tmp/mnist_test/conversion_out` folder. Fill it with 100 `protobuf` requests, and cache labels for these requests in the `/tmp/mnist_test/labels.npy` file.

### Trained Model

Servable models (as with other training artifacts) can be saved by a training script. As previously mentioned, to access these you have to use the command provided by the `nctl mount` command and mount output storage locally. All the example scripts save servable models servable models in their model's subdirectory. To use models like this for inference mount the `input` storage too, because models have to be accessible from inside of the cluster. 

For the single experiment example, execute these commands:

```
mkdir -p /mnt/input/single
mkdir /mnt/output
... mount command provided with nctl mount used to mount output storage to /mnt/output
... mount command provided with nctl mount used to mount input storage to /mnt/input
cp /mnt/output/single/models/* -Rf /mnt/input/single/
```
After these steps the `/mnt/input/single` should contain:

```
/mnt/input/single/:
00001
/mnt/input/single/00001:
saved_model.pb  variables
/mnt/input/single/00001/variables:
variables.data-00000-of-00001  variables.index
```
### Running a Prediction Instance

The following provides a brief example of running inference using the batch command. For more information, refer to [Evaluating Experiments with Inference Testing](inference_testing.md).

Before running the `batch` command, copy `protobuf` requests to input storage, because  they need to be accessed by the prediction instance too. 

Execute these commands:

```
mkdir /mnt/input/data
cp /tmp/mnist_test/conversion_out/* /mnt/input/data
```
To create a prediction instance, execute these commands.

```
nctl predict batch -m /mnt/input/home/single -d /mnt/input/home/data --model-name mnist --name single-predict
```

The following are the example results of this command: 

```

| Prediction Instance   | Model location        | State     |
|--------------+----------------------+---------+-----------|
| single-predict        | mnt/input/home/single | QUEUED    |

```

Notice the additional **home** directory in path to both model and input data. This is how the path looks from the perspective of the prediction instance. The `mnist_converter_pb.py` creates requests to the MNIST model. The `--model-name mnist` is where this MNIST name is given to the prediction instance.

**Note:** Refer to [predict Command](predict.md) for _predict_ command information.

### Prediction Instance Complete

After the prediction instance completes (can be checked using the `predict list` command), collect instance responses from output storage. 

In the example, it contains 100 `protobuf` responses. These can be validated using `mnist_checker.py`. 

Running the following command locally will display the error rate calculated for this model and this sample of the test set.<br>

`python examples/mnist_checker.py --input_dir /mnt/output/single-predict`

## Viewing Experiment Output Folder

Use the following steps to mount the output folder and view TensorBoard data files. Mount a folder to your Nauta namespace output directory:

1.	**macOS/Ubuntu:** Mount your `Nauta` output directory to a local folder. Create a folder for mounting: `my_output_folder`. 

      `mkdir my_output_folder`

2.	To see the correct mount options and command, execute:

       `nctl mount`

3.	Use the mounting command that was displayed to mount Nauta storage to your local machine. The following are examples of mounting the local folder to the Nauta output folder for each OS:
       * **macOS:** `mount_mbfs //'USERNAME:PASSWORD'@CLUSTER-URL/output my_output_folder`
       * **Ubuntu:** `sudo mount.cifs -o username=USERNAME,password=PASSWORD,rw,uid=1000 \ //CLUSTER-URL/output my_output_folder`

4.	Navigate to the mounted location. 
       * **macOS/Ubuntu only:** Navigate to the `my_output_folder`.

5.	See the saved event file by navigating to `mnist-single-node/tensorboard.` 

   Example file: `events.out.tfevents.1542752172.mnist-single-node-master-0`

6.	Unmount Nauta Storage using one of the below commands:
       * **macOS:** `umount output my_output_folder`
       * **Ubuntu:** `sudo umount my_output_folder`
        
For more information on mounting, refer to [Working with Datasets](working_with_datasets.md). 

## Removing Experiments

An experiment that has been completed and is no longer needed can be removed from the experiment list using the `cancel`  command and its `--purge` option. 

* If the `--purge` option _is not_ set in the `cancel` command, the experiment will only change status to `CANCELLED`. 

* If the `--purge` option is set in the `cancel` command, experiment objects and logs will be irreversibly removed (the experiment’s artifacts will remain in the Nauta storage output folder).

**Syntax:** `nctl experiment cancel [options] EXPERIMENT-NAME`

Execute this command, substituting your experiment name:

 `nctl experiment cancel –-purge <your_experiment>`

**Note:** For --purge information, refer to [Deleting a User Account](../actions/delete_user.md).
 
 ----------------------

## Return to Start of Document

* [README](../README.md)


----------------------




