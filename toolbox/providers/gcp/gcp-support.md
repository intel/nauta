# Nauta on Google Cloud Platform - Support

Typically environment after creation has to be maintained. Some use cases were described 
and maintenance scripts were written.

##Prepare Nauta for users

Just after installation gateway and Nauta Platform have only on user: administrator (called typically nauta).

Shell user on gateway has administrator privileges and sudoers sudo access.
Nauta administrator has permissions to manage cluster.

Users can be created using `gcp-users.sh` script.

```Usage:
gcp-users.sh [options]
```
Options:
- `k8s-cluster` - [nauta] - Kubernetes cluster name.
- `gcp-config` `[pwd/gcp-config.yml]` - Config file with cluster parametrs (resources, access).
- `external-key` `[~/.ssh/id_rsa]` -Path to file with private key used to connect to cluster gateway.
- `network-settings` `config.yml` - File name with network settings in provider directory.
- `gateway-users` `gateway-users.yml` - File name with users' configuration.

Sample `gateway-users.yml`:
```
gateway_users:
  nautaoperator:
    groups:
      - docker
    # yamllint disable-line rule:line-length
    authorized_key: "ssh-rsa dummykey myaccount@mycompany.com"
```
### Use cases
#### Create platform users
```$xslt
./gcp-user.sh --k8s-cluster nauta-cluster --gateway-users <path_to_config_file>
```

### Results
Routine prepares environment with the following steps:
- installs `nctl` binary in system wide visible directory (`/usr/local/bin`)
- creates ssh users on gateway node
- fills `.authorized_keys` with access key defined in config
- copies fresh config files from client to users' directories
- creates nauta users
- copies access config for users to their `~/.kube` directories.

#### Create platform users from within the gateway
Clone repository and run:
```$xslt
make create-gateway-users ENV_GATEWAY_USERS=`pwd`/toolbox/support/gateway-users/gateway-users.yml
```
***Please note, that `ENV_GATEWAY_USERS` MUST be absolute path to the file.***