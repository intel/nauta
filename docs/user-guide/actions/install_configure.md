# Client Installation and Configuration

This section provides instructions for installing and configuring Nauta to run on your client system, and discusses the following main topics: 

- [Supported Operating Systems](#supported-operating-systems)  
- [Required Software Packages](#required-software-packages)  
- [Installation](#installation)
- [Setting Variables Permanently](#setting-variables-permanently)

For instructions to install and configure Nauta to run on the host server, refer to the 
[Nauta Installation, Configuration, and Administration Guide](../../installation-and-configuration/README.md). 


## Supported Operating Systems

This release of the Nauta client software has been validated on the following operating systems and versions:

* Ubuntu (16.04, 18.04)
* RedHat 7.5
* macOS High Sierra (10.13)

## Required Software Packages

The following software _must_ be installed on the client system before installing Nauta client:


* kubectl version 1.10 or later, refer to: [Install Kubectl](https://kubernetes.io/docs/tasks/tools/install-kubectl/#install-kubectl)
* git version 1.8.3.1 or later

## Installation

To install the Nauta client software package, do the following:

1.	Download and install the two required software packages listed above, preferably in the order given.

2.	Build the Nauta client software package for your operating system ([Nauta CLI build instructions](nctl.md)). There is no installation utility. You can unpack this package and place the unpacked files in any location you prefer. Take note of the path. 

3.	Set KUBECONFIG environment variable to the Kubernetes configuration file provided by your Nauta administrator. The `<PATH>` is located wherever your _config_ file is stored.
 
    * For **macOS/Ubuntu**, enter: `export KUBECONFIG=<PATH>/<USERNAME>.config`
 
4.	**Optional:** Add the package `nctl` to your terminal PATH. `NCTL_HOME` should be the path to the nctl application folder:

    * For **macOS/Ubuntu**, enter: `export PATH=$PATH:NCTL_HOME`
    
## Setting Variables Permanently

Should you want to permanently set the variables, you can add the variables to your:

* .bashrc
* .bash_profile

Alternatively, you may want to set the PATH and KUBECONFIG variables in the  _Environment Variables_ window. This is accessed by opening the Control Panel > System and Security > System > Advanced system settings, and accessing Environment variables. This is an administrator function only.

 ----------------------

## Return to Start of Document

* [README](../README.md)

----------------------

