# Nauta Installer System Requirements 

When installing Nauta, it should be installed on a separate machine (your installer machine), as Nauta requires a separate machine to run the installer.

## Nauta Supported Operating Systems
Nauta supports the following Operating Systems: 
  * Red Hat* Enterprise Linux* 7.5 or CentOS* 7.5
  * Ubuntu* 16.04
   
### Red Hat Enterprise Linux 7.5

Required on system, software requirements:
  * Python 2.7 and /usr/bin/python available
  * sshpass (when password authentication is used)
  * helm 2.9.1 (version of a helm client must be the same as helm server used by the platform)
   
### CentOS 7.5

Required on system, software requirements:
  * Python 2.7 and /usr/bin/python available
  * sshpass (when password authentication is used)
  * helm 2.9.1 (version of a helm client must be the same as helm server used by the platform)
  
### Ubuntu 16.04

Required on system, software requirements:
  * Python 3.5
  * apt packages installed:
    - python3-pip
    - build-essential
    - libffi-dev
    - libssl-dev
    - sshpass
  * helm 2.9.1 (version of a helm client must be the same as helm server used by the platform)

## Next Steps: Target Host Requirements

* [Target Host Requirements](../Target_Host_Requirements/THR.md)



