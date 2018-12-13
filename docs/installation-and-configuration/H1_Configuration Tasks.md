# Configuration Tasks
The Intel DL Studio configuration tasks include configuring the files, proxies, and DNS servers and other configuration tasks. 

**Note:** In the examples shown, Green indicates parameter name; and, Blue indicates exemplary parameter value.

## Configuration File and Options

### Proxy Configuration

**Description:** This is the _proxy setting_ for internal applications.

**Default value:** {}

**Example:**
```yaml
proxy:
http_proxy: <your proxy address and port>
https_proxy: <your proxy address and port>
no_proxy: .<localhost, any other addresses>,10.0.0.1,localhost,.dlse
```
**Note:**  Proxy address should be replaced by a specific value by a client.

### dns_servers

**Description:** This is a list of DNS servers used for resolution: a max of three (3) entries.

**Default value:** []

**Example:**
```yaml
dns_servers:
  - 8.8.8.8
  - 8.8.4.4
```

### dns_search_domains

**Description:** This is a domain used as part of a domain search list.

**Default value:** []

**Example:**
```yaml
dns_search_domains:
  - example.com
  - example.org
```

### domain

**Description:** This is the Internal domain name.

**Default value:** dlse

**Example:**
```yaml
domain: company
```

### nodes_domain


**Description:** Internal subdomain for infrastructure. Full domain for an infrastructure is: `<nodes_domain>.<domain>`

**Default value:** infra

**Note:**  The domain setting is for top domain. Together with nodes_domain it creates a full zone domain. For example: 

  domain: `dlse` 

  nodes_domain: `infra` 

This results in full domain: `infra.dlse`

**Example:**
```yaml
nodes_domain: lab007
```

**Note:** These IP addresses _should not_ conflict with Internal IP address ranges. 

### k8s_domain


**Description:** This is the Internal_ subdomain for Kubernetes resources. Full domain for infrastructure is: `<k8s_domain>.<domain>`

**Default value:** kubernetes

**Example:**
```yaml
k8s_domain: kubernetes-001
```

### kubernetes_pod_subnet


**Description:** This is the Network Range for Kubernetes pods.

**Default value:** 10.3.0.0/16

**Example:**
```yaml
kubernetes_pod_subnet: 10.128.0.0/16
```

### kubernetes_svc_subnet


**Description:** This is the Network Range for Kubernetes services.

**Default value:** 10.4.0.0/16

**Example:**
```yaml
kubernetes_svc_subnet: 10.129.0.0/16
```

### insecure_registries


**Description:**  This is a list of insecure docker registries added to configuration.

**Default value:** []

**Example:**
```yaml
insecure_registries:
  - my.company.registry:9876
```

### enabled_plugins

**Description:** This is a list of enabled Yum* plugins.

**Default value:** []

**Example:**
```yaml
enabled_plugins:
  - presto
```

### disabled_plugins

**Description:** This is a list of disabled _Yum plugins_.

**Default value:** []

**Example:**
```yaml
disabled_plugins:
  - presto
```

### use_system_enabled_plugins

**Description:** This defines if Yum should use system-enabled plugins.

**Default value:** False

**Example:**
```yaml
use_system_enabled_plugins: True
```

### enabled_repos

**Description:** This is a list of enabled repositories, and is used for external dependencies installation.

**Default value:** []

**Example:**
```yaml
enabled_repos:
  - rhel
```

### disabled_repos

**Description:** This is a list of disabled repositories, and is used for external dependencies installation.

**Default value:** []

**Example:**
```yaml
disabled_repos:
  - rhel
```

### use_system_enabled_repos

**Description:** This defines if the default system repositories should be enabled in external dependencies installation.

Default value: True

**Example:**
```yaml
use_system_enabled_repos: True
```


### dls4e_configuration


**Description:** Definition of Intel DL Studio Applications configuration.

**Default value:** {}

#### input_nfs


**Description:** Definition of input NFS mounts for samba.

By default, internal NFS provisioner is used.

**Default value:** {}

### Fields
  - path: NFS path to mount
  - server: NFS server

#### output_nfs


**Description:** This is the definition of output NFS mounts for Samba.


 By default, internal NFS provisioner is used.

**Default value:** {}

### Fields
  **path:** NFS path to mount
  **server:** NFS server

### Example
```yaml
dls4e_configuration:
  input_nfs:
    path: /exports/test/input
    server: 10.0.0.1
  output_nfs:
    path: /exports/test/output
    server: 10.0.0.1
```

### Features

**Description:** This is a map of enabled features and more information can be found under: [Features and Network File System](J1_Features_and_Network_File_System.md)

### Example
```
features:
  nfs: True
  redsocks: True
```
## Example
```
proxy:
  http_proxy: http://proxy-chain.intel.com:911
  https_proxy: http://proxy-chain.intel.com:912
  no_proxy: .intel.com,127.0.0.1,localhost,.dlse

dns_servers:
  - 10.102.60.20
  - 10.102.60.30

dls4e_configuration:
  input_nfs:
    path: /exports/test/input
    server: 10.91.120.230
  output_nfs:
    path: /exports/test/output
    server: 10.91.120.230
```

