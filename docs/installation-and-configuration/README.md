# Nauta Installation, Configuration, and Administration Guide

This Nauta Installation, Configuration, and Administration guide provides step-by-step instructions for installing,   configuring, upgrading, and removing Nauta. This guide also provides an overview of Nauta requirements, configuration options, and administration tasks. 
 
This section discusses the following main topics: 

- [Nauta Hardware Requirement Overview](#nauta-hardware-requirement-overview): Provides an overview of Nauta Hardware requirements.   
- [Nauta Installation Procedures](#nauta-installation-procedures): Provides the Installation Instructions. 
- [Document Flow](#document-flow): This is your gateway to the Nauta installation documentation instructions; start here. 

**Note:** For instructions on configuring the Nauta client, refer to the [Nauta User Guide](../user-guide/README.md).

Nauta is a software suite that provides a multi-user, distributed computing environment for running deep learning model training experiments. Results of experiments can be viewed and monitored using a Command Line Interface (CLI), Web UI and/or TensorBoard. You can use existing data sets, your own data, or downloaded data from online sources, as well as create public or private folders to make collaboration among teams easier. 

Nauta runs on Kubernetes and Docker for scalability and ease of management. Nauta uses customizable templates to remove the complexities of creating and running single and multi-node deep learning training experiments without all the system's complexity and scripting needed with standard container environments.

# Nauta Hardware Requirement Overview

Nauta is intended to run on a multi-server Kubernetes cluster. To run Nauta, you will need at least one Master node, and one or more Worker nodes. Nauta is a platform for performing Deep Learning training, and requires robust hardware specifications to run with optimal performance. 

## Minimal Memory and Disk Requirements 

Node | Count | CPU  | Memory | Disk
---    | ---  | --- | ---  | ---
Master | 1    | 12  | 32Gi | 200Gi
Worker | 2    | 4   | 8Gi  | 200Gi

**Note:** These requirements are based on our development environments and nctl config command specifications. This configuration has been tested and does function. However, it does indicate that Nauta _might_ work on smaller configurations.

### Example of Production Environment Setup 

Node | Count  | CPU    | Memory   | Disk
---    | ---  | ---    | ---      | ---
Master | 1    | 	2x40  | 384Gi	   | 144TB
Worker | 4    | 	2x40  | 192Gi    | 1TB

**Note:** This is just an example of production environment, which is able to run multiple resource demanding experiments at once.

# Nauta Installation Procedures

To install Nauta in a 'bare metal' (for example, non-cloud) server environment, you will need to:

1. Execute the following commands from the command line: 

 - `git clone --recursive https://github.com/IntelAI/nauta.git` 
 
 - `cd nauta`

2. Build the base package (a makefile will automate the bulk of the process, but there are some minimum packages needed for Nauta).

* **Note:** To see the list of installed components and their versions, refer to: [List of Software Components](./System_Software_Components_Requisites/SSCR.md) and for Package information, refer to: [Installation Package Requirements](./Installation_Package_Requirements/IPR.md).
 
3. Populate or create Nauta's inventory file to define where your master and worker nodes are, and how to access them. To create the Inventory file: 

   - Copy the Inventory file example information: [Inventory File Information](./Inventory_Tasks/IT.md).

   - Modify the newly created Inventory file to suit your needs. 

4. Modify Nauta's configuration file to define your proxy, network quirks and filesystem preferences. To create the configuration file: 

   - Copy the Configuration file example infomation: [Configuration File Information](./Configuration_Tasks_Variables/CTV.md).

   - Modify the newly created Configuration file to suit your needs. 

5. Run the installation script (see [Installation Process](./Installation_Process/IP.md) for more information). 

This process does the following:

- Creates a Kubernetes cluster, all the Docker files you need to run Tensorflow, Jupyter, Tensorboard, and Horovod.

- Installs the Nauta server-side application on your new Kubernetes cluster, and starts the system running.

Completing all of the above takes some time. We are working on streamlining the process. 

## Removing Nauta

Should you need to delete/remove Nauta, refer to: [Installation Process](./Installation_Process/IP.md) page for more details. 

# Document Flow

This guide consists of the following main topics, in order. Start here to move through the correct sequence of events. 

* [System Software Components Requisites](System_Software_Components_Requisites/SSCR.md)
* [Building Nauta](How_to_Build_Nauta/HBN.md)
    * [Installer System Requirements](Installer_System_Requirements/ISR.md)
    * [Target Host Requirements](Target_Host_Requirements/THR.md)
* [Inventory Configuration](Inventory_Tasks/IT.md)
* [Nauta Configuration (Variables)](Configuration_Tasks_Variables/CTV.md)
    * [Installation Package Requirements](Installation_Package_Requirements/IPR.md)
* [Installating and Starting Nauta](Installation_Process/IP.md)
* [User Management](User_Management/UM.md)
* [Troubleshooting](Troubleshooting/T.md)

To read Intel Terms and Conditions check [this](TaC.md) document.

This user guide is subject to [CC-BY-ND 4.0](https://creativecommons.org/licenses/by-nd/4.0/).
