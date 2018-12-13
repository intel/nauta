# Working with Experiments

This section provides greater detail about:

* [Mounting Experiment Input to Storage](mount_exp_input.md)
* [Launching Jupyter Interactive Notebook](launch_jupyter.md)
* [Submitting a Single Experiment](submit_single.md)
* [Submitting Multiple Experiments](submit_mult_exp.md)
* [Run an Experiment on Multiple Notes](submit_mult_nodes.md)
* [Working with Template Packs](template_packs.md)
* [Mounting Storage to View Experiment Output](mount_exp_output.md)
* [Cancelling Experiments](cancel_exp.md)

**Note:** Files located in the input storage are accessible through Jupyter Notebooks. Only files that are 
written to /output/home/ are persistently stored. Therefore, changes made to other files, including model scripts, 
during the session will not be saved after the session is closed. It is recommended to save session data to the 
output/[experiment] folder for future use.
