# Client Installation and Configuration

This section provides instructions for installing and configuring Nauta to run on your client system. For instructions to install and configure Nauta to run on the host server, refer to the 
[Nauta Installation, Configuration, and Administration Guide](../../installation-and-configuration/README.md). 

This section discusses the following main topics: 

- [Supported Operating Systems](#supported-operating-systems)  
- [Required Software Packages](#required-software-packages)  
- [Installation](#installation)
- [Setting Variables Permanently](#setting-variables-permanently)

## Supported Operating Systems

This release of the Nauta client software has been validated on the following operating systems and versions.

* Ubuntu (16.04, 18.04)
* Red Hat 7.6
* macOS High Sierra (10.13)

## Required Software Packages

The following software _must_ be installed on the client system before installing Nauta client:

* kubectl version 1.15 or later, refer to: [Install Kubectl](https://kubernetes.io/docs/tasks/tools/install-kubectl/#install-kubectl)
* git version 1.8.3.1 or later. 

## Installation

Complete the following steps to install the Nauta client software package:

1.	Download and install the _Required Software Package_ above, preferably in the order given.

2. There _is no_ installation utility. Unpack this package and place the unpacked files in any preferred loctation. Take note of the path. 

3.	Set KUBECONFIG environment variable to the Kubernetes configuration file provided by your Nauta administrator. The `<PATH>` is located wherever your _config_ file is stored.
 
    * For **macOS/Ubuntu**, enter: `export KUBECONFIG=<PATH>/<USERNAME>.config`

4.	**Optional:** Add the package `nctl` to your terminal PATH. `NCTL_HOME` should be the path to the nctl application folder:

    * For **macOS/Ubuntu**, enter: `export PATH=$PATH:NCTL_HOME`
    
## Setting Variables Permanently

Should you want to permanently set the variables, you can add the variables to your:

* .bashrc
* .bash_profile


 ----------------------

## Return to Start of Document

* [README](../README.md)

----------------------
