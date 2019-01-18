# Installation Process

Before proceeding with this step, you must create an inventory and configuration file LINKS PENDING TO EXAMPLES.

## Nauta Installer: Two Modes
Nauta Installer supports two modes: full installation or upgrade. Full installation requires that RedHat 7.5 operating system is installed and configured on the host account to the information included in this document. 


## Installation Procedure

To install Nauta, follow these steps:
1. Set variables with configuration file, and: set environment variables to point to the configuration and inventory file on   Installer Machine.

* **ENV_INVENTORY (mandatory):** Inventory file location, for example:

  
`export ENV_INVENTORY=$(absolute path <inventory file>)`
  
* **ENV_CONFIG (mandatory):** Configuration file location, for example:

  
`export ENV_CONFIG=$(absolute path <config file>)`
   
2. Run the installation:

`./installer.sh install`

## Installation Script Options

Invoke `./installer.sh` with one of the following options:

* **install:** Kubernetes and Nauta Installation
* **platform-install:** Kubernetes installation only
* **nauta-install:** Nauta installation only
    - **Note:** It is assumed that Kubernetes is already installed. In addition, this requires the same procedure for Nauta upgrades.
* **nauta-upgrade:** Nauta installation upgrade

## Additional Installer Parameter Information 

The default installation targets: /opt/nauta. In addition, there are some binary files that target: `/usr/bin` and settings located in: `/etc/nauta-cluster`. The path _cannot_ be changed and the version is included in the package name.


## Installation Build Process Artifacts

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
