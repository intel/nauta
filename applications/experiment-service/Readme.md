# DLS4E Experiment Service


## Requirements
1. Go 1.10.2 https://golang.org/doc/install
1. dep v.0.4.1 https://github.com/golang/dep


## Setup project
If `$GOPATH` is not set, Go will use following location as the default one: `$HOME/go`
This project should be placed under (only non-capitals letters - issue in
 [code-generator](https://github.com/kubernetes/code-generator/issues/20#issuecomment-412686432)) `$HOME/go/src/github.com/nervanasystems/carbon`


## Development
For more info about preoject structure check [Knowledge](#knowledge) section

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
1. Open port Forwarding: `./hack/registry.sh`
1. Build new image: `docker build . -t 127.0.0.1:31655/experiment-service`
1. Push to remote docker registry: `docker push 127.0.0.1:31655/experiment-service`
1. Change image address in deployment to `image: 127.0.0.1:31655/experiment-service`: 
    ```
    kubectl edit -n=dls4e deployment dls4enterprise-experiment-service
    ```
1. Test it!

## Test
To verify if experiment-service works correctly we can try to add some exampled run: `kubectl create -f sample/run.yaml`


## Knowledge
Project was prepared based on [sample-apiserver](https://github.com/kubernetes/sample-apiserver) and
[sample-controller](https://github.com/kubernetes/sample-controller) which shows in practise 
how to use following kubernetes libraries:
1. [apiserver](https://github.com/kubernetes/apiserver)
1. [code-generator](https://github.com/kubernetes/code-generator)

### Significant files
1. Model: [pkg/apis/aggregator/v1/types.go](pkg/apis/aggregator/v1/types.go)
    More info how to prepare models and how to use **tags**:
    1.  https://blog.openshift.com/kubernetes-deep-dive-code-generation-customresources/
    1.  https://github.com/kubernetes/community/blob/master/contributors/devel/generating-clientset.md
1. Controller: [cmd/controller](cmd/controller)
1. ApiServer [cmd/apiserver](cmd/apiserver)
1. Informers (generated): [pkg/client/informers/externalversions/aggregator/v1](pkg/client/informers/externalversions/aggregator/v1)
1. All generated code like [client](pkg/client) or `zz_generated.***.go` files were created by [update-codegen.sh](hack/update-codegen.sh) script

### Enable paging (chunking) for List operations
To enable Paging, flag `Paging` has to be enabled in [storagebackend.Config](https://github.com/kubernetes/apiserver/blob/master/pkg/storage/storagebackend/config.go).
In our code we made it in [NewRunServerOptions](https://github.com/NervanaSystems/carbon/blob/develop/applications/experiment-service/cmd/apiserver/start.go#L46) method.

Usage ([doc](https://github.com/kubernetes/kubernetes/commit/35ffb5c6cf70974c0a571cd1ebdc72ad8d0f8332)):
1. `https://http://127.0.0.1:8080/apis/aggregator/v1/namespaces/zenek/runs?limit=1`
1. `https://http://127.0.0.1:8080/apis/aggregator/v1/namespaces/zenek/runs?continue=a3ViZS1wdWJsaWM`

### Enable and configure filter feature

#### Field selectors
Field selectors let you select Kubernetes resources based on the value of one or more resource fields.

To enable filtering, proper `FieldLabelConversionFunc` method has to be register on schema init. We made it in [register.go](pkg/apis/aggregator/v1/register.go#L43).
Next proper `fields.Set` has to be passed to `GetAttrs` method in [strategy.go](pkg/registry/aggregator/run/strategy.go#L47).

Usage ([doc](https://kubernetes.io/docs/concepts/overview/working-with-objects/field-selectors/)):
1. Filter by state: `?fieldSelector=spec.state=RUNNING`
1. Filter by specific metric: `?fieldSelector=spec.metrics.accuracy=52`
1. Chained selectors: `?fieldSelector=spec.metrics.accuracy=52,spec.state=RUNNING`

e.g: `https://http://127.0.0.1:8080/apis/aggregator/v1/namespaces/zenek/runs?fieldSelector=spec.metrics.accuracy=52&fieldSelector=spec.state=RUNNING`

#### Labels selectors
Labels selector are more complex and let among others for set search: `my_label in (OK, BAD)`

Usage ([doc](https://kubernetes.io/docs/concepts/overview/working-with-objects/labels/#api)):
1. Filter by name: `?labelSelector=name=test-1`
1. Filter using set (`my_label in (OK, BAD)`): `?labelSelector=my_label%20in%20(OK%2C%20BAD)%0A`

e.g. `https://http://127.0.0.1:8080/apis/aggregator/v1/namespaces/zenek/runs?labelSelector=name=test-1`
