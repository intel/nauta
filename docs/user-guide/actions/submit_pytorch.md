# Run an Experiment using Pytorch Framework

 This section describes how to submit an experiment using Pytorch framework.

 Nauta provides a separate template with Pytorch framework, which is named `pytorch-training`. If you want to run experiment based on Pytorch framework, pass `pytorch-training` (or `pytorch-training-py2` for python 2) value as the `-t` option when executing `experiment submit` command.

 **Example:** 

 ```
nctl experiment submit --name pytorch-training --template pytorch /examples/pytorch_mnist.py
```

 The command above runs an experiment using the `pytorch_mnist.py` example delivered together with `nctl` application. The following result displays showing the queued job.

 ```
Submitting experiments.   
| Name         | Parameters             | Status  | Message |
|--------------+------------------------+---------+---------|
| multinodes   |                        | QUEUED  |         |
```

 ----------------------

 ## Return to Start of Document

 * [README](../README.md)
----------------------
