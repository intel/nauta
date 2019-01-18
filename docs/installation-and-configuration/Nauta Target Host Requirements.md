

# Target Host Requirements

For the target host (bare metal install only), the supported system is:
- Red Hat Enterprise Linux 7.5

In addition, the following is also required on the host:
- Configured access to user over SSH.
  - This is configured access from your Installer Machine to your Target Host (master).
- Full network connectivity between target hosts.


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

**Note:** If the operating system is installed and configured with a valid repository that contains the required packages, an Administrator _does not_ need to install the packages manually. 
