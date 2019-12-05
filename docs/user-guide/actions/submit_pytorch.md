# Run an Experiment using Pytorch Framework

This section describes how to submit an experiment using a PyTorch framework.


Nauta provides a separate template with the Pytorch framework, which is named `pytorch`. If you want to run an experiment based on a PyTorch framework, pass the `pytorch` value as the `-t` / `-template` option when executing the `experiment submit` command.

 **Example:** 

```
nctl experiment submit --name pytorch-training --template pytorch /examples/pytorch_mnist.py
```

The previous command runs an experiment using the `pytorch_mnist.py` example delivered together with the `nctl` application. The following result displays showing the queued job.

## Result of this Command 

 ```
Submitting experiments.   
| Name    | Parameters         | Status   | Message   |
|---------+--------------------+----------+-----------|
| pytorch | mnist_multinode.py | QUEUED   |           |

```

 ----------------------

 ## Return to Start of Document

 * [README](../README.md)
----------------------

