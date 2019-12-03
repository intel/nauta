# Troubleshooting

This section provides information related to Nauta-related issues, descriptions, and workarounds. Before contacting customer support or filing a ticket, refer to the information described in this section.  

This section discusses the following main topics: 

- [Jupyter Error 1](#jupyter-error-1-cause)  
- [Jupyter Error 2](#jupyter-error-2-cause)
- [Docker Error](#docker-error)
- [Removal of Docker Images](#removal-of-docker-images)  
- [User Management Error](#user-management-error)
- [Nauta Connection Error](#nauta-connection-error)
- [DNS Server has Changed or Missed in Installation Step](#dns-server-has-changed-or-missed-in-installation-step)
- [Insufficient Resources Causes Experiments Failures](#insufficient-resources-causes-experiments-failures)
- [Experiment Pods Stuck in Terminating State on Node Failure](#experiment-pods-stuck-in-terminating-state-on-node-failure)
- [A Multinode Horovod Experiment Receives a FAILED Status](#a-multinode-horovod-experiment-receives-a-failed-status)
- [Experiments Still in RUNNING State Even if they Finish with Success](#experiments-still-in-running-state-even-if-they-finish-with-success)

## Jupyter Error 1  

Saving a file causes the following error:
    
`Creating file failed. An error occurred while creating a new file.`

`Unexpected error while saving file: input/home/filename [Errno 2]`

`No such file or directory: /mnt/input/home/filename`
        
This error appears when a user tries to save a file in the `/input/home` folder, which is a read-only folder. 

### Jupyter Error 1 Workaround

In Jupyter, select the `/output/home` folder to correct this issue.

## Jupyter Error 2 

Closing the Jupyter notebook window in a Web browser causes experiments to stop executing. Continuing the same Jupyter session still shows the stopped experiment. 

### Jupyter Error 2 Workaround

Currently, there _is no_ workaround.

**Note:** This is a known issue in Jupyter (refer to: [keep notebook running after the browser tab closed #1647](https://github.com/jupyter/notebook/issues/1647) on GitHub for more information).

## Docker Error 

The Docker installation on the client machine takes up significant space and contains a large amount of container images.
Refer to [Official Docker Documentation](https://docs.docker.com) for more information. 

### Docker Error Workaround

Docker takes a conservative approach to cleaning up unused objects (often referred to as garbage collection), such as images, containers, volumes, and networks. These objects are generally _not_ removed unless you explicitly ask Docker to do so.

**Note:** Refer to the following information for detailed instructions on how to prune unused Docker images: [Prune unused Docker objects](https://docs.docker.com/config/pruning). 

## Removal of Docker Images 

Due to known errors in Docker Garbage Collector making automatic removal of Docker images is laborious and error-prone.

### Periodic Registry Clean Up

Before running the Docker Garbage Collector, the administrator should remove images that are no longer needed and perform Docker's registry cleanup periodically.

If there are too many images in registry it may negatively impact the submission of experiments: submitting of experiments works much slower than usual and eventually a user _is not_ able to submit an experiment. To prevent this, administrators should perform this cleanup periodically. 

### Removal of Docker Images Procedure and Workaround

1) Expose the internal Docker registry's API by exposing locally port 5000, exposed by `nauta-docker-registry service_ located` in the Nauta namespace. This can be done, for example by issuing the following command on a machine that has access to Nauta:`kubectl port-forward svc/nauta-docker-registry 5000 -n nauta`
     
2) Get a list of images stored in the internal registry by issuing the following command (it is assumed that port 5000 is exposed locally): curl http://localhost:5000/v2/_catalog 
     
 - For more information on Docker Images, refer to: [docker image ls](https://docs.docker.com/engine/reference/commandline/image_ls/)

3) From the list of images received in the previous step, choose the images that should be removed. For each chosen image, execute the following steps:  

      a) Get the list of tags belonging to the chosen image by issuing the following command (it is assumed that port 5000 is exposed locally): `curl http://localhost:5000/v2/<image_name>/tags/list` 
     
      b) For each tag, get a digest related to this tag:  
     ```
     curl --header "Accept: application/vnd.docker.distribution.manifest.v2+json" http://localhost:5000/v2/<image_name>/manifests/<tag>
     ``` 
     
     Digest is returned in a header of a response under the _Docker-Content-Digest_ key
      
      c) Remove the image from the registry by issuing the following command:  
     ```
     curl -X "DELETE" --header "Accept: application/vnd.docker.distribution.manifest.v2+json" http://localhost:5000/v2/<image_name>/manifests/<digest>
     ```
     
4) Run Docker Garbage Collector by issuing the following command:

     ```
     kubectl exec -it $(kubectl get --no-headers=true pods -l app=docker-registry -n nauta -o custom-columns=:metadata.name) -n nauta registry garbage-collect /etc/docker/registry/config.yml
     ```

5) Restart the system's Docker registry. It can be done by deleting the pod with the label: `nauta_app_name=docker-registry` 

   
## User Management Error   

**Users with the Same Name Cannot be Created**

After deleting a user name and verifying that the user name _is not_ on the list of user names, it _is not_ possible to create a new user with the same name within a short period of time (_roughly a few minutes_). This is due to a user's-related Kubernetes objects, which are deleted asynchronously by Kubernetes. Due to these deletions, it can take time to resolve.

### User Management Error Workaround  

To resolve, wait a few minutes before creating a user with the same name.

## Nauta Connection Error 

**Launching a TensorBoard instance and launching a Web UI _does not_ work.**
 
After running Nauta to launch the Web UI (`nctl launch webui`) or the `nctl launch tb <experiment_name>` commands, a connection error message may be visible (for example: `Error during creation of a proxy for a tensorboard`). During the usage of these commands, a proxy tunnel to the cluster is created. 

As a result, a connection error can be caused by an incorrect `user-config` generated by an Administrator or by incorrect proxy settings in a local machine. 

### Nauta Connection Error Workaround

To prevent this, ensure that a valid user-config is used and check the proxy settings. In addition, ensure that the current proxy settings _do not_ block any connection to a local machine.  


## DNS Server has Changed or Missed in Installation Step

To change DNS settings in the installation, make the changes on the master node:

* Stop consul service `systemctl stop consul`
* Change file with your favorite text editor i.e. vim `vim /etc/consul/dns.json`
* In recursor, provide proper DNS server information. For example: `"recursors" : ["8.8.8.8","8.8.4.4"]`
* Start consul service: `systemctl start consul`

##  Insufficient Resources Causes Experiments Failures 

**An experiment fails just after submission, even if the script itself is correct.**  

If a Kubernetes cluster _does not_ have enough resources, the pods used in experiments are evicted. This results in failure of the whole experiment, even if there are no other reasons for this failure, such as those caused by users (such as, lack of access to data, errors in scripts and so on).

###  Insufficient Resources Causes Experiments Failures Workaround

It is recommended that the Administrator investigate the failures to determine a course of action. For example, determine why have all the resources been consumed. Once determined, try to free them.
    
## Experiment Pods Stuck in Terminating State on Node Failure 

There may be cases where a node suddenly becomes unavailable, for example due to a power failure. Experiments using TFJob  running on such a node will stay _Running  in Nauta_ and pods will terminate templates, indefinitely.
Furthermore, an experiment _is not_ rescheduled automatically. 

As shown below in the example below, such occurrences are visible using the `kubectl` tool:

````
                    user@ubuntu:~$ kubectl get nodes
NAME                                 STATUS     ROLES    AGE   VERSION
worker0.node.infra.nauta             NotReady   Worker   7d    v1.10.6
worker1.node.infra.nauta             Ready      Worker   7d    v1.10.6
master.node.infra.nauta              Ready      Master   7d    v1.10.6

user@ubuntu:~$ kubectl get pods
NAME                                   READY   STATUS        RESTARTS   AGE
experiment-master-0                    1/1     Terminating   0          45m
tensorboard-service-5f48964d54-tr7xf   2/2     Terminating   0          49m
tensorboard-service-5f48964d54-wsr6q   2/2     Running       0          43m
tiller-deploy-5c7f4fcb69-vz6gp         1/1     Running       0          49m
````

### Experiment's Pods Stuck in Terminating State on Node Failure Workaround

To resolve this issue, manually resubmit the experiment using Nauta. This is related to unresolved issues found in Kubernetes and design of TF-operator. For more information, see the GitHub links below. 

* [Pod stuck in unknown status when kubernetes node is down #720](https://github.com/kubeflow/tf-operator/issues/720)
* [Pods are not moved when Node in NotReady state #55713](https://github.com/kubernetes/kubernetes/issues/55713)

## A Multinode Horovod Experiment Receives a FAILED Status

**A Multinode Horovod-based Experiment Receives a FAILED Status after a Pod's Failure**

If during the execution of a multinode, (and a Horovod-based experiment) one of the pods fails, then the whole experiment gets the FAILED status. Such behavior is caused by a construction of a Horovod framework. This framework uses an Open MPI framework to handle multiple tasks instead of using Kubernetes features. Therefore, it _cannot_ rely also on other Kubernetes features such as restarting pods in case of failures. 

### A Multinode Horovod Experiment Receives a FAILED Status Workaround

This results in training jobs using Horovod _does not_ resurrect failed pods. The Nauta system also _does not_ restart these training jobs. If a user encounters this, they should rerun the experiment manually. The construction of a multinode TFJob-based experiment is different, as it uses Kubernetes features. Thus, training jobs based on TFJobs restart failing pods so an experiment can be continued after their failure without a need to be restarted manually by a user.

## Experiments Still in RUNNING State Even if they Finish with Success 

This can happen due to a known issue in Kubernetes client library it may happen, especially when there are a lot of experiments running at the same time. As a result, some single-node experiments _may still be_ in RUNNING status, even if scripts run within such experiments are finished with success. Our analysis indicates that this problem may affect roughly 1% of experiments. 

### Experiments Still in RUNNING State Even if they Finish with Success Workaround

Until a resolution of the problem on library's side is found, monitor the statuses of experiments and check whether they _are not_ running too long relative to predicted duration. If there are such cases, cancel an experiment _without_ purging it. The results are still available on shares. 

----------------------

## Return to Start of Document

* [README](../README.md)

----------------------
