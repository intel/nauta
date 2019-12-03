# Target Host Requirements

For the _Target host_, install Nauta **on bare metal only** with Red Hat Enterprise Linux 7.6 (this can be preinstalled).

- Configured access to the master host over SSH.
  - This is configured access from your _Installer Machine to your Target Host (master)._
  
- Full network connectivity between a target hosts is required. In addition, Installer connectivity is only required to the master node.

This section discusses the following main topics: 

- [Red Hat Enterprise Linux 7.6](#red-hat-enterprise-linux)  
- [Valid Repositories](#valid-repositories)  
- [Repositories List](#repositories-list)

## Red Hat Enterprise Linux

Red Hat Enterprise Linux 7.6 is required, as well as the following required packages: 

  - byacc
  - cifs-utils
  - ebtables
  - ethtool
  - gcc
  - gcc-c++
  - git
  - iproute
  - iptables >= 1.4.21
  - libcgroup
  - libcgroup-devel
  - libcgroup-tools
  - libffi-devel
  - libseccomp-devel
  - libtool-ltdl-devel
  - make
  - nfs-utils
  - openssh
  - openssh-clients
  - openssl
  - openssl-devel
  - policycoreutils-python
  - python
  - python-backports
  - python-backports-ssl_match_hostname
  - python-devel
  - python-ipaddress
  - python-setuptools
  - rsync
  - selinux-policy >= 3.13.1-23
  - selinux-policy-base >= 3.13.1-102
  - selinux-policy-targeted >= 3.13.1-102
  - socat
  - systemd-libs
  - util-linux
  - vim
  - wget

## Valid Repositories

If the operating system is installed and configured with a valid repository that contains the required packages, an Administrator _does not_ need to install the packages manually. However, if the repository _is not_ valid, the Installer  attempts to install the package automatically. If this fails, an error message is displayed.

## Repositories List

Use the following command to check your repository list: `yum repolist all`

A list of **required** enabled repositories for RHEL 7.6, is:

- Extra Packages for Enterprise Linux 7 - x86_64
- Red Hat Enterprise Linux 7 Server - x86_64
- Red Hat Enterprise Linux 7 Server (High Availability) - x86_64
- Red Hat Enterprise Linux 7 Server (Optional) - x86_64
- Red Hat Enterprise Linux 7 Server (Supplementary) - x86_64

A list of **required** enabled repositories for Centos 7.6, is:

- CentOS-7 - Base
- CentOS-7 - Extras
- CentOS-7 - Updates
- Extra Packages for Enterprise (epel) 

## Data directory

The `/data` directory _must_ be created on the master node before installation. This directory contains persistent Kubernetes', as well as explicit Nauta data. Therefore, you should mount a separate disk to this directory. However, the size is dependent on your needs and the number of users. The recommended disk size is 70Gi, as this is a practical solution for a default three-node Nauta environment.   

## Next Steps: Preparing for the Nauta Installation

* [Inventory File Configuration Tasks](../Inventory_Tasks/IT.md)

----------------------

## Return to Start of Document

* [README](../README.md)

----------------------
