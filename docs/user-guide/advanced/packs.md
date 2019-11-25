# Controlling Packs Parameters

This section discusses the following main topics: 

 - [Pack Definition](#pack-definition)
 - [Modifying Values](#modifying-values)  
 - [Experiment Resources](#experiment-resources)

## Pack Definition 

The packs are located in the `nctl_config` folder. Navigate to `.draft/packs/https-github.com-Azure-draft/packs` folder to list existing packs. 

The default pack used by `nctl_ client` is `tf-training-single`. The pack consists of:

* Docker image specification _Dockerfile_ 

* Helm deployment _charts_ folder

All the pack parameters that can be controlled by _nctl_ are defined in the `charts/values.yaml` file.

The example `values.yaml` file (shown below) is taken from `tf-training-multi` pack:

```
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
```

## Modifying Values

The values can be modified directly by editing the `values.yml` file or by providing _-p_, _--pack_param_ parameter to the selected _nctl_ commands:

 * _nctl experiment submit_
 
 * _nctl experiment interact_
 
The _-p_ parameter can be provided multiple times.
Format specification:

 * 'key value' or 'key.subkey.subkey2 value'
 
 * for lists: 'key "['val1', 'val2']"'
 
 * for maps: 'key "{'a': 'b'}"'
 
### Example

`nctl experiment submit multinode.py -t tf-training-multi -p workersCount 12 -p pServersCount 1`

## Experiment Resources

_nctl_, by default uses the following resource limits and requests for each built-in template:

| Template      | CPU   Request | CPU Limit | Memory Request | Memory Limit | Physical CPU Cores Request
| --- | --- | --- | --- | --- | --- |
| jupyter       | 38 | 38 | 120Gi | 120Gi | - |
| tf-training-horovod | 76 | 76 | 240Gi | 240Gi | 20 |
| tf-training-multi | 76 | 76 | 240Gi | 240Gi | - |
| openvino-inference-batch | 38 | 38 | 120Gi | 120Gi | - |
| openvino-inference-stream | 38 | 38 | 120Gi | 120Gi | - |
| tf-inference-batch | 38 | 38 | 120Gi | 120Gi | - |
| tf-inference-stream | 38 | 38 | 120Gi | 120Gi | - |
| tf-training-single | 38 | 38 | 120Gi | 120Gi | - |

It is recommended to keep requests and limits on the same values. In addition, the requested limits never should be larger than resources available on node.

**Note:** You can use `cpu` and `memory` pack parameters when you want to change both requests and limits, for example, by using the following command:

```
nctl experiment submit multinode.py -p cpu 2 -p memory 4Gi
```
Will submit an experiment with CPU requests and limits set to 2, and memory requests and limits set to 4Gi.

To change these defaults, following parameters should be adjusted (using methods described in Modifying values section):

| Template      | Resource Parameters |
| --- | --- | 
| jupyter       | - resources.requests.cpu<br> - resources.requests.memory<br> - resources.limits.cpu<br> - resources.limits.memory |
| tf-training-horovod | - resources.requests.cpu<br> - resources.requests.memory<br> - resources.limits.cpu<br> - resources.limits.memory<br> - cpus<br> - processesPerNode |
| tf-training-multi | - worker_resources.requests.cpu<br> - worker_resources.requests.memory<br> - worker_resources.limits.cpu<br> - worker_resources.limits.memory<br> - ps_resources.requests.cpu<br> - ps_resources.requests.memory<br> - ps_resources.limits.cpu<br> - ps_resources.limits.memory |
| openvino-inference-batch | - resources.requests.cpu<br> - resources.requests.memory<br> - resources.limits.cpu<br> - resources.limits.memory |
| openvino-inference-stream | - resources.requests.cpu<br> - resources.requests.memory<br> - resources.limits.cpu<br> - resources.limits.memory |
| tf-inference-batch | - resources.requests.cpu<br> - resources.requests.memory<br> - resources.limits.cpu<br> - resources.limits.memory |
| tf-inference-stream | - resources.requests.cpu<br> - resources.requests.memory<br> - resources.limits.cpu<br> - resources.limits.memory |
| tf-training-single | - resources.requests.cpu<br> - resources.requests.memory<br> - resources.limits.cpu<br> - resources.limits.memory |

----------------------

## Return to Start of Document

* [README](../README.md)

----------------------


