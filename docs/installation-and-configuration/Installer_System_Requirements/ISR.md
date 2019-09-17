# Nauta Installer System Requirements 

When installing Nauta, it should be installed on a separate machine (your _Installer machine_), as Nauta requires a separate machine to run the installer. For installation information, refer to the [Installation Process](../Installation_Process/IP.md).

## Nauta Supported Operating Systems

Nauta supports the following Operating Systems: 
  * RedHat Enterprise Linux 7.5 or CentOS 7.5
  * Ubuntu 16.04
   
### Red Hat Enterprise Linux 7.5

Required on system, software requirements:
  * Python 2.7 and /usr/bin/python available
  * Python 3.5
  * sshpass (when password authentication is used)
  * Helm 2.9.1 (the version of a Helm client _must be_ the same as Helm server used by the platform)
   
### CentOS 7.5

Required on system, software requirements:
  * Python 2.7 and /usr/bin/python available
  * Python 3.5
  * sshpass (when password authentication is used)
  * Helm 2.9.1 (the version of a Helm client _must be_ the same as Helm server used by the platform)
  
### Ubuntu 16.04

Required on system, software requirements:
  * Python 2.7 and /usr/bin/python available
  * Python 3.5
  * apt packages installed:
    - python3-pip
    - build-essential
    - libffi-dev
    - libssl-dev
    - sshpass
  * Helm 2.9.1 (the version of a Helm client _must be_ the same as Helm server used by the platform)

## Next Steps: Target Host Requirements

* [Target Host Requirements](../Target_Host_Requirements/THR.md)


----------------------

## Return to Start of Document

* [README](../README.md)

----------------------



