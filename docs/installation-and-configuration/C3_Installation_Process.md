## Installation Process

Before proceeding with this step, you must create a configuration and an inventory file (see [Configuration examples directory example](Z_examples/Configuration) and [Inventory examples directory example](Z_examples/Inventory)).

### Installation Procedure

To install Intel DL Studio, follow these steps:
1. Export variables with configuration file, and:
  * **ENV_INVENTORY (mandatory):** Inventory file location, for example: `export ENV_INVENTORY=$(realpath <inventory file>)`
  * **ENV_CONFIG (mandatory):** Configuration file location, for example: `export ENV_CONFIG=$(realpath <config file>)`
2. Run the installation: `./installer.sh install`

## Installer’s Parameters
* **install:** kubernetes and DLS4Enterprise installation
* **platform-install:** kubernetes installation
* **dls4e-install:** DLS4Enterprise installation
* **dls4e-upgrade:** DLS4Enterprise upgrade

**Note 1:** The default installation is targeting: `/opt/dls4e`. In addition, there are some binaries targeting: `/usr/bin` and settings located in `/etc/dls-cluster`. The path _cannot_ be changed.

**Note 2:** The version is included in the package name.

## Installation Build Process Artifacts

As an output of platform installation, files are created in the main installation directory:
- `platform-admin.config - cluster admin config file`

As an output of the dls4e installation, files are created in the main installation directory:
- `dls4e-admin.config - DLS4E admin config file`

## Upgrading Intel DL Studio

To upgrade the Intel DL Studio, do the following:

`export DLS_KUBECONFIG=/path/to/dls4e-admin.config`
   - Call the installer with dls4e-upgrade:<br>
   - `./installer.sh dls4e-upgrade`

**Note:** It is recommended to _not_ use the cluster during an upgrade.
