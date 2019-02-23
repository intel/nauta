# # Nauta on Google Cloud* Platform: Advanced Options

This document contains information referring to [Nauta on Google Cloud Platform - Getting Started](gcp.md).

## Overall Cluster Architecture

GCP Nauta Kubernetes instance consists of several parts:

- **gateway:** Bastion host to access to cluster
- **test node: (optional)** Bastion host with test software to do continuous tests
- **nfs server:** Internal server with nfs based resources
- **gke cluster:** - Kubernetes cluster

Refer to terraform definition files (in directory terraform/templates) to see detailed configuration (networking,
resources, etc.)

## Prerequisites

### Workstation

To install Nauta on GCP workstation (Linux or Mac-based) with access to the internet is required. Installation repository (nauta) has to be downloaded or cloned from github repository.

***All operations described below should be made on workstation. All paths are connected with downloaded or cloned repository*** 

### Google Cloud Platform

Service account has to be created to operate on user's project (Refer to https://console.cloud.google.com/iam-admin/serviceaccounts?project=<project_name> for more information).

Service account should have `project-owner` priviliges and be ready to create gke cluster, vpc, and virtual machines.

#### GCP Access Config

Copy previously downloaded JSON configuration file (for service account) as `gcp-service-account.json` into `$NAUTA_DIR/toolbox/providers/gcp` directory. 

**Note:** Values are defined in config file generated during service account creation.

### Connectivity Configuration

During installation several operations on cluster are completed using SSH connectivity. Network configuration is stored
in the `toolbox/config.yml` file.

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

**Note:** For specific SSH connectivity, refer to the `ssh`/`scp` manuals.

## Basic configuration

Kubernetes cluster resources and connectivity servers can be defined in yaml file (for example: `gcp-config.yml`)

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
- `external-username` - Username to connect to Bastion (gateway) server
- `gateway_type` - Node type (see server types accessible in region and zone defined above) for Bastion (gateway) server
- `testnode_type` - Node type (see server types accessible in region and zone defined above) for test server
- `nfs_type` - Node type (see server types accessible in region and zone defined above) for internal NFS server
- `nfs_disk_size` - Size (in GB) of the disk attached to nfs server to store user data
- `internal_username` - Username for internal SSH connectivity
- `pool_type` - Node type (see server types accessible in region and zone defined above) for GKE cluster resources
- `pool_size` - GKE cluster servers quantity
- `pool_min_cpu_platform` - CPU architecture
- `generate_test_node` `[True|False]` - Boolean flag to decide if test node will be created
- `test_node_image` - Name of the image accessible in the gcp project to create test node with pre-installed test software


## Installation Process

Installer process uses [Terraform](https://www.terraform.io/) to create resources on Google Cloud Platform.

### Installer Options

```Usage:
gcp.sh [options]
```
**Options:** 

- `operation` `[create,destroy,]` - Operation to perform. If an _empty only_ installation attempt will be performed.
- `k8s-cluster` - [nauta] - Kubernetes cluster name.
- `gcp-config` `[pwd/gcp-config.yml]` - Config file with cluster parametrs (resources, access).
- `external-public-key` `[~/.ssh/id_rsa.pub]` - Path to file with public key accepted by cluster gateway to connect.
- `external-key` `[~/.ssh/id_rsa]` -Path to file with private key used to connect to cluster gateway.
- `s3-url` Url to s3 bucket to store terraform cluster state. By default, a local file will be used.
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

- #### Create Cluster

This command creates gke cluster and resources related to the cluster (gateway, nfs).

```$xslt
./gcp.sh --k8s-cluster nauta-cluster --operation create \
                                     --gcp-config `pwd`/gcp-config.yml
```

- #### Create Cluster and Install Platform

This command creates gke cluster, resources and installs nauta from local file.

```$xslt
./gcp.sh --k8s-cluster nauta-cluster --operation create \
                                     --gcp-config `pwd`/gcp-config.yml \
                                     --install-file /opt/project-data/repository/releases/nauta/nauta-1.0.0-latest.tar.gz
```

- #### Create Cluster and Install Platform

This command creates gke cluster, resources: compiles and create platform distribution artifacts on gateway node and installs Nauta.

```$xslt
./gcp.sh --k8s-cluster nauta-cluster --operation create \
                                     --gcp-config `pwd`/gcp-config.yml \
                                     --compile-platform-on-cloud true
```

### Installer Output
#### Access Data

IP addresses for Bastion nodes are visible in `<cluster_name>.info` file.
User can access to Bastion/gateway node using:

```$xslt
ssh -i /pathtoprivatekey -o ProxyCommand='nc -X 5 -x myproxy.com:1080 %h %p' <external-user>@<ip-gateway>
```

or without proxy:

```$xslt
ssh -i /pathtoprivatekey <external-user>@<ip-gateway>
```
#### Definition data
During cluster creation all data related with terraform definition and state is stored in `.workspace/terraform/<cluster-name>` directory.
