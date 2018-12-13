# Inventory Tasks
This is a _yaml file_ used by Ansible* for installation.  It contains the system's inventory, which defines the hosts and groups of hosts upon which commands, modules, and tasks in a playbook operate. An admin should update it before starting the installation process. In addition, the content of this file should reflect hardware on which the Intel DL Studio software is going to be installed.

The file contains two sections:
* **Master:** contains a description of a master node. This section must contain exactly one row.
* **Worker:** contains descriptions of workers. Each worker is described in one row. In this section, it can have one or many rows depending on a structure of a cluster.

Format of rows with node's descriptions is as follows (all parts of such row are separated with spaces):
`[NAME] [VARIABLES]`
where:

* **NAME:** This is a name of a node. It should be a hostname of a real node (however, this is not a requirement)
* **VARIABLES:** Variables describing the node in the following format: 
  *	`[VARIABLE_NAME]=[VARIABLE_VALUE]`
  *	List of available variables is given below. If certain variable has a default value, which satisfies a user's needs; however, it does not have to be added to a row. A row may contain more than one variable, in this case variables are separated with spaces.

## Installation Inventory Variables

Basic ssh parameters for RedHat* Ansible* should be used to determine how to gain root access on remote hosts, including:
* ansible_ssh_user
* ansible_ssh_pass
* ansible_ssh_host
* ansible_ssh_port
* ansible_ssh_private_key_file

**Note:** If an Administrator decides to choose something other than root for Ansible ssh user, the user _must be_ configured in sudoers file with NOPASSWD option.

### internal_interface
_Internal interface name:_ This is used for internal communication between Kubernetes processes and pods.

#### Specification
* **Type:** string
* **Default:** None
* **Required:** True
* **Used when:** always
* **Exclusive with:** -
* **Acceptable values:** interface name

### local_data_device
_Local data device:_ This is used by elastic search as storage

#### Specification
* **Type:** string
* **Default:** None
* **Required:** True
* **Used when:** for master nodes
* **Exclusive with:** -
* **Acceptable values:** path to block device

### local_data_path
_Local data path:_ This is used as the mountpoint for `local_data_device.`

#### Specification
* **Type:** string
* **Default:** /data
* **Required:** False
* **Used when:** storage_type is set to auto
* **Exclusive with:** -
* **Acceptable values:** block device name

### data_interface
_Data interface name:_ This is used for _ScaleIO data transfer and communication._ This can be used in the same way as `internal_interface.`

#### Specification
* **Type:** string
* **Default:** None
* **Required:** True
* **Used when:** always
* **Exclusive with:** -
* **Acceptable values:** interface name

### external_interface
**External interface name:** This is used for external network communication.

#### Specification
* **Type:** string
* **Default:** None
* **Required:** True
* **Used when:** always
* **Exclusive with:** -
* **Acceptable values:** interface name

## Examples

Examples can be found on: [Inventory examples directory](Z_examples/Inventory)
