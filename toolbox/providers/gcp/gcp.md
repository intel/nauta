# Nauta on Google Cloud* Platform: Getting Started

The Nauta platform has many different deployment options and customization capabilities. To make it simple for a typical use case, this guide uses simplified deployment procedures and relays on default parameters.

If you prefer to use local machines, adjust advanced options or cluster details, refer to the [Advanced Nauta Installation Guide](gcp-advanced.md) for more information.

## Introduction

This guide assumes that installation occurs on a dedicated node, created on the Google Cloud Platform. In this guide, it is referred to as the _Platform Installation Node_ and the majority of the steps involved are executed on this machine.

**Note:** The platform is compiled from the source code during this procedure; therefore, it may take some time. The typical installation time is roughly 2 hours (or slightly longer). Binary installation is described in advanced guide. Refer to the [Advanced Nauta Installation Guide](gcp-advanced.md) for more information

### Google Cloud Platform Console: Creating a Platform Installation Node Instance

To install the platform, you will need a machine created on Google Cloud Platform, using Google's web interface (as shown in the example image below), Google Cloud Platform Console.
 
Create machine with the following specifications:

- **Machine type:** At least 1 vCPU, 3.75 GB memory (this can be a small machine)

- **Boot disk:** Ubuntu 18.04 LTS with 150 GB standard disk

- **Other options:** These can stay in their default state

**Note:** You _must_ have remote access configured to be able to remotely access this machine over SSH. This is _out of scope_ of this tutorial. Contact your administrator or refer to the Google Cloud Platform documentation for support.

![alt text](screenshots/x-screenshot-create-platform-installation-node.png "Create Platform Installation Node on Google Cloud Platform")

### Platform Installation Node: Login via SSH

Platform Installation Node details, including its external IP address and in-browser connectivity can be found on the instances list in the Google Cloud Platform Console (shown in the example image below):

![alt text](screenshots/x-screenshot-access-platform-installation-node.png "Access Platform Installation Node on Google Cloud Platform")

Use either in-browser connectivity (by clicking _SSH_ option) or your own SSH client, with external IP address listed (keep in mind that you may need to configure proxy to access it).

### Platform Installation Node: Install Required Packages

```
sudo apt update && sudo apt install git make python3-pip python3-dev virtualenv unzip
echo -e "\n\n\n" | ssh-keygen -t rsa -N ""
```

**Note:** The SSH keys generated during this step will be used for the initial login to the platform after deployment.

### Platform Installation Node: Clone Nauta Repository

```
git clone https://github.com/IntelAI/nauta
cd nauta
echo 'export NAUTA_DIR=$HOME/nauta' >> ~/.bashrc
source ~/.bashrc
```

***From this point on, all operations described below should be made on Platform Installation Node. All paths are connected with a cloned repository*** 

### Google Cloud Platform Console: Create Service Account

Nauta deployment requires a subset of Google Cloud Platform permissions; those are represented by Service Account resource.

To create create a dedicated service account for Nauta deployment needs, follow the official Google Cloud Platform guide: https://cloud.google.com/iam/docs/creating-managing-service-accounts

**Note:** The service account has to be created to operate on user's project dedicated to running Nauta cluster. Refer to https://console.cloud.google.com/iam-admin/serviceaccounts?project=<project_name>) for more information.

A _Service Account_ should have `project-owner` priviliges and be ready to create gke cluster, vpc, virtual machines.

With the service account created, you will be able to download a JSON file with its details and save it. Data within _is required_ in the next step.

#### Platform Installation Node: Adjust Google Cloud Platform Service Account Config

Copy previously downloaded JSON configuration file (for service account) as `gcp-service-account.json` into the `$NAUTA_DIR/toolbox/providers/gcp` directory. 

## Platform Installation Node: Adjust Cluster Details

```$xslt
gcp:
  region: "us-west1"               # GCP target data center
  zone: "us-west1-a"               # GCP target data center zone
  external_username: "nauta"       # safe default
  internal_username: "nauta"       # safe default
  gateway_type: "n1-standard-4"    # safe default
  testnode_type: "n1-standard-4"   # (do not edit)
  nfs_type: "n1-standard-2"        # safe default
  nfs_disk_size: "400"             # size in GB, safe default
  pool_type: "n1-standard-16"      # Worker GCP Node size, adjust as needed
  pool_size: "1"                   # Number of Worker GCP Nodes
  pool_min_cpu_platform: "Intel Skylake" # CPU Architecture, safe default
  generate_test_node: False        # (do not edit)
  testnode_image: ""               # (do not edit)
``` 

### Platform Installation Node: Deployment: Cluster Creation

```
cd $NAUTA_DIR/toolbox/providers/gcp/
./gcp.sh --operation create --compile-platform-on-cloud true
```

Should you want to create multiple Nauta deployments on a single account, pass extra parameter `--k8s-cluster NAME` to `gcp.sh`, with different names for every Nauta deployment.

### Platform Installation Node: Post Installation Steps

#### Cluster Creation

Executing the following command, _Cluster Creation_ creates a file containing details of your fresh Nauta cluster and save them in the file:

```
cat $NAUTA_DIR/toolbox/providers/gcp/<k8s-cluster>.info
```
Where `k8s-cluster` is the name of cluster provided to `--k8s-cluster` flag or `nauta` if the flag was not provided.

#### Nauta Cluster Bastion Node

Executing the following command, to connect via ssh to the Nauta Cluster Bastion Node:

```
ssh nauta@<ip-gateway-from-nauta.info>
```

Bastion node is accessible from the Internet. Adjust authorized keys and add your own to the bastion host to `~/.ssh/authorized_keys`.

When on a Nauta Cluster Bastion Node, untar `~/artifacts/nctl-1.0.0-<timestamp>-linux.tar.gz` file which gives you a possibility to use `nctl` tool. Refer to [Nauta Getting Started document](../../../docs/user-guide/actions/getting_started.md) for further information on `nctl`. 

Your first step after veryfing that `nctl` works correctly should be a regular user creation and switching to it to perform other operations supported by Nauta.  

### Next Steps

When connected via ssh to Nauta Cluster Bastion Node, you can use `nctl` command to manage cluster.

### Platform Installation Node: Cluster Removal

When you need to delete a cluster you created, you can issue the following command when being signed in to the Platform Installation Node:

```
cd $NAUTA_DIR/toolbox/providers/gcp/
./gcp.sh --operation destroy
```
