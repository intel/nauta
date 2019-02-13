# Installation Requirements

## Nauta Package: Extraction from Local Package

Copy the package to the installer machine, then untar it using the following command:

`tar -zxf nauta-1.0.0-beta.tar.gz -C <destination>`

### Nauta Structure

In extracted archive, the following appears:
- **Files**
  - **installer.sh:** sh script
  - **ansible.cfg:**  configuration file for Ansible*

- **Folders**
   - **bin:** binary directory
   - **docs:** documentation 
   - **libs:** contains various scripts that are used by the installer
   - **nauta:** Nauta Enterprise applications deployer
   - **platform:** Kubernetes platform deployer


### Components Version

To see the list of installed components and their versions, refer to: [List of Software Components](../System_Software_Components_Requisites/SSCR.md)

## Next Steps: Nauta Installation Process 

* [Installation Process](../Installation_Process/IP.md)



