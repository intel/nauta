# Product Overview

Nauta software provides a multi-user, distributed computing environment for running deep learning model training experiments. Results of experiments, can be viewed and monitored using a command line interface, web UI and/or TensorBoard. 

You can use existing data sets, use your own data, or downloaded data from online sources, and create public or private folders to make collaboration amongst teams easier. Nauta runs using the industry leading Kubernetes and Docker platform
for scalability and ease of management. 

Templates are available (and customizable) on the platform to take the complexities out of creating and running single and multi-node deep learning training experiments without all the systems overhead and scripting needed with standard container environments. To test your model, Nauta also supports both batch and streaming inference, all in a single platform.

The Nauta client software has been validated on the following operating systems and versions:

* Ubuntu (16.04, 18.04)
* Red Hat 7.6
* macOS High Sierra (10.13)

# Nauta User Guide Purpose

This guide describes how to use Nauta, and discusses the following topics:

* [Naua Basic Concepts](actions/concepts.md)
* [Client Installation and Configuration](actions/install_configure.md)
* [Getting Started](actions/getting_started.md)
* [Working with Datasets](actions/working_with_datasets.md)
* [Working with Experiments](actions/working_with_experiments.md)
* [Working with Template Packs](actions/template_packs.md)
* [Evaluating Experiments](actions/view_exp.md)
* [Exporting Models](actions/model_export.md)
* [Evaluating Experiments with Inference Testing](actions/inference_testing.md)
* [OpenVINO Model Server Overview](actions/openvino_inf.md)
* [Managing Users and Resources](actions/managing_users_resources.md)
* [Kubernetes Resource Dashboard Overview](actions/accessing_kubernetes.md)
* [CLI Commands](actions/view_cli_help.md)
    * [config](actions/config.md) - adjusts packs' configuration to resources available on a cluster 
    * [experiment](actions/experiment.md) - training and managing training jobs    
    * [launch](actions/launch.md) - launching browser for Web UI and Tensorboard
    * [model](actions/model.md) - export model
    * [mount](actions/mount.md) - displaying details concerning how to mount user's folders
    * [predict](actions/predict.md) - deploy and manage inference on trained model
    * [template](actions/template.md)  - manage template packs used by nctl application
    * [user](actions/user.md) - adding/deleting/listing users of the system 
    * [verify](actions/verify.md) - verifies installation of _nctl_ application
    * [version](actions/version.md) - displays version of _nctl_ application
        
## Advanced Sections

* [Installing Libraries and Dependencies](advanced/customlibs.md)
* [Controlling Packs Parameters](advanced/packs.md)
* [Administrator access to Gitea console](advanced/gitea_console.md)

- - - -

To read Intel Terms and Conditions check [this](TaC.md) document.

This user guide is subject to [CC-BY-ND 4.0](https://creativecommons.org/licenses/by-nd/4.0/).
