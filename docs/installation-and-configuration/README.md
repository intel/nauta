# Nauta Installation, Configuration, and Administration Guide

This Nauta Installation, Configuration, and Administration guide provides step-by-step instructions for installing and configuring Nauta. This guide also provides an overview of Nauta requirements and configuration options.

**Note:** For instructions on configuring the Nauta client, refer to the [Nauta User Guide](../user-guide/).

Nauta is a software suite that provides a multi-user, distributed computing environment for running deep learning model training experiments. Results of experiments can be viewed and monitored using a command line interface (CLI), Web UI and/or TensorBoard*. You can use existing data sets, your own data, or downloaded data from online sources, as well as create public or private folders to make collaboration among teams easier. 

Nauta runs on Kubernetes* and Docker* for scalability and ease of management. Nauta uses customizable templates to remove the complexities of creating and running single and multi-node deep learning training experiments without all the system's complexity and scripting needed with standard container environments.

# Hardware Requirement Overview

Nauta is intended to run on a multi-server Kubernetes cluster. To run Nauta, you will need at least one Master node, and one or more Worker nodes. Nauta is a platform for performing Deep Learning training, and requires robust hardware specifications to run with optimal performance. 

# Installation Overview

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

# Document Flow

This guide consists of the following main topics, in order:

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



