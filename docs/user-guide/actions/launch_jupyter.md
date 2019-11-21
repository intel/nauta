# Launching Jupyter Interactive Notebook

You can use Jupyter Notebook to run and display the results of your experiments. This section discusses the following main topics:

 - [Launching Jupyter Interactive Notebook](#launching-jupyter-interactive-notebook)
 - [Storage and Session Data](#storage-and-session-data)  
 - [Tunneling](#tunneling)
 - [Canceling a Jupyter Notebook](#canceling-a-jupyter-notebook)

## Launching Jupyter Interactive Notebook

This release of Nauta supports Python 3 and 2.7 for scripts. 

**Syntax:** `nctl experiment interact [options]`

Options, include:

* `name` - The name of this Jupyter Notebook session. 

* `filename` - File with a notebook that should be opened in Jupyter notebook.

For detailed command syntax information, refer to: [experiment interact Subcommand](experiment.md#interact-subcommand). 

Execute this command to launch Jupyter:

`nctl experiment interact`

## Storage and Session Data

Files located in the input storage are accessible through Jupyter Notebooks. Only files that are written to `/output/home/` are persistently stored. Therefore, changes made to other files, including model scripts, during the session _will not_ be saved after the session is closed. Therefore, it is recommended that you save session data to the `output/experiment` folder for future use.

**Note:** Files that are accessible through the Jupyter Notebook are the same folders accessible to the user for experiments.

## Tunneling

If you are using CLI through remote access, you will need to setup a X server for tunneling over SSH with port forwarding or use SSH Proxy command tunneling. After establishing a tunnel from the gateway to your local machine, you can use the URL provided by nctl.

The following result displays.

```
Submitting experiments.
| Experiment                  | Parameters | State  | Message   |
|-----------------------------+------------+--------+-----------|
| jup-936-18-09-17-20-14-58   |            | QUEUED |           | 

Browser will start in a few seconds. Please wait...
Go to http://locahost:28113
Proxy connection created.
Press Ctrl-C key to close a port forwarding process...
```
 
Jupyter Notebook will launch in your default web browser. The following displays. 

 ![](images/jupyter_dashbd.png)


An example active Jupyter Notebook, shows a simple experiment plot.
 
 ![](images/jupyter_plot.png)
 
## Canceling a Jupyter Notebook

In Nauta, running a Jupyter notebook is done through an interact session. The session will remain open such that the Jupyter notebook that is running will continue when the browser is closed. Therefore, a user _must_ manually cancel the interact session, or it will continue to allocate resources.
 
### Steps to Manage and Cancel Interacts

1. To see all running jobs, execute: `nctl experiment list --status RUNNING`

2. To cancel a running interact, execute: `nctl experiment cancel [options] [EXPERIMENT-NAME]`

   * EXPERIMENT-NAME is the interact name.
   
   * Use the `--purge` option if you need to remove session from experiment list. For _purge_ information, refer to: [Getting Started, Remove Experiment Section](../actions/getting_started.md).  
   
To verify that cancellation has completed, execute: `nctl experiment list --status RUNNING` 

----------------------

## Return to Start of Document

* [README](../README.md)

----------------------
