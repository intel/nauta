# Product Overview

Nauta software provides a multi-user, distributed computing environment for running deep learning model training experiments.
Results of experiments, can be viewed and monitored using a command line interface, web UI and/or TensorBoard. 

You can use existing data sets, use your own data, or downloaded data from online sources, and create public or private folders to make collaboration amongst teams easier. Nauta runs using the industry leading Kubernetes and Docker platform
for scalability and ease of management. 

Templates are available (and customizable) on the platform to take the complexities out of creating and running single and multi-node deep learning training experiments without all the systems overhead and scripting needed with standard container environments. To test your model, Nauta also supports both batch and streaming inference, all in a single platform.

The Nauta client software has been validated on the following operating systems and versions:
* Ubuntu* (16.04, 18.04)
* RedHat* 7.5
* macOS* High Sierra (10.13)
* Windows* 10

# Nauta User Guide

This guide describes how to use Nauta, and the following topics:

* [Basic Concepts](actions/concepts.md)
* [Client Installation and Configuration](actions/install_configure.md)
* [Getting Started](actions/getting_started.md)
* [Working with Datasets](actions/working_with_datasets.md)
* [Working with Experiments](actions/working_with_experiments.md)
* [Working with Template Packs](actions/template_packs.md)
* [Evaluating Experiments](actions/view_exp.md)
* [Evaluating Experiments with Inference Testing](actions/inference_testing.md)
* [Managing Users and Resources](actions/managing_users_resources.md)
* [Building Nauta CTL (nctl)](actions/nctl.md)
* [CLI Commands](actions/view_cli_help.md)
    * [config](actions/config.md) - adjusts packs' configuration to resources available on a cluster
    * [experiment](actions/experiment.md) - training and managing training jobs 
    * [launch](actions/launch.md) - launching browser for Web UI and Tensorboard
    * [mount](actions/mount.md) - displaying details concerning how to mount user's folders
    * [template](actions/template.md)
    * [predict](actions/predict.md) - deploy and manage inference on trained model
    * [user](actions/user.md) - adding/deleting/listing users of the system 
    * [verify](actions/verify.md) - verifies installation of _dlsctl_ application
    * [version](actions/version.md) - displays version of _dlsctl_ application

## Advanced Sections

* [Installing Additional Libraries and Dependencies](advanced/customlibs.md)
* [Controlling Packs Parameters](advanced/packs.md)

# Terms and Conditions

This document is subject to [CC-BY-ND 4.0.](https://creativecommons.org/licenses/by-nd/4.0/) 

Copyright © 2019 Intel Corporation. All rights reserved.

Intel and the Intel logo are trademarks of Intel Corporation in the U.S. and other countries.

'*'    Other names and brands may be claimed as the property of others.
This document contains information on products and/or processes in development.
