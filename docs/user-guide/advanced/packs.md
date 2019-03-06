# Controlling Packs Parameters

### Pack Definition 

The packs are located in the _nctl_config_ folder. Navigate to _.draft/packs/https-github.com-Azure-draft/packs_ folder to list existing packs.

The default pack used by _nctl_ client is _tf-training-tfjob_. The pack consist of the parts:

* docker image specification _Dockerfile_ 
* helm deployment _charts_ folder

All the pack parameters that can be controlled by _nctl_ are defined in _charts/values.yml_ file.

Example _values.yaml_ file taken from _multinode-tf-training-tfjob_ pack:

	# Default values for charts.
	# This is a YAML-formatted file.
	# Declare variables to be passed into your templates.
	
	TensorBoardPort: 8888
	TensorIPythonPort: 6006
	
	commandline:
	  args:
	    {% for arg in NAUTA.CommandLine %}
	    - {{ arg }}
	    {% endfor %}
	
	image:
	  pullPolicy: IfNotPresent
	  clusterRepository: {{ NAUTA.ExperimentImage }}
	
	service:
	  type: ClusterIP
	
	worker_resources:
	  requests:
	    cpu: 76
	    memory: 240Gi
	  limits:
	    cpu: 76
	    memory: 240Gi
	
	worker_cpu: null
	worker_memory: null
	
	ps_resources:
	  requests:
	    cpu: 76
	    memory: 240Gi
	  limits:
	    cpu: 76
	    memory: 240Gi
	
	ps_cpu: null
	ps_memory: null
	
	sidecar_resources:
	  requests:
	    cpu: 0.01
	    memory: 1Gi
	
	sidecar_cpu: null
	sidecar_memory: null
	
	
	experimentName: {{ NAUTA.ExperimentName }} 
	registryPort: {{ NAUTA.RegistryPort }}
	
	workersCount: 3
	psSidecarLoggingLevel: "WARNING"
	pServersCount: 1


    
### Modifying Values

The values can be modified directly by editing the _values.yml_ file or by providing _-p_, _--pack_param_ parameter to the selected _nctl_ commands:

 * _nctl experiment submit_
 * _nctl experiment interact_
 
The _-p_ parameter can be provided multiple times. Format specification:

 * 'key value' or 'key.subkey.subkey2 value'
 * for lists: 'key "['val1', 'val2']"'
 * for maps: 'key "{'a': 'b'}"'
 
#### Example

    nctl experiment submit multinode.py -t multinode-tf-training-tfjob -p workersCount 12 -p pServersCount 1

### Experiment Resources

_nctl_ is using by default following resource limits and requests for each built-in template:

| Template      | CPU   request | CPU limit | Memory request | Memory limit | Physical CPU cores request
| --- | --- | --- | --- | --- | --- |
| jupyter       | 38 | 38 | 120Gi | 120Gi | - |
| jupyter-py2   | 38 | 38 | 120Gi | 120Gi | - |
| multinode-tf-training-horovod | 76 | 76 | 240Gi | 240Gi | 20 |
| multinode-tf-training-horovod-py2 | 76 | 76 | 240Gi | 240Gi | 20 |
| multinode-tf-training-tfjob | 76 | 76 | 240Gi | 240Gi | - |
| multinode-tf-training-tfjob-py2 | 76 | 76 | 240Gi | 240Gi | - |
| tf-inference-batch | 38 | 38 | 120Gi | 120Gi | - |
| tf-inference-stream | 38 | 38 | 120Gi | 120Gi | - |
| tf-training-tfjob | 38 | 38 | 120Gi | 120Gi | - |
| tf-training-tfjob-py2 | 38 | 38 | 120Gi | 120Gi | - |

It is recommended to keep requests and limits on the same values. Also requested limits never should be bigger than resources available on node.

**Note:** You can use `cpu` and `memory` pack parameters when you want to change both requests and limits using the following command:
```
nctl experiment submit multinode.py -p cpu 2 -p memory 4Gi
```
Will submit an experiment with CPU requests and limits set to 2, and memory requests and limits set to 4Gi.

To change these defaults, following parameters should be adjusted (using methods described in Modifying values section):

| Template      | Resource parameters |
| --- | --- | 
| jupyter       | - resources.requests.cpu<br> - resources.requests.memory<br> - resources.limits.cpu<br> - resources.limits.memory |
| jupyter-py2       | - resources.requests.cpu<br> - resources.requests.memory<br> - resources.limits.cpu<br> -  resources.limits.memory |
| multinode-tf-training-horovod | - resources.requests.cpu<br> - resources.requests.memory<br> - resources.limits.cpu<br> - resources.limits.memory<br> - cpus<br> - processesPerNode |
| multinode-tf-training-horovod-py2 | - resources.requests.cpu<br> - resources.requests.memory<br> - resources.limits.cpu<br> - resources.limits.memory<br> - cpus<br> - processesPerNode |
| multinode-tf-training-tfjob | - worker_resources.requests.cpu<br> - worker_resources.requests.memory<br> - worker_resources.limits.cpu<br> - worker_resources.limits.memory<br> - ps_resources.requests.cpu<br> - ps_resources.requests.memory<br> - ps_resources.limits.cpu<br> - ps_resources.limits.memory |
| multinode-tf-training-tfjob-py2 | - resources.requests.cpu<br> - resources.requests.memory<br> - resources.limits.cpu<br> - resources.limits.memory <br> - ps_resources.requests.cpu<br> - ps_resources.requests.memory<br> - ps_resources.limits.cpu<br> - ps_resources.limits.memory |
| tf-inference-batch | - resources.requests.cpu<br> - resources.requests.memory<br> - resources.limits.cpu<br> - resources.limits.memory |
| tf-inference-stream | - resources.requests.cpu<br> - resources.requests.memory<br> - resources.limits.cpu<br> - resources.limits.memory |
| tf-training-tfjob | - resources.requests.cpu<br> - resources.requests.memory<br> - resources.limits.cpu<br> - resources.limits.memory |
| tf-training-tfjob-py2 | - resources.requests.cpu<br> - resources.requests.memory<br> - resources.limits.cpu<br> - resources.limits.memory |



