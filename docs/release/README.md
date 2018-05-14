# Requirements

Supported systems:
  * CentOS 7.4.1708
  * Ubuntu 16.04

Installation requirements:
  * sshpass installed on provisioning host (in case when password authentication is used)

# Installation
 
## Inventory file creation
 
Documentation: [Inventory file specification](inventory.md)
 
## Configuration file creation
 
Documentation: [Configuration file specification](configuration.md)

## DLS4Enterprise package

### Extraction from local package

To extract package from local resource:
* create extraction directory
* extract `tar -zxf <package> -C <destination>`

### Extraction from remote package

To extract package from local resource:
* create extraction directory
* extract `curl <package> | tar -zxf - -C <destination>`

### Structure

In extracted archive you will have:
- Makefile - make definition of installation process
- bin - binary directory
- dls4e - DLS4Enterprise applications deployer
- platform - kubernetes platform deployer
- docs - documentation

## Installation process

Before this step create inventory and configuration file

### With make

Steps:
* verify if your system is supported with `make os-supported`
* export variables with configuration file:
  * ENV_INVENTORY - inventory file location, example `export ENV_INVENTORY=$(realpath <inventory file>)`
  * ENV_CONFIG (optional) - configuration file location, example `export ENV_CONFIG=$(realpath <config file>)`
* check ssh accessibility to all hosts `make pre-verify`
* run installation `make install`

Other make targets:
* platform-install - kubernetes installation
* dls4e-install - DLS4Enterprise installation
* dls4e-upgrade - DLS4Enterprise upgrade
