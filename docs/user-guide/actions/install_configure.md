# Client Installation and Configuration

TThe section provides instructions for installing and configuring Intel DL Studio to run on your client system. 

For instructions to install and configure Intel DL Studio to run on the host server, refer to the Intel® Deep Learning Studio Installation and Configuration Guide.


## Supported Operating Systems

The Intel DL Studio software runs on the following operating systems listed next. Please contact your Intel representative for information about how to acquire the installation package for your OS.

* Ubuntu 16.04

* macOS

* Windows 10

## Required Software Packages
The following software must be installed on the client system before installing Intel DL Studio:

* kubectl version 1.10 or later: (https://kubernetes.io/docs/tasks/tools/install-kubectl/#install-kubectl)

* docker version 18.03.0-ce or later: (https://docs.docker.com/install/)

**Note**: Helm is shipped together with Intel DL Studio.


## Installation

To install the Intel DL Studio software package, do the following:

1.	Download and install the two required software packages for above, preferably in the order given.

2.	Download and extract the Intel DL Studio client software package for your operating system. 

3.	Set KUBECONFIG environment variable to the Kubernetes configuration file provided by your Intel DL Studio Admin. Here, <PATH> is wherever your _config_ file is located.
 
    * MacOS/Ubuntu: **Execute**: `export KUBECONFIG=<PATH>/<USERNAME>.config`
 
    * Windows: **Execute**: `set KUBECONFIG=<PATH>\<USERNAME>.config`
 
4.	(OPTIONAL) Add the package `dlsctl` to your terminal PATH. `DLSCTL_HOME` should be the path to the dlsctl application folder:

    * MacOS/Ubuntu: **Execute**: `export PATH=$PATH:DLSCTL_HOME`
    
    * Windows: **Execute**: `set PATH=%PATH%;DLSCTL_HOME`
    
**Note**: If you want to set the variables permanently, you can add the variables to your .bashrc, .bash_profile, or Windows system PATH. Alternatively, you may want to set the PATH and KUBECONFIG variables in the “Environment Variables” window. This is accessed by opening the Control Panel > System and Security > System > Advanced system settings, and accessing Environment variables. This is an administrator function only.

 
