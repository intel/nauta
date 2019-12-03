# Installation Process

Before proceeding with this step, you _must_ create an _Inventory_ and _Configuration_ file. If you are unsure how to do this, see the example instructions below. 

This section discusses the following main topics: 

- [Creating an Inventory or Configuration File ](#creating-an-inventory-or-configuration-file)  
- [Kernel Upgrade](#kernel-upgrade)
- [Nauta Installation](#nauta-installation)
- [Installation Script Options](#installation-script-options)
- [Access Files for the kubectl Client](#access-files-for-the-kubectl-client)  
- [Upgrading Nauta Procedure](#upgrading-nauta-procedure)

## Creating an Inventory or Configuration File 

The _Inventory_ file defines where your master and worker nodes reside, and how to access them. The _Configuration_ file defines your proxy settings, network quirks, and file system preferences. Should you need to create an _Inventory_ and/or _Configuration_ follow the instructions below. 

### Inventory File Creation

To create Nauta's _Inventory file_, do the following:

1. Copy the Inventory file example information: [Inventory File Information](../Inventory_Tasks/IT.md).

1. Modify the newly created Inventory file to suit your needs using your favorite text editor (vi for example). 

### Configuration File Creation 

To modify Nauta's Configuration file to define your proxy, network quirks, and file system preferences. To create the configuration file, follow these steps:

1. Copy the Configuration file example information: [Configuration File Information](../Configuration_Tasks_Variables/CTV.md).

1. Modify the newly created Configuration file to suit your needs using your favorite text editor (vi for example).

## Kernel Upgrade

If you run Linux kernel prior to 4.x version, it is recommended that you upgrade the kernel on all nodes of a cluster before performing a platform installation. 

Running heavy training jobs on workers with the operating system kernel older than 4.x may lead to hanging the worker node. 
- Refer to [Red Hat Bugzilla – Bug 1507149](https://bugzilla.redhat.com/show_bug.cgi?id=1507149) for more information.

This may occur when a memory limit for a training job is set to a value close to the maximum amount of memory installed on this node. These problems are caused by errors in handling memory limits in older versions of the kernel.

The following kernel was verified as a viable fix for this issue (see link below).

- [Index of /linux/kernel/el7/x86_64/RPMS](https://elrepo.org/linux/kernel/el7/x86_64/RPMS/)

To install the new kernel refer to [CHAPTER 5. MANUALLY UPGRADING THE KERNEL](https://access.redhat.com/documentation/en-us/red_hat_enterprise_linux/7/html/kernel_administration_guide/ch-manually_upgrading_the_kernel) in Red Hats Kernel Administration Guide.

**Note:** The above kernel _does not_ include Red Hat's optimizations and hardware drivers.

## Nauta Installation

BTo install Nauta, follow these steps.  

### Nauta Installation Procedure

To install Nauta, follow these steps:

1. Set the following environment variables that point to the configuration and inventory file on the _Installer Machine_.

* **ENV_INVENTORY (mandatory):** Inventory file location, for example:
  
  `export ENV_INVENTORY=<absolute path to inventory file>`
  
* **ENV_CONFIG (mandatory):** Configuration file location, for example:

  `export ENV_CONFIG=<absolute path to config file>`
   
2. Run the installation:

    `./installer.sh install`

## Installation Script Options

Invoke `./installer.sh` with one of the following options:

* **install:** Use this option to install Kubernetes and Nauta as part of your installation.
* **platform-install:** Use this option to install **Kubernetes only**.
* **nauta-install:** Use this option to install **Nauta only**.
    - **Note:** If you select this option, it is _assumed_ that Kubernetes is already installed. In addition, this requires the same procedure for Nauta upgrades (see below). 
* **nauta-upgrade:** Nauta installation upgrade (see [Nauta Installation Process](../Installation_Process/IP.md) for Nauta upgrade  procedures). 

### Installation Output 

Nauta is installed on cluster nodes in the following folders: `/opt/nauta`,`/usr/bin`, `/etc/nauta-cluster`

## Access Files for the kubectl Client

On your _Installer Machine_, the following files are created in the Installation folder. These files are *access files* used to connect to the cluster using `kubectl` client.

As an output of Kubernetes installation, `platform-admin.config` file is created and the installation log is written into the log folder in the main installation directory:

`platform-admin.config - cluster admin config file`

As an output of the Nauta installation, As an output of Kubernetes installation, `platform-admin.config` file is created and the installation log is written into the log folder in the main installation directory:

`nauta-admin.config - NAUTA admin config file`

## Upgrading Nauta 

As an administrator, you may be required to upgrade Nauta to gain new features, implement new networking configurations, or stay up-to-date with current versions, and so on. 

## Upgrading Nauta Procedure

To upgrade Nauta, do the following:

1. Set the following environment variables that point to the configuration, inventory and configuration file on the _Installer Machine:_

* **ENV_INVENTORY (mandatory):** Inventory file location, for example:
  
  `export ENV_INVENTORY=<absolute path to inventory file>`
  
* **ENV_CONFIG (mandatory):** Configuration file location, for example:

  `export ENV_CONFIG=<absolute path to config file>`

* **NAUTA_KUBECONFIG (mandatory):** Nauta admin file location, for example:

  `export NAUTA_KUBECONFIG=<absolute path to nauta-admin.config file>`
   
2. Call the installer with nauta-upgrade option:

    `./installer.sh nauta-upgrade`

**Note:** It is recommended that you _do not_ use the cluster during an upgrade.

3. After successful execution of platform upgrade you need to also upgrade all users by running:

    `nctl user upgrade`

**Note:** This command can be run only by an administrator.

This completes the Nauta Upgrade Process.


## Next Steps: User Management Tasks

* [User Management Tasks](../User_Management/UM.md)

----------------------

## Return to Start of Document

* [README](../README.md)

----------------------


