# # Nauta on Google Cloud Platform*: Advanced Options

The instructions contained in this document provide step-by-step guidance on the Nauta on Google Cloud Platform advanced options that you may need. For getting started information, refer to the [Nauta on Google Cloud Platform - Getting Started](gcp.md).

## Overall Cluster Architecture

A GCP Nauta Kubernetes* instance consists of:

- **gateway:** Bastion host to access to cluster
- **test node: (optional)** Bastion host with test software to do continuous tests
- **nfs server:** Internal server with NFS* based resources
- **gke cluster:** - Kubernetes cluster

**Note:** Refer to the terraform definition files (located in the directory `terraform/templates`) to see detailed configuration (networking, resources, etc.)

## Prerequisites

### Workstation

To install Nauta on a GCP workstation (Linux* or Mac-based*), access to the internet is required. Furthermore, the installation repository (Nauta) has to be downloaded or cloned from the (Nauta) GitHub repository.

***All operations described below should be made on a workstation. All paths are connected with downloaded or cloned repository*** 

### Google Cloud Platform

Service account has to be created to operate on user's project (please refer to https://console.cloud.google.com/iam-admin/serviceaccounts?project=<project_name>).

**Note:** A service account _must have_ `project-owner` priviliges; and, be ready to create GKE cluster, vpc, virtual machines.

#### GCP Access Config

Copy your previously downloaded JSON configuration file (for the service account) as `gcp-service-account.json` into the  `$NAUTA_DIR/toolbox/providers/gcp` directory. 

**Note:** Values defined in config file are generated during service account creation.

### Connectivity Configuration

During installation, several operations on cluster are performed using SSH connectivity. In addition, Network configuration is stored
in `toolbox/config.yml` file.

#### No Proxy Configuration

```$xslt
proxy_env:
  http_proxy: ""
  https_proxy: ""
  no_proxy: ""
  ssh_args_for_proxy: ""
  ssh_args_for_cmd_line: ""
  ssh_args_prefix_for_proxy: ""

proxy: "{{ proxy_env }}"
```

#### Configuration with Proxy

```$xslt
proxy_env:
  http_proxy: "{{ lookup('env', 'http_proxy') | default('') }}"
  https_proxy: "{{ lookup('env', 'https_proxy') | default('') }}"
  no_proxy: "{{ lookup('env', 'no_proxy') | default('') }}"
  ssh_args_for_proxy: "-o ProxyCommand='nc -X 5 -x myproxy.com:1080 %h %p'"
  ssh_args_for_cmd_line: "nc -X 5 -x myproxy.com:1080 %h %p"
  ssh_args_prefix_for_proxy: "nc -X 5 -x myproxy.com:1080"

proxy: "{{ proxy_env }}"
```
- `http_proxy`, `https_proxy`, `no_proxy` are standard variables to connect with internet to access online resources
(in this case there are taken from environment)
- `ssh_args_for_proxy`, `ssh_args_for_cmd_line`, `ssh_args_prefix_for_proxy` are custom variables used to define 
`ssh`/`scp` options in `ProxyCommand` part
(`ssh_args_for_proxy` is full value, `ssh_args_for_cmd_line`, `ssh_args_prefix_for_proxy` are parts for specific purposes)

**Note:** For specific SSH connectivity, refer to `ssh`/`scp` manuals.

## Basic Configuration

Kubernetes cluster resources and connectivity servers can be defined in a YAML file (for example: `gcp-config.yml`).

```$xslt
gcp:
  region: "europe-west1"
  zone: "europe-west1-b"

  external_username: "nauta"

  gateway_type: "n1-standard-4"
  testnode_type: "n1-standard-4"
  nfs_type: "n1-standard-2"

  internal_username: "nauta"

  pool_type: "n1-standard-16"
  pool_size: "1"

  generate_test_node: False
  testnode_image: ""
``` 

- `region` and `zone` - Typical GCP parameters
- `external-username` - Username to connect to bastion (gateway) server
- `gateway_type` - Node type (see server types accessible in region and zone defined above) for bastion (gateway) server
- `testnode_type` - Node type (see server types accessible in region and zone defined above) for test server
- `nfs_type` - Node type (see server types accessible in region and zone defined above) for internal nfs server
- `nfs_disk_size` - Size (in GB) of the disk attached to nfs server to store user data
- `internal_username` - Username for internal ssh connectivity
- `pool_type` - Node type (see server types accessible in region and zone defined above) for gke cluster resources
- `pool_size` - GKE cluster servers quantity
- `pool_min_cpu_platform` - CPU architecture
- `generate_test_node` `[True|False]` - Boolean flag to decide if test node will be created
- `test_node_image` - The name of the image accessible in the GCP project to create test node with pre-installed test software


## Installation Process

The _Installer Process_ uses [Terraform](https://www.terraform.io/) to create resources on the Google Cloud Platform.

### Installer Options
```Usage:
gcp.sh [options]
```
**Options:**

- `operation` `[create,destroy,]` - Operation to perform. If empty only installation attempt will be perform.
- `k8s-cluster` - [nauta] - Kubernetes cluster name.
- `gcp-config` `[pwd/gcp-config.yml]` - Config file with cluster parametrs (resources, access).
- `external-public-key` `[~/.ssh/id_rsa.pub]` - Path to file with public key accepted by cluster gateway to connect.
- `external-key` `[~/.ssh/id_rsa]` -Path to file with private key used to connect to cluster gateway.
- `s3-url` Url to s3 bucket to store terraform cluster state. By default local file will be used.
- `s3-secret-key` Secret key to s3 bucket.
- `s3-access-key` Secret key to s3 bucket.
- `install-file` Path to nauta installer file.
- `client-file` Path to nauta client installer file.
- `network-settings` `config.yml` - File name with network settings in provider directory.
- `compile-platform-on-cloud` [`false|true]` - If true plagform packages will be create on bastion/gatway node.
- `service-account-config-file` `[gcp-service-account.json]` Path to GCP service account config file.
- `platform-config-file` Path to platform config file

### Use Cases
- #### Destroy cluster
```$xslt
./gcp.sh --k8s-cluster nauta-cluster --operation destroy
```

- #### Create cluster

This command creates the GKE cluster and resources related to the cluster (gateway, NFS).

```$xslt
./gcp.sh --k8s-cluster nauta-cluster --operation create \
                                     --gcp-config `pwd`/gcp-config.yml
```

- #### Create cluster and install platform

This command creates a GKE cluster, resources, and installs Nauta from a local file.

```$xslt
./gcp.sh --k8s-cluster nauta-cluster --operation create \
                                     --gcp-config `pwd`/gcp-config.yml \
                                     --install-file /opt/project-data/repository/releases/nauta/nauta-1.0.0-latest.tar.gz
```

- #### Create cluster and install platform

This command creates the GKE cluster, resources; compiles and creates platform distribution artifacts on the gateway node and installs Nauta.

```$xslt
./gcp.sh --k8s-cluster nauta-cluster --operation create \
                                     --gcp-config `pwd`/gcp-config.yml \
                                     --compile-platform-on-cloud true
```

### Installer Output
#### Access Data

IP addresses for Bastion nodes are visible in `<cluster_name>.info` file. A user can access to Bastion/gateway node using:

```$xslt
ssh -i /pathtoprivatekey -o ProxyCommand='nc -X 5 -x myproxy.com:1080 %h %p' <external-user>@<ip-gateway>
```

or without proxy:

```$xslt
ssh -i /pathtoprivatekey <external-user>@<ip-gateway>
```
#### Definition Data

During cluster creation all data related with terraform definition and state is stored in the `.workspace/terraform/<cluster-name>` directory.
