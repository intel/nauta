# DLS4E Experiment Service


## Requirements
1. Go 1.10.2 https://golang.org/doc/install
1. dep v.0.4.1 https://github.com/golang/dep


## Setup project
If `$GOPATH` is not set, Go will use following location as the default one: `$HOME/go`
This project should be placed under (only non-capitals letters!) `$HOME/go/src/github.com/nervanasystems/carbon`


## Development

### Knowledge
Project was prepared based on [sample-apiserver](https://github.com/kubernetes/sample-apiserver) and
[sample-controller](https://github.com/kubernetes/sample-controller) which shows in practise 
how to use following kubernetes libraries:
1. [apiserver](https://github.com/kubernetes/apiserver)
1. [code-generator](https://github.com/kubernetes/code-generator)


[_example](_example) directory contains base code with models which was copied to [pkg](pkg)

All generated code like [client](pkg/client) or `zz_generated.***.go` files were created by [update-codegen.sh](hack/update-codegen.sh) script

#### Significant files
1. Model: [pkg/apis/aggregator/v1/types.go](pkg/apis/aggregator/v1/types.go)
1. Controller: [cmd/controller](cmd/controller)
1. ApiServer [cmd/apiserver](cmd/apiserver)
1. Informers (generated): [pkg/client/informers/externalversions/aggregator/v1](pkg/client/informers/externalversions/aggregator/v1)

### Update code
1. Made changes - e.g. add new field in `types.go`
1. Regenerate client files and build new binaries: `make build`
1. commit changes

### Update dependencies
1. Add new dependency in the go file import
1. call: `make dep_update`
1. commit changes


## Deployment

### Deploy on cluster
Current deployment configuration is handled by helm chart [here](../../dls4e-charts/experiment-service)

### Update running api-server in the cluster
1. Make changes in your code e.g.: add new field. Build it: `make build`
1. Open port Forwarding: `./dev-local-cluster/registry.sh`
1. Export returned port, e.g: `export FORWARDED_PORT=30887`
1. Build new image: `docker build . -t 127.0.0.1:30887/experiment-service`
1. Push to remote docker registry: `docker push 127.0.0.1:30887/experiment-service`
1. Change image address in deployment to `127.0.0.1:30887/experiment-service`: 
    ```
    kubectl edit -n=dls4e deployment dls4enterprise-experiment-service
    ```
1. Test it!

## Test
To verify if experiment-service works correctly we can try to add some exampled run: `kubectl create -f sample/run.yaml`