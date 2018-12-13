# Viewing Experiment Logs and Results Data 

Each experiment generates logs. This is the information generated during the run of the experiment and saved. If an experiment did not print out data during execution, the logs will be blank.

Separate from logs, the results or output of an experiment can be found by mounting the user’s output folder or output-shared folder.  A model file should write to the DLS4E output folder in order to save any output files. 

Use the following command to view logs from a given experiment.

**Syntax:** `dlsctl experiment logs [OPTIONS] EXPERIMENT_NAME`

**Execute:** `dlsctl experiment logs multiexp-1`

The following result, displays an example log. 
 ![Image](images/experiment_log.png)

 
