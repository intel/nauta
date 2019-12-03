# Inventory File Tasks

Nauta uses Ansible (refer to [Ansible Overview](https://en.wikipedia.org/wiki/Ansible_(software))) for certain provisioning tasks during installation. You _must_ create (or modify) an Ansible inventory file to match your hardware configuration. Nauta looks for your inventory file at the location defined in the `ENV_INVENTORY` environment variable (refer to the [Installation Process](../Installation_Process/IP.md) for more information).

Your Nauta cluster will contain one Master node and one or more Worker nodes. Each of these nodes _must be_ specified in the Inventory file. Refer to the [Configuration File](../Configuration_Tasks_Variables/CTV.md) for Configuration file information.

This section discusses the following main topics: 

- [Inventory File Configuration Example](#inventory-configuration-file-example)  
- [Inventory File Structure](#inventory-file-structure)
- [Per-node Inventory Variables](#per-node-inventory-variables)

## Inventory Configuration File Example

Below is an example of Inventory file and shows one Master Node and five Worker nodes. Your configuration may differ from the example shown. However, you can copy and modify the information to create your own Ansible Inventory file.

**Note:** Ansible uses the YAML format. Refer to [YAML Format Overview](https://en.wikipedia.org/wiki/YAML) for more information (scroll right to see full contents).

```yaml
[master] 
master-0 ansible_ssh_host=192.168.100 ansible_ssh_user=root ansible_ssh_pass=YourPassword internal_interface=em2 external_interface=em3 local_data_device=/dev/sdb1

[worker] 
worker-0 ansible_ssh_host=192.168.100.61 ansible_ssh_user=root ansible_ssh_pass=YourPassword internal_interface=p3p1 external_interface=em1
worker-1 ansible_ssh_host=192.168.100.55 ansible_ssh_user=root ansible_ssh_pass=YourPassword internal_interface=p3p1 external_interface=em1
worker-3 ansible_ssh_host=192.168.100.106 ansible_ssh_user=root ansible_ssh_ pass=YourPassword internal_interface=p3p1 external_interface=em1
worker-4 ansible_ssh_host=192.168.100.107 ansible_ssh_user=root ansible_ssh_ pass=YourPassword internal_interface=p3p1 external_interface=em1
```

## Inventory File Structure

The file contains two sections, master and worker:

1. `[master]` Contains a description of a master node. This section _must_ contain **exactly one row**.

1. `[worker]` Contains descriptions of worker. Each worker is described in one row. In this section, it can have one or many rows depending on the structure of the cluster.

Each row describes a server (playing either the role of _Master_ or _Worker_ depending on which section the row is in). For each server, the Inventory file _must_ define a series of values that tells Nauta where to find the server, how to log into the server, and so on. 

The format for each row is as follows: 

```
[SERVER_NAME] [VAR_NAME1]=[VAR_VALUE1] [VAR_NAME2]=[VAR_VALUE2] [VAR_NAME3]=[VAR_VALUE3]...
```

### Standard Hosting Name Rules

The `SERVER_NAME` _must_ conform to standard host naming rules and each element of the hostname _must_ be from 1 to 63 characters long. The entire hostname, including the dots _must not_ exceed 253 characters long. 

Valid characters for hostnames are ASCII(7) letters from a to z (lowercase), the digits from 0 to 9, and a hyphen. However, **_do not_**  start a hostname with a **_hyphen_**. 

## Per-node Inventory Variables

The table below lists all the variables understood by Nauta's inventory system. Some variables are required for all servers in the inventory and some variables are optional.

Variable Name | Description | Req? | Type | Default | Used When | Value |
--- | ---  | --- | --- | --- | --- | --- 
ansible_ssh_user | The user name _must be_ the same for master and worker nodes. <br><br> **Note:** If an Administrator decides to choose something other than root for Ansible SSH user, the user _must be_ configured in sudoers file with NOPASSWD option. <br><br> Refer to the official [Ansible Inventory documentation](https://docs.ansible.com/ansible/latest/user_guide/intro_inventory.html) for more information. | Yes | string | none | always | username
ansible_ssh_pass | The SSH password to use. | Yes | string | none | always | Password
ansible_ssh_host | The name (DNS name) or IP Address of the host to connect to. | Yes | IPaddr | none | always | IP Address
ansible_ssh_port | The SSH port number, if not defined 22 is used. | No | int | 22 | not using 22 | Port Address
ansible_ssh_private_key_file | This is a Private Key file used by SSH. | No | string | none | using a keyfile | filename
internal_interface | This is used for internal communication between Kubernetes processes and pods. All interfaces (both external and internal) are Ethernet interfaces. | Yes | string | none |  always used for both for master and worker nodes |  Interface name
local_data_device | This device is used for Nauta internal data and NFS data in case of local NFS. | Yes | string | none | used with master nodes | Path to block device
local_device | This device is used for Nauta internal data and NFS data in case of local NFS. | Yes | string | none | used with master nodes | Path to block device
local_data_path | This is used as the mountpoint for `local_data_device` | No | string | none | used with master nodes |  Absolute path where data is located in file system
external_interface | This is used for external network communication. | Yes | string | none | always used for both for master and worker nodes | Interface name

**Note:** It is recommended to use separate interfaces as values of `internal_interface` and `external_interface`,
but configuration with single interface acting as both local and external interface will also work.
If you use separate interfaces for internal/external communication, it is recommended that the`local_interface` be a SFP+ or fiber network. 

## Next Steps: Configuration Tasks

* [Configuring Nauta - Proxies, File System and Network](../Configuration_Tasks_Variables/CTV.md)

----------------------

## Return to Start of Document

* [README](../README.md)

----------------------
