# Inventory File Configuration Tasks

Configuration files are YAML* files used to define configuration settings so that will be used with Nauta. As part of the Inventory configuration tasks you need to create a YAML file and modify the file for the system inventory.

## Invetory File Example
Below is an example of Inventory File and shows one Master Node and five Worker nodes. Your configuration may differ from the example shown. 

**`[master]`** 

`master-0 ansible_ssh_host=192.168.100 ansible_ssh_user=root ansible_ssh_pass=YourPassword internal_interface=em2 data_interface=em2 external_interface=em3 local_data_device=/dev/sdb1`

**`[worker]`** 

`worker-0 ansible_ssh_host=192.168.100.61 ansible_ssh_user=root ansible_ssh_pass=YourPassword internal_interface=p3p1 data_interface=p3p1 external_interface=em1` 

`worker-1 ansible_ssh_host=192.168.100.55 ansible_ssh_user=root ansible_ssh_pass=YourPassword internal_interface=p3p1 data_interface=p3p1 external_interface=em1` 

`worker-3 ansible_ssh_host=192.168.100.106 ansible_ssh_user=root ansible_ssh_ pass=YourPassword internal_interface=p3p1 data_interface=p3p1 external_interface=em1` 

`worker-4 ansible_ssh_host=192.168.100.107 ansible_ssh_user=root ansible_ssh_ pass=YourPassword internal_interface=p3p1 data_interface=p3p1 external_interface=em1` 


## Inventory File Structure

The file contains two sections:
* **Master:** Contains a description of a master node. This section must contain exactly one row.
* **Worker:** Contains descriptions of workers. Each worker is described in one row. In this section, it can have one or many rows depending on a structure of a cluster.

Format of rows with node's descriptions is as follows (all parts of such row are separated with spaces):

`[NAME] [VARIABLES]`

* **NAME:** This is a name of a node. It should be a hostname of a real node. However, this _is not_ a requirement.

* **VARIABLES:** Variables describing the node in the following format: 

`[VARIABLE_NAME]=[VARIABLE_VALUE]`



## Installation Inventory Variables

The table below shows the basic SSH parameters for RedHat* Ansible* that must be used to determine how to gain root access on remote hosts.


Name | Description 
--- | ---  
ansible_ssh_user | The user name must be the same for master and worker nodes
ansible_ssh_pass | The SSH password to use
ansible_ssh_host | The name (DNS name) or IP Address of the host to connect to. 
ansible_ssh_port | The SSH port number, if not defined 22 is used. However, if this variable is present it must have an assigned value. If you do not enter a value in this row for the file, the default value is 22
ansible_ssh_private_key_file | This is a Private Key file used by SSH

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
* **Default:** local_data_path is optional 
* **Required:** false
* **Used when:** used with master nodes
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

## Next Steps: Configuration Tasks

* [Configuration Tasks: (Varibles: Proxy, DNS, File Examples)](../Configuration_Tasks_Variables/CTV.md)
