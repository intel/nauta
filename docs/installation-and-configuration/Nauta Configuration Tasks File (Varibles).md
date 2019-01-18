# Configuration Tasks
Nauta configuration tasks include configuring the files, proxies, and DNS servers and other configuration tasks. 

**Note:** In the examples shown, Green indicates parameter name and Blue indicates exemplary parameter value.

## Example Configuration File and Options

### Proxy Configuration

**Description:** This is the Proxy setting for internal applications and, this proxy configuration is a dictionary and DNS server is list.

**Default value:** {}

- **Note:** Instances of curly brackets { } indicates that this is an empty dictionary.

```yaml
proxy:
  http_proxy: http://<your proxy address and port>
  ftp_proxy: http://<your proxy address and port>
  https_proxy: http://<your proxy address and port>
  no_proxy: <localhost, any other addresses>, 10.0.0.1,localhost,.nauta
  HTTP_PROXY: http://proxy-chain.intel.com:911
  FTP_PROXY: http://<your proxy address and port>
  HTTPS_PROXY: http://<your proxy address and port>
  NO_PROXY: .<localhost, any other addresses>, 10.0.0.1,localhost,.nauta
```
**Note:**  Proxy addresses should be replaced by a specific value by a client.

### dns_servers

**Description:** This is a list of DNS servers used for resolution: a max of three entries.

**Default value:** []

- **Note:** Instances of squares brackets [ ] indicates that this is an empty list. 

```yaml
dns_servers:
  - 10.102.60.20
  - 10.102.60.30
```

### dns_search_domains

**Description:** This is a domain used as part of a domain search list.

**Default value:** []

```yaml
dns_search_domains:
  - example.com
  ```

### domain

**Description:** This is the _Internal_ domain name.

**Default value:** nauta

```yaml
domain: nauta
```

### nodes_domain


**Description:** Internal subdomain for infrastructure. Full domain for an infrastructure is:

`<nodes_domain>.<domain>`

**Default value:** infra

**Note:**  The domain setting is for top domain. Together with nodes_domain it creates a full zone domain. For example: 

 **domain:** `nauta` 

 **nodes_domain:** `infra` 

This results in full domain: `infra.nauta`

```yaml
nodes_domain: lab007
```

**Note:** These IP addresses _should not_ conflict with Internal IP address ranges. 

### k8s_domain

**Description:** This is the Internal subdomain for Kubernetes resources. Full domain for infrastructure is: `<k8s_domain>.<domain>`

**Default value:** kubernetes

```yaml
k8s_domain: kubernetes
```

### kubernetes_pod_subnet

**Description:** This is the Network Range for Kubernetes pods.

**Default value:** 10.3.0.0/16

```yaml
kubernetes_pod_subnet: 10.3.0.0/16
```

### kubernetes_svc_subnet

**Description:** This is the Network Range for Kubernetes services.

**Default value:** 10.4.0.0/16

```yaml
kubernetes_svc_subnet: 10.4.0.0/16
```

### insecure_registries 

**Description:**  This is a list of insecure Docker registries added to configuration.

**Default value:** []

**Note:** This refers to Docker registries only. 

```yaml
insecure_registries: 
- my.company.registry:9876
```

### enabled_plugins 

**Description:** This is a list of enabled Yum* plugins.

**Default value:** []

```yaml
enabled_plugins:
  - presto
```

### disabled_plugins

**Description:** This is a list of disabled Yum plugins.

**Default value:** []

```yaml
disabled_plugins:
  - presto
```

### use_system_enabled_plugins

**Description:** This defines if Yum should use system-enabled plugins.

**Default value:** False

```yaml
use_system_enabled_plugins: False
```

### enabled_repos 

**Description:** This is a list of enabled repositories, and is used for external dependencies installation.

**Default value:** []

```yaml
enabled_repos:
  - rhel
```

### disabled_repos 

**Description:** This is a list of disabled repositories, and is used for external dependencies installation.

**Default value:** []

```yaml
disabled_repos:
  - rhel
```

### use_system_enabled_repos 

**Description:** This defines if the default system repositories should be enabled in external dependencies installation.

Default value: True

```yaml
use_system_enabled_repos: True
```

### input_nfs

**Description:** Definition of input NFS mounts for Samba.

By default, internal NFS provisioner is used.

**Default value:** {}

**Fields**
- **path:** NFS path to mount

- **server:** NFS server

### output_nfs


**Description:** Definition of input NFS mounts for Samba. By default, internal NFS provisioner is used.


 By default, internal NFS provisioner is used.

**Default value:** {}

**Fields**
- **path:** NFS path to mount
- **server:** NFS server

```yaml
nauta_configuration:
  input_nfs:
    path: "{{ nfs_base_path }}/input"
    server: "{{ nfs_server }}"
  output_nfs:
    path: "{{ nfs_base_path }}/output"
    server: "{{ nfs_server }}"
```

### Features (Optional) 

**Description:** This is a map of enabled features and more information can be found under: [Features and Network File System](J1_Features_and_Network_File_System.md)

```yaml
features:
  nfs: True
  redsocks: True
```

### Features: Network File System (NFS) and Redsocks 

Nauta features include NFS and Redsocks. To configure either NFS or Redsocks, you _must_ enable either feature and configure feature options.

### Features List 

**NFS:** default: enabled
**Redsocks:** default: disabled

### How to Enable Features 

Additional features can be enabled using features object in configuration, as shown below.

```yaml
features:
    redsocks: False
```

### Feature Plugin Configuration 

Configuration for features should be placed under `features_config'.

```yaml
features:
  redsocks: True
features_config:
  redsocks:
    IP: 10.217.247.236
    Port: 1080
```
### Features: Network File System (NFS) and Redsocks  

Nauta features include NFS and Redsocks*.  To configure either NFS or Redsocks, you must enable either feature and configure feature options. 

### Network File System Overview

The Network File System, or NFS allows a system to share directories and files with others over a network. The advantage of using NFS is that end-users as well as programs can access files on remote systems in the same way as local files. In addition, NFS uses less disk space, as it can be store data on a single machine while remaining accessible to others over a network.
Redsocks Configuration 
Redsocks configuration is an optional part of the installer; therefore, it might apply only to limited number of installations.

### Redsocks Configuration Parameters 

### IP 

**Description:** This is the IP address of Socks5 proxy.

**Required:** True

### Port 

**Description:** This is the port address of Socks5 proxy. 

**Required:** True

### Interfaces 

**Description:** Comma-separated list of interfaces from which traffic should be managed by RedSocks.

**Required:** False 

**Default:** cni0

