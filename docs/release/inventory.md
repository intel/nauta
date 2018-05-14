# Inventory

## Installation inventory variables

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


## Examples

Examples can be found on [Inventory examples directory](examples/inventory)
