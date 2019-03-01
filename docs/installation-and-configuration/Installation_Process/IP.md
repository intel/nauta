# Installation Process

Before proceeding with this step, you _must_ create an _Inventory_ and _Configuration_ file. 

* See the example  [Inventory File Information](../Inventory_Tasks/IT.md) and [Configuration File Information](../Configuration_Tasks_Variables/CTV.md). 

## Kernel Upgrade

If you run Linux* kernel prior to 4.* version it is recommended that you upgrade it on all nodes of a cluster before performing a platform installation. 

Running heavy training jobs on workers with the operating system kernel older than 4.* may lead to hanging the worker node. 
* See https://bugzilla.redhat.com/show_bug.cgi?id=1507149 for more information.

This may occur when a memory limit for a training job is set to a value close to the maximum amount of memory installed on this node. These problems are caused by errors in handling memory limits in older versions of the kernel.

The following kernel was verified as a viable fix for this issue (see link below).

* https://elrepo.org/linux/kernel/el7/x86_64/RPMS/

To install the new kernel refer to: Chapter 5, Manually Upgrading the Kernel in Red Hat's* Kernel Administration Guide (see link below).

* https://access.redhat.com/documentation/en-us/red_hat_enterprise_linux/7/html/kernel_administration_guide/ch-manually_upgrading_the_kernel

**Note:** The above kernel _does not_ include Red Hat's optimizations and hardware drivers.

## Installation Procedure

To install Nauta, follow these steps:

1. Set the following environment variables that point to the configuration and inventory file on the Installer Machine.

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

Nauta is installed on cluster nodes in the following folders: `/opt/nauta`,`/usr/bin`, `/etc/nauta-cluster`

## Access Files

On your Installer Machine, the following files are created in the Installation folder. These files are *access files* used to connect to the cluster using kubectl client.

As an output of Kubernetes* installation, files are created in the main installation directory:

`platform-admin.config - cluster admin config file`

As an output of the Nauta installation, files are created in main installation directory:

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

