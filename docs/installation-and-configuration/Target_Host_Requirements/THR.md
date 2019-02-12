

# Target Host Requirements

For the target host, install Nauta on bare metal only with Red Hat Enterprise Linux 7.5* (can be preinstalled).

- Configured access to the master host over SSH.
  - This is configured access from your _Installer Machine to your Target Host (master)._
- Full network connectivity between target hosts is required. In addition, Installer connectivity is only required to the master node.


## Red Hat* Enterprise Linux 7.5

Required packages:
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

If the operating system is installed and configured with a valid repository that contains the required packages, an Administrator _does not_ need to install the packages manually. However, if the repository _is not_ valid the Installer  attempts to install the package automatically. If this fails an error message is displayed. 

## Next Steps: Preparing for the Nauta Installation

* [Inventory File Configuration Tasks](../Inventory_Tasks/IT.md)
