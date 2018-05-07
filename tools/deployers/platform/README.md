# Installation

Requirements:
  * Working yum
  * CentOS 7.4.1708

Installation requirements:
  * SSH key pair - we will use SSH Private and Public key for ansible installation process
  * Access to `http://repository.toolbox.nervana.sclab.intel.com/`
  * Carbon Release ID
  * Installed python3.6 with virtualenv
  * sshpass installed on host (in case when password authentication is used)

## Installation inventory variables

Example inventories are in [inventory](examples/inventory/)

Basic ssh parameters for ansible should be used to determine how to get root access on remote hosts:
* ansible_ssh_user
* ansible_ssh_pass
* ansible_ssh_host
* ansible_ssh_port
* ansible_ssh_user
* ansible_become_method - default sudo
* ansible_become_pass
* ansible_become_exe
* ansible_become_flags

### ansible_client_python
Path to python2.7 on target host

Type: path
Default: None
Required: True
Used when: always
Exclusive with: -
Acceptable values: ansible path

### internal_interface
Internal interface name - used for internal communication between kubernetes processes and pods

Spec:
* Type: string
* Default: None
* Required: True
* Used when: always
* Exclusive with: -
* Acceptable values: interface name

### data_interface
Data interface name - used for ScaleIO data transfer and communication - can be used same as internal_interface

Spec:
* Type: string
* Default: None
* Required: True
* Used when: always
* Exclusive with: -
* Acceptable values: interface name

### external_interface
External interface name - used for external network communication

Spec:
* Type: string
* Default: None
* Required: True
* Used when: always
* Exclusive with: -
* Acceptable values: interface name

### nfs_device
Device used for NFS file system

Spec:
* Type: string
* Default: None
* Required: True
* Used when: always
* Exclusive with: -
* Acceptable values: device name

## Installation config file
<TBD>

## Installation targets

### verify

Hosts in inventory will be checked if everything is ok. Checked scopes:
* interface existence
* correct dls repository installed
* correct dls python installed

### init

Hosts gonna be verified in same way step `verify` is doing this, but missing repositories gonna be installed

### install

Installation process on provided inventory

## Installation parameters

### ENV_CONFIG

Location of configuration file

### ENV_INVENTORY

Location of inventory file

## Installation process

* Create inventory file
* Copy and modify configuration file
* Init hosts for installation `make init ENV_CONFIG=<config> ENV_INVENTORY=<inventory>`
* Install kubernetes `make install ENV_CONFIG=<config> ENV_INVENTORY=<inventory>`
