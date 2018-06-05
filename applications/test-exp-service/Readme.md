# DLS4E Experiment Service

## Setup
Install:
1. apiserver-builder v1.9-alpha.4: [info](https://github.com/kubernetes-incubator/apiserver-builder/blob/master/docs/installing.md)
1. Go 1.10.2 https://golang.org/doc/install

### Prepare Go project environment
If `$GOPATH` is not set, Go will use following location as the default one: `$HOME/go`
This project should be placed under (only non-capitals letters!) `$HOME/go/src/github.com/nervanasystems/carbon`

## Development

### Add new models
1. (already done) Init new APIService: `apiserver-boot init repo --domain aipg.intel.com`
1. (already done) Create new model: `apiserver-boot create group version resource --group aggregator --version v1 --kind Run`
1. (one-time only for downloaded project) Fetch vendor data: `apiserver-boot update vendor`
1. Update fields and methods in file: `pkg/apis/aggregator/v1/run_types.go`
1. Regenerate code: `apiserver-boot build executables`

### Update code
1. Make changes, ex. add new field
1. Regenerate code: `apiserver-boot build executables`
1. Commit

## Deployment

### Deploy on cluster
1. Setup Docker Registry:
    1. For local cluster:
        1. `kubectl create -f dev-local-cluster/pod-registry.yaml`
        1. `kubectl create -f dev-local-cluster/svc-registry.yaml`
        1. run port forwarding (FORWARDED_PORT == 5000): `kubectl port-forward docker-registry 32111:5000`
    1. For Sclab cluster:
        1. run port forwarding (RETURNS FORWARDER_PORT): `./dev-local-cluster/registry.sh`
    1. Set `FORWARDED_PORT` env in terminal: `export FORWARDED_PORT=XXXXX`
1. Build image: `apiserver-boot build container --image 127.0.0.1:31048/experiment-service`
1. Push image: `docker push 127.0.0.1:31048/experiment-service`
1. Prepare current cluster configuration:
    1. Remove current conf: `rm -Rf config/`
    1. [TEMPORARY SOLUTION] Install required kubernetes config: `kubectl create -f ./dev-local-cluster/auth.yaml`
    1. Generate new cluster conf: `apiserver-boot build config --name experiment-service --namespace dls4e --image 127.0.0.1:31048/experiment-service --service-account=exp-apiserver`
1. Prepare storage:
    1. for local Kubernetes from Docker on Mac `./dev-local-cluster/storage-docer-mac.yaml`
    1. for Sclab cluster: in `config/.apiserver.yaml` set `volume.beta.kubernetes.io/storage-class` value to: `dls4enterprise-k8s-platform-nfs`
1. Run (after call wait for `ETCD` and `experiment-service` Pods to be Ready): `kubectl apply -f config/apiserver.yaml`
1. Verify new APIService status: `kubectl describe apiservice v1.aggregator.aipg.intel.com`
1. Add exampled Run: `kubectl create -f sample/run.yaml`

### Update running image in cluster
1. Make changes in your code e.g.: add new field.
1. Build and push image again:
    1. `apiserver-boot build container --image 127.0.0.1:${FORWARDED_PORT}/experiment-service`
    1. `docker push 127.0.0.1:{FORWARDED_PORT}/experiment-service`
1. Kill `experiment-service` Pod to create new one from new image.
1. Test it!

## Problems and Tips:
1. If on Sclab you get the following error in experiment-service: `User "system:anonymous" cannot list  runs.aggregator.aipg.intel.com at the cluster scope`
Add cluster-admin role to your user: `kubectl create clusterrolebinding cluster-system-anonymous --clusterrole=exp-apiserver-role --user=system:anonymous`
1. If on Sclab you get the following error in experiment-service: `panic: cluster doesn't provide requestheader-client-ca-file` -> check [Jira issue](https://jira01.devtools.intel.com/browse/CAN-403)
