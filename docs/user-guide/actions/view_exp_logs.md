# Viewing Experiment Logs and Results Data 

Each experiment generates logs. This is the information generated during the run of the experiment and saved. If an experiment _did not_ print out data during execution, the logs will be blank.

Separate from logs, the results or output of an experiment can be found by mounting the user’s output folder or output-shared folder. A model file should write to the Nauta output folder in order to save any output files. 

Use the following command to view logs from a given experiment.

**Syntax:** `nctl experiment logs [OPTIONS] EXPERIMENT_NAME`

Here is an example:

`nctl experiment logs multiexp-1`

The following result, displays an example log. 
 ![Image](images/experiment_log.png)
 
 
**Note:** Logs generated with sub-millisecond frequency may appear out of order when displayed. This is casued by the 1ms resolution of the underlying logging solution.
 
 
 
 
