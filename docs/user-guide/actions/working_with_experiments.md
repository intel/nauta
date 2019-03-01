# Working with Experiments

This section provides greater details on:

* [Mounting Experiment Input to Storage](mount_exp_input.md)
* [Launching Jupyter Interactive Notebook](launch_jupyter.md)
* [Submitting a Single Experiment](submit_single_exp.md)
* [Submitting Multiple Experiments](submit_mult_exp.md)
* [Run an Experiment on Multiple Nodes](submit_mult_nodes.md)
* [Working with Template Packs](template_packs.md)
* [Mounting Storage to View Experiment Output](mount_exp_output.md)
* [Cancelling Experiments](cancel_exp.md)

**Note:** Files located in the input storage are accessible through Jupyter Notebooks. Only files that are 
written to: `output/home/` are persistently stored. Therefore, changes made during a session to other files (including model scripts) _will not_ be saved when the session is closed. Therefore, it is recommended that you save session data to the 
output/[experiment] folder for future use.
