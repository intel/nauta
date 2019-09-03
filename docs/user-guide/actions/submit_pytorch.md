# Run an Experiment using Pytorch Framework

 This section describes how to submit an experiment using a Pytorch framework.

Nauta provides a separate template with the Pytorch framework, which is named `pytorch`. If you want to run an experiment based on a Pytorch framework, pass the `pytorch` value as the `-t` option when executing the `experiment submit` command.

 **Example:** 

```
nctl experiment submit --name pytorch --template pytorch /examples/pytorch_mnist.py
```

The previous command runs an experiment using the `pytorch_mnist.py` example delivered together with the `nctl` application. The following result displays showing the queued job.

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
