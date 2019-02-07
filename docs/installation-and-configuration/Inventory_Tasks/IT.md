# Inventory Configuration

Nauta uses Ansible for certain provisioning tasks during installation. You must create (or modify) an Ansible inventory file to match your hardware configuration. Nauta will look for your inventory file at the location defined the `ENV_INVENTORY` environment variable (explained in [Installation Process](Installation_Process/IP.md)).

Your Nauta cluster will contain one Master node and one or more Worker nodes. Each of these nodes must be specified in the inventory file.
## Invetory File Example
Below is an example of Inventory File and shows one Master Node and five Worker nodes. Your configuration may differ from the example shown. Note that Ansible uses the YAML format.

```yaml
**[master]** 
master-0 ansible_ssh_host=192.168.100 ansible_ssh_user=root ansible_ssh_pass=YourPassword internal_interface=em2 data_interface=em2 external_interface=em3 local_data_device=/dev/sdb1

**[worker]** 
worker-0 ansible_ssh_host=192.168.100.61 ansible_ssh_user=root ansible_ssh_pass=YourPassword internal_interface=p3p1 data_interface=p3p1 external_interface=em1
worker-1 ansible_ssh_host=192.168.100.55 ansible_ssh_user=root ansible_ssh_pass=YourPassword internal_interface=p3p1 data_interface=p3p1 external_interface=em1
worker-3 ansible_ssh_host=192.168.100.106 ansible_ssh_user=root ansible_ssh_ pass=YourPassword internal_interface=p3p1 data_interface=p3p1 external_interface=em1
worker-4 ansible_ssh_host=192.168.100.107 ansible_ssh_user=root ansible_ssh_ pass=YourPassword internal_interface=p3p1 data_interface=p3p1 external_interface=em1
```

## Inventory File Structure

The file contains two sections:
* `**[master]**` Contains a description of a master node. This section must contain exactly one row.
* `**[worker]**` Contains descriptions of workers. Each worker is described in one row. In this section, it can have one or many rows depending on a structure of a cluster.

Each row describes a server (playing either the role of "master" or "worker" depending on which section the row is in). For each server, the inventory file must define a series of values that tells Nauta where to find the server, how to log into it, etc. The format for each row is as follows:

`[SERVER_NAME] [VAR_NAME1]=[VAR_VALUE1] [VAR_NAME2]=[VAR_VALUE2] [VAR_NAME3]=[VAR_VALUE3]...`

**NOTE**: `SERVER_NAME` must conform to standard host naming rules - each element of the hostname must be from 1 to
63 characters long and the entire hostname, including the dots, can be at most 253 characters long. Valid characters
for hostnames are ASCII(7) letters from a to z, the digits from 0 to 9, and the hyphen. A hostname may not start with
a hyphen.

## Per-node Inventory Variables
The table below lists all the variables understood by Nauta's inventory system. Some variables are required for all servers in the inventory, some are only required for some, and some variables are entirely optional.

Variable Name | Description | Req? | Type | Default | Used When | Value |
--- | ---  | --- | --- | --- | --- | --- 
ansible_ssh_user | The user name must be the same for master and worker nodes. **Note:** If an Administrator decides to choose something other than root for Ansible SSH user, the user must be configured in sudoers file with NOPASSWD option. Refer to [Ansible Inventory documentation](https://docs.ansible.com/ansible/latest/user_guide/intro_inventory.html) for more information. | Yes | string | none | always | username
ansible_ssh_pass | The SSH password to use | Yes | string | none | always | Password
ansible_ssh_host | The name (DNS name) or IP Address of the host to connect to. | Yes | IPaddr | none | always | IP Address
ansible_ssh_port | The SSH port number, if not defined 22 is used. | No | int | 22 | not using 22 | Port Address
ansible_ssh_private_key_file | This is a Private Key file used by SSH | No | string | none | using a keyfile | filenae
internal_interface | This is used for internal communication between Kubernetes processes and pods. All interfaces (both external and internal) are Ethernet interfaces. | Yes | string | none |  always for both for master and worker nodes |  Interface name
local_data_device | This device is used for Nauta internal data and NFS data in case of local NFS. | Yes | string | none | used with master nodes | this is the path to block device
local_data_path | This is used as the mountpoint for `local_data_device.` | No | string | none | used with master nodes |  this is the absolute path where data is located in file system.
data_interface | This is used for data transfer.  This is the same type of variable as internal_interface. | Yes | string | none | always for both for master and worker nodes | interface name
external_interface | This is used for external network communication. | Yes | string | none | always for both for master and worker nodes | interface name

## Next Steps: Configuration Tasks

* [Configuring Nauta - Proxies, Filesystem and Network](../Configuration_Tasks_Variables/CTV.md)
