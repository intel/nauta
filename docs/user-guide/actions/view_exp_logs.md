# Viewing Experiment Logs and Results Data 

Each experiment generates logs. This is the information generated during the run of the experiment and saved. If an experiment _did not_ print out data during execution, the logs will be blank.

Separate from logs, the results or output of an experiment can be found by mounting the user’s output folder or output-shared folder. A model file should write to the Nauta output folder in order to save any output files. 

Execute the following command to view logs from a given experiment.

**Syntax:** `nctl experiment logs [options] EXPERIMENT-NAME`

**Example:** `nctl experiment logs mnist-tb`

**Result:** The following result, displays an _example log_ (where mnist-tb is shown in the experiment logs, this indicates the name of the experiment).

```
2019-03-20T16:11:38+00:00 mnist-tb-master-0 Step 0, Loss: 2.3015756607055664, Accuracy: 0.078125
2019-03-20T16:11:44+00:00 mnist-tb-master-0 Step 100, Loss: 0.13010963797569275, Accuracy: 0.921875
2019-03-20T16:11:49+00:00 mnist-tb-master-0 Step 200, Loss: 0.07017017900943756, Accuracy: 0.984375
2019-03-20T16:11:55+00:00 mnist-tb-master-0 Step 300, Loss: 0.08880224078893661, Accuracy: 0.984375
2019-03-20T16:12:00+00:00 mnist-tb-master-0 Step 400, Loss: 0.15115690231323242, Accuracy: 0.953125
2019-03-20T16:12:07+00:00 mnist-tb-master-0 Validation accuracy: 0.980400025844574
```
 
**Note:** Logs generated with sub-millisecond frequency may appear out of order when displayed. This is casued by the 1ms resolution of the underlying logging solution. 

----------------------
 
## Return to Start of Document

* [README](../README.md)
 
----------------------

