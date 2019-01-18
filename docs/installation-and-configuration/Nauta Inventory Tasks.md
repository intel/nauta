# Inventory Tasks

This is a YAML file used by Nauta for installation.  It contains the system's inventory: defines the hosts and groups of hosts upon which commands, modules, and tasks where Nauta will be installed. An Administrator should update the YAML file before starting the installation process. In addition, the content of this file should reflect hardware on which the Nauta software is going to be installed.

## Invetory File Example
Below is an Inventory File example that shows one Master node and five Worker nodes. Your configuration may differ from the example shown. 

**`[master]`** 

`master-0 ansible_ssh_host=10.91.120.53 ansible_ssh_user=root ansible_ssh_pass=YourPassword internal_interface=em2 data_interface=em2 external_interface=em3 local_data_device=/dev/sdb1`

**`[worker]`** 

`worker-0 ansible_ssh_host=10.91.120.61 ansible_ssh_user=root ansible_ssh_pass=YourPassword internal_interface=p3p1 data_interface=p3p1 external_interface=em1` 

`worker-1 ansible_ssh_host=10.91.120.55 ansible_ssh_user=root ansible_ssh_pass=YourPassword internal_interface=p3p1 data_interface=p3p1 external_interface=em1` 

`worker-3 ansible_ssh_host=10.91.120.106 ansible_ssh_user=root ansible_ssh_ pass=YourPassword internal_interface=p3p1 data_interface=p3p1 external_interface=em1` 

`worker-4 ansible_ssh_host=10.91.120.107 ansible_ssh_user=root ansible_ssh_ pass=YourPassword internal_interface=p3p1 data_interface=p3p1 external_interface=em1` 

`worker-5 ansible_ssh_host=10.91.120.108 ansible_ssh_user=root ansible_ssh_v internal_interface=p3p1 data_interface=p3p1 external_interface=em1` 

## Inventory File Structure

The file contains two sections:
* **Master:** Contains a description of a master node. This section _must_ contain exactly one row.
* **Worker:** Contains descriptions of workers. Each worker is described in one row. In this section, it can have one or many rows depending on a structure of a cluster.

Format of rows with node's descriptions is as follows (all parts of such row are separated with spaces):

`[NAME] [VARIABLES]`

* **NAME:** This is a name of a node. It should be a hostname of a real node. However, this _is not_ a requirement.

* **VARIABLES:** Variables describing the node in the following format: 

`[VARIABLE_NAME]=[VARIABLE_VALUE]`

This is the list of available variables (shown below), if a certain variable has a default value, which satisfies a user's needs. However, it _is not_ required to be add this to a row. A row may contain more than one variable, in this case variables are separated with spaces.

## Installation Inventory Variables
Basic SSH parameters for RedHat* Ansible* should be used to determine how to gain root access on remote hosts, including:

- ansible_ssh_user
  - The user name must be the same for master and worker nodes
- ansible_ssh_pass
  - The SSH password to use. However, it is highly recommend to skip storing this variable in plain text.
- ansible_ssh_host
  - The name (DNS name) or IP Address of the host to connect to. This is different from any alias you wish to assign.
- ansible_ssh_port
  - o	The SSH port number, if _not_ defined 22 is used.
- ansible_ssh_private_key_file
  - o	A Private Key file used by SSH.

**Note:** If an Administrator decides to choose something other than root for Ansible SSH user, the user must be configured in sudoers file with NOPASSWD option. Refer to [Ansible Inventory documentation](https://docs.ansible.com/ansible/latest/user_guide/intro_inventory.html) for more information. 

### internal_interface
_Internal interface name:_ This is used for internal communication between Kubernetes processes and pods. All interfaces (both external and internal) are Ethernet interfaces.

#### Specification
* **Type:** string
* **Default:** none
* **Required:** true
* **Used when:** always for both for master and worker nodes
* **Acceptable values:** this is the interface name

### local_data_device
_Local data device:_ This device is used for Nauta internal data and NFS data in case of local NFS.

#### Specification
* **Type:** string
* **Default:** none
* **Required:** true
* **Used when:** used with master nodes 
* **Acceptable values:**  this is the path to block device

### local_data_path
_Local data path:_ This is used as the mountpoint for `local_data_device.`

#### Specification
* **Type:** string
* **Default:** local_data_path
* **Required:** false
* **Used when:** this is the storage_type that is set to auto
* **Acceptable values:** this is the absolute path where data is located in file system.

### data_interface
_Data interface name:_ This is used for data transfer.  This is the same type of variable as internal_interface.

#### Specification
* **Type:** string
* **Default:** none
* **Required:** true
* **Used when:** always for both for master and worker nodes
* **Acceptable values:** interface name

### external_interface
**External interface name:** This is used for external network communication.

#### Specification
* **Type:** string
* **Default:** none
* **Required:** true
* **Used when:** always for both for master and worker nodes
* **Acceptable values:** interface name


