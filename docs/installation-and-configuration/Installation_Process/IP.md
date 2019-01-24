# Installation Process

Before proceeding with this step, you must create an _Inventory_ and _Configuration_ file. See:  [Inventory File Information](../Inventory_Tasks/IT.md) and [Configuration File Information](../Configuration_Tasks_Variables/CTV.md)

## Kernel upgrade

Running heavy training jobs on workers with the operating system kernel older than 4.* might lead to hanging the worker node. See https://bugzilla.redhat.com/show_bug.cgi?id=1507149 for more information.

Additionally please remember, that update of a kernel should be made before installation of a platform. Otherwise some components of the platform - those which depends on libraries installed with a new kernel - will be removed.

This may occur when a memory limit for 0 job is set to a value close to the maximum amount of memory installed on this node. These problems are caused by errors in handling memory limits in older versions of the kernel. To avoid this problem, it is recommended to install on all nodes of a cluster with a newer version of a system's kernel.

The following kernel was verified as a viable fix for this issue (see link below).

* https://elrepo.org/linux/kernel/el7/x86_64/RPMS/

To install the new kernel refer to: Chapter 5, Manually Upgrading the Kernel in RedHat's Kernel Administration Guide (see link below).

https://access.redhat.com/documentation/en-us/red_hat_enterprise_linux/7/html/kernel_administration_guide/ch-manually_upgrading_the_kernel

Note: The above kernel does not include RedHat's optimizations and hardware drivers.

## Installation Procedure

To install Nauta, follow these steps:
1. Set variables with configuration file, and: set environment variables to point to the configuration and inventory file on   Installer Machine.

* **ENV_INVENTORY (mandatory):** Inventory file location, for example:

  
`export ENV_INVENTORY=<absolute path to inventory file>`
  
* **ENV_CONFIG (mandatory):** Configuration file location, for example:

  
`export ENV_CONFIG=<absolute path to config file>`
   
2. Run the installation:

`./installer.sh install`

## Installation Script Options

Invoke `./installer.sh` with one of the following options:

* **install:** Kubernetes and Nauta Installation
* **platform-install:** Kubernetes installation only
* **nauta-install:** Nauta installation only
    - **Note:** It is assumed that Kubernetes is already installed. In addition, this requires the same procedure for Nauta upgrades.
* **nauta-upgrade:** Nauta installation upgrade

## Installation Output 

Nauta will be installed on cluster nodes in the following folders: /opt/nauta`,`/usr/bin`, `/etc/nauta-cluster`


## Access Files

On installer machine, the following files will be created in the Installation folder. These files are access files used to connect to the cluster using kubectl client.

As an output of Kubernetes installation, files are created in the main installation directory:

`platform-admin.config - cluster admin config file`

As an output of the nauta installation, files are created in main installation directory:

`nauta-admin.config - NAUTA admin config file`

## Upgrading Nauta

To upgrade Nauta, do the following:

`export NAUTA_KUBECONFIG=/<PATH>/nauta-admin.config`
   
Call the installer with nauta-upgrade option:

`./installer.sh nauta-upgrade`

**Note:** It is recommended that you _do not_ use the cluster during an upgrade.

This completes the Nauta Installtion Process.

## User Management Tasks & Troublshooting

* [User Management Tasks](../User_Management/UM.md)

* [Troubleshooting Information](../Troubleshooting/T.md)






