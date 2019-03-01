# Launching TensorBoard to View Experiments

You can launch TensorBoard* from the Nauta web UI or the CLI; both methods are described.

## Launching TensorBoard from the Web UI

**Note:** To view the experiment’s results in TensorBoard, TensorBoard data _must be_ written to a 
folder in the directory `/mnt/output/experiment.`

To launch TensorBoard from the web UI and view results for individual experiments, perform these steps:

1. Open the web ui. Execute this command:

   `$ nctl launch webui`

2. At the web UI, identify the experiment that you want to see displayed in TensorBoard. Click the check box to the 
left of the experiment name.

3. With an experiment selected (checked), the **LAUNCH TENSORBOARD** button becomes active. Click **LAUNCH TENSORBOARD**. 
TensorBoard is launched with graphs showing the experiment’s results. 

The following screen displays (this is an example only).

![](images/tensorboard.png)

## Launching TensorBoard from the CLI

To launch TensorBoard from the CLI, enter this command:

`$ nctl launch tb <experiment_name>`

The following result displays.

![](images/tensorboard_from_cli.png)

This command will launch a local browser. If the command was run with the --no-launch option, then you need to copy the returned URL into a web browser. TensorBoard is launched with graphs showing the experiment’s results (as shown above).

You can also launch TensorBoard and with the `nctl experiment view` command:

`nctl experiment view -tensorboard <experiment_name>`

This command exposes a TensorBoard instance with data from the named experiment as above.

