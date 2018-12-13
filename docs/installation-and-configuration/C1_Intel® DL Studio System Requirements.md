# Intel® DL Studio System Requirements 

Intel DL Studio supported installer systems, include:
  * Red Hat* Enterprise Linux* 7.5
  * Ubuntu* 16.04
  * CentOS* 7.5
 
### Red Hat Enterprise Linux 7.5

Required on system:
  * sshpass (when password authentication is used)
 
### CentOS 7.5

Required on system:
  * sshpass (when password authentication is used)
  
### Ubuntu 16.04

Required on system:
  * Python 3.5
  * apt packages installed:
    - python3-pip
    - build-essential
    - libffi-dev
    - libssl-dev
    - sshpass

**Note:** If the O/S is reinstalled or configured the system with valid repository that contains required packages, an Administrator would need to reinstall the packages. 

# Target Host Requirements

For the target host, supported systems include:
- Red Hat Enterprise Linux 7.5

In addition, the following is also required on the host:
- Configured access to user over ssh
- For regular users, access to root account via sudo
- Full network connectivity between target hosts

## Red Hat Enterprise Linux 7.5

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

**Note:** Deep Learning Studio Installer supports two modes: full installation or upgrade. 
Full installation requires that RedHat 7.5 O/S is installed and configured on the host account to the information included in this document. For upgrade instructions, refer to the corresponding Release Notes. 
