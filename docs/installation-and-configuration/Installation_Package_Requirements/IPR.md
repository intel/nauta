# Installation Requirements

## Nauta Package: Extraction from Local Package

Copy the package to the installer machine, then untar it using the following command:

`nauta-1.1.0-ent-20191010050128.tar.gz -C <destination>`

**Note:** Refer to [How to Build Nauta, Required Packages ](../How_to_Build_Nauta/HBN.md) section for required package information.

### Nauta Structure

Nauta Structure includes two files and five folders, all of which are installed during the installation process. 

In extracted archive, the following appears:
- **Files**
  - **installer.sh:** sh script
  - **ansible.cfg:**  configuration file for Ansible

- **Folders**
   - **bin:** binary directory
   - **docs:** documentation
   - **diagnose:** contains script to diagnose system if installer fails 
   - **libs:** contains various scripts that are used by the installer
   - **nauta:** Nauta Enterprise applications deployer
   - **platform:** Kubernetes platform deployer

### Components Version

To see the list of installed components and their versions, refer to: [List of Software Components](../System_Software_Components_Requisites/SSCR.md)

## Next Steps: Nauta Installation Process 

* [Installation Process](../Installation_Process/IP.md)

----------------------

## Return to Start of Document

* [README](../README.md)

----------------------


