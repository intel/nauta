# Kubernetes features

User (Data Scientist) can easily and flexible manage his kubernetes cluster by adding and
removing features prepared by DL Enterprise team..

Kubernetes features can be installed by calling specific `make` routine from root repository
directory.

Feature installation is based on `helm` package and charts.

## Prerequisities

User environment has to fill the following requirements
- `kubectl` and `helm` packages have to be installed
- Kubernetes config file has to be prepared and accessible. User has to have the permissions
according to requested operations. In case of any problem please contact with cluster administrator.
- Kubernetes endpoint connectivity has to be properly set. If applicable os environment variables
`http_proxy` and `no_proxy` have to be set. All routines use these values to manage network traffic.

Features installer checks if `tiller` is installed of cluster. If not installer deploys it on cluster.
 
## Feature installation
To install kubernetes feature user has to call:
```aidl
make k8s-features-install K8S_FEATURES_LIST=[comma separated features list] K8S_CONFIG_LOCATION=[path to k8s config file] 
```

- `K8S_CONFIG_LOCATION` - parameter has to privide path to kubernetes cluster admin user config. This has to be
the same file as user uses with `kubectl` tool

- `K8S_FEATURES_LIST` - comma separated features list

## Feature uninstallation
To install kubernetes feature user has to call:
```aidl
make k8s-features-install K8S_FEATURES_LIST=[comma separated features list] K8S_CONFIG_LOCATION=[path to k8s config file] 
```

- `K8S_CONFIG_LOCATION` - parameter has to privide path to kubernetes cluster admin user config. This has to be
the same file as user uses with `kubectl` tool

- `K8S_FEATURES_LIST` - comma separated features list

## Features list
- `dummy` - Dummy feature to provide ability to check if all kubernetes components on client and server
are properly installed (i.e. `tiller` on )
- `docker-registry` - Private docker registry

## Features parametrization
Each feature can be parametrized using `values.yml` file present in specific feature directory. All
features are collected in [chart directory](/k8s-features/charts)