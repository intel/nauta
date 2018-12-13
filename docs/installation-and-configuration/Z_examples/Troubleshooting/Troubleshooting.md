# Troubleshooting Guide

## Jupyter Error 

* __Saving a File Causes Following Error:__
    
        Creating file failed. An error occured while creating a new file.
        
        Unexpected error while saving file: input/home/filneme [Errno 2]
        No such file or directory: '/mnt/input/home/filename'
        
    The error appears when a user tries to save file in _/input/home_ folder which is a readonly folder. In Jupyter, select the _/output/home_ folder. 
    
* **Note:** Closing the Jupyter notebook window in a web browser causes experiments to stop executing. Attaching to the same Jupyter session still shows the stopped experiment.

    This is a known issue in Jupyter [https://github.com/jupyter/notebook/issues/1647](https://github.com/jupyter/notebook/issues/1647). Currently there is no workaround.
    

## User Management Error 

* __User with the same name cannot be created directly after its removal__

After deleting a user name and verifying that the user name _is not_ on the list of user names, _it is not_ possible to create a new user with the same name within short period of time. The reason is that the user's related Kubernetes objects are deleted asynchronously by Kubernetes and it can take some time.

**Note:** To resovle, wait a few minutes before creating a user with the same name.


## Docker Error 

* __The Docker installation on the client machine takes up a lot of space and contains a lot of container images__

[https://docs.docker.com](https://docs.docker.com) states:
_Docker takes a conservative approach to cleaning up unused objects (often referred to as “garbage collection”), such as images, containers, volumes, and networks: these objects are generally _not_ removed unless you explicitly ask Docker to do so._

**Note:** Refer to the following information for detailed instructions on how to prune unused Docker images: [https://docs.docker.com/config/pruning/](https://docs.docker.com/config/pruning/) 
