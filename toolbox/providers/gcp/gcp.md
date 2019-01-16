# Google Cloud Platform installation guide

## Overall cluster architecture
GCP Nauta Kubernetes instance consists of several parts:
- gateway - bastion host to access to cluster
- test node (optional) - bastion host with test software to do continuous tests
- nfs server - internal server with nfs based resources
- gke cluster - kubernetes cluster.

Plase refer to [terraform definition files](terraform/tasks/templates/main) to see detailed configuration (networking,
resources, etc.)

## Prerequisities
Installer process uses [Terraform](https://www.terraform.io/) to create resources on Google Cloud Platform.
Service account has to be created to operate on user's project.

The following resources MUST be defined before installation

###GCP access config
File `gcp-service-account.yml` present in `toolbox/providers/gcp` directory MUST be properly filled wih access data.
```$xslt
gcp_service_account:
  type: "service_account"
  project_id: "<fill-with-proper-data>"
  private_key_id: "<fill-with-proper-data>"
  private_key: "<fill-with-proper-data>"
  client_email: "<fill-with-proper-data>"
  client_id: "<fill-with-proper-data>"
  auth_uri: "https://accounts.google.com/o/oauth2/auth"
  token_uri: "https://accounts.google.com/o/oauth2/token"
  auth_provider_x509_cert_url: "https://www.googleapis.com/oauth2/v1/certs"
  client_x509_cert_url: "<fill-with-proper-data>"
``` 

###Connectivity configuration
During installation several operations on cluster is done using ssh connectivity. Network configuration is stored
in `toolbox/config.yml` file.

####No proxy configuration
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

####Configuration with proxy
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

For specific ssh connectivity please refer to `ssh`/`scp` manuals.

## Basic configuration
Kubernetes cluster resources and connectivity servers can be defined in yaml file (i.e. `gcp-config.yml`)
```$xslt
gcp:
  gke_project: "myprojectname"
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

- `gke-project`, `region` and `zone` - typical GCP parameters
- `external-username` - username to connect to bastion (gateway) server
- `gateway_type` - node type (see server types accessible in region and zone defined above) for bastion (gateway) server
- `testnode_type` - node type (see server types accessible in region and zone defined above) for test server
- `nfs_type` - node type (see server types accessible in region and zone defined above) for internal nfs server
- `internal_username` - username for internal ssh connectivity
- `pool_type` - node type (see server types accessible in region and zone defined above) for gke cluster resources
- `pool_size` - gke cluster servers quantity
- `generate_test_node` `[True|False]` - boolean flag to decide if test node will be created
- `test_node_image` - name of the image accessible in the gcp project to create test node with pre-installed test software


## Installation process
### Installer options
```Usage:
gcp.sh [options]
```
Options:
- `operation` `[create,destroy,]` - Operation to perform. If empty only installation attempt will be perform.
- `k8s-cluster` - [nauta] - Kubernetes cluster name.
- `gcp-config` `[pwd/gcp-config.yml]` - Config file with cluster parametrs (resources, access).
- `external-public-key` `[~/.ssh/id_rsa.pub]` - Path to file with public key accepted by cluster gateway to connect.
- `external-key` `[~/.ssh/id_rsa]` -Path to file with private key used to connect to cluster gateway.
- `s3-url` Url to s3 bucket to store terraform cluster state. By default local file will be used.
- `s3-secret-key` Secret key to s3 bucket.
- `s3-access-key` Secret key to s3 bucket.
- `network-settings` `config.yml` - File name with network settings in provider directory.
- `compile-platform-on-cloud` [`false|true]` - If true plagform packages will be create on bastion/gatway node.

### Use cases
- #### Destroy cluster
```$xslt
./gcp.sh --k8s-cluster cicd-carbon-b --operation destroy
```

- #### Create cluster
```$xslt
./gcp.sh --k8s-cluster cicd-carbon-b --operation create \
                                     --gcp-config `pwd`/gcp-config.yml
```

- #### Create cluster and install platform
```$xslt
./gcp.sh --k8s-cluster cicd-carbon-b --operation create \
                                     --gcp-config `pwd`/gcp-config.yml \
                                     --install-file /opt/project-data/repository/releases/nauta/nauta-1.0.0-latest.tar.gz
```

### Installer output
#### Access data
Ip addresses for bastion nodes are visible in `<cluster_name>.info` file.
User can access to bastion/gateway node using:

```$xslt
ssh -i /pathtoprivatekey -o ProxyCommand='nc -X 5 -x myproxy.com:1080 %h %p' <external-user>@<ip-gateway>
```

or without proxy:

```$xslt
ssh -i /pathtoprivatekey <external-user>@<ip-gateway>
```
#### Definition data
During cluster creation all data related with terraform definition and state is stored in `.workspace/terraform/<cluster-name>` directory.
