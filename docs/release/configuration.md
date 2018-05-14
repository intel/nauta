# Configuration

## Configuration file

## Configuration options

### proxy

Description: Proxy setting for internal applications
Default value: []

Example:
```yaml
proxy:
  http_proxy: http://proxy-chain.intel.com:911
  https_proxy: http://proxy-chain.intel.com:912
  no_proxy: .intel.com,127.0.0.1,localhost,.dlse

dns_servers:
  - 10.102.60.20
  - 10.102.60.30
```

### dns_servers

Description: List of DNS servers used to resolution - max 3 entries
Default value: []

Example:
```yaml
dns_servers:
  - 10.102.60.20
  - 10.102.60.30
```

### dns_search_domains

Description: List of DNS search domains - max 3 entries
Default value: []

Example:
```yaml
dns_search_domains:
  - intel.com
```

### domain

Description: Internal domain name
Default value: dlse

Example:
```yaml
domain: company
```

### nodes_domain


Description: Internal subdomain for infrastructure. Full domain for infrastructure will be `<nodes_domain>.<domain>`
Default value: infra

Example:
```yaml
nodes_domain: lab007
```

### k8s_domain


Description: Internal subdomain for kubernetes resources. Full domain for infrastructure will be `<k8s_domain>.<domain>`
Default value: kubernetes

Example:
```yaml
k8s_domain: kubernetes-001
```

### kubernetes_pod_subnet


Description: Network range for kubernetes pods
Default value: 10.3.0.0/16

Example:
```yaml
kubernetes_pod_subnet: 10.128.0.0/16
```

### kubernetes_svc_subnet


Description: Network range for kubernetes services
Default value: 10.4.0.0/16

Example:
```yaml
kubernetes_pod_subnet: 10.129.0.0/16
```

### insecure_registries


Description: List of insecure registries added to configuration
Default value: []

Example:
```yaml
insecure_registries:
  - my.company.registry:9876
```


### dls4e_configuration


Description: Definition of DLS4E Applications configuration
Default value: {}

#### input_nfs


Description: Definition of input NFS mounts for samba. By default internal NFS provisioner will be used
Default value: {}

Fields:
  - path: NFS path to mount
  - server: NFS server

#### output_nfs


Description: Definition of output NFS mounts for samba. By default internal NFS provisioner will be used
Default value: {}

Fields:
  - path: NFS path to mount
  - server: NFS server
  

Example:
```yaml
dls4e_configuration:
  input_nfs:
    path: /exports/test/input
    server: 10.91.120.230
  output_nfs:
    path: /exports/test/output
    server: 10.91.120.230
```

## Examples

Examples can be found on [Configuration examples directory](examples/configuration)
