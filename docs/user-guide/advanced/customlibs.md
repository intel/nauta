# Installing Libraries and Dependencies

This section discusses the following main topics: 

 - [Installing an Operating System library](#installing-an-operating-system-library)
 - [Modifying Existing Draft Packs](#modifying-existing-draft-packs)
 - [Installing Operating System Packages](#installing-operating-system-packages)  
 - [Proxy Settings](#proxy-settings)
 - [Example Dockerfile Modification](#example-dockerfile-modification) 

## Installing an Operating System Library

To install an Operating System library or dependency that _is not_ included in standard Nauta Docker image, you _must_ modify the draft pack definition. To install a pip dependency (like NumPy Python or pandas Python), refer to `experiment submit` command documentation.

**Note:** For NumPy Python information, refer to: [NumPy.org](http://www.numpy.org). For pandas Python information, refer to: [Pandas Information](https://pandas.pydata.org/)

## Modifying Existing Draft Packs

The draft packs are located in the `nctl_config` folder. Navigate to `.draft/packs` folder to list existing packs.
The default pack used by _nctl_ client is `tf-training-single`. Edit the _Dockerfile_ located in selected pack to make necessary changes.

Example _Dockerfile_:

```
    FROM nauta/tensorflow:1.9.0-py3
    
    WORKDIR /app

    ADD training.py .
    
    ENV PYTHONUNBUFFERED 1
``` 

## Installing Operating System Packages

The images in Nauta are based on CentOS. To install system package, add the following lines to _Dockerfile_:

```
    RUN yum update
    RUN yum install package1 package2
```

## Proxy Settings

Depending on the network configuration, it may be required to setup proxy servers.

     ARG http_proxy=corporate-proxy.com:911
     ARG https_proxy=corporate-proxy.com:912

## Example Dockerfile Modification

An example _Dockerfile_ showing installation of additional packages is shown below.

```  
    FROM nauta/tensorflow:1.9.0-py3
    
    WORKDIR /app

    ARG http_proxy=corporate-proxy.com:911
    ARG https_proxy=corporate-proxy.com:912
         
    RUN yum update
    RUN yum install libsndfile
    
    ADD training.py .
    
    ENV PYTHONUNBUFFERED 1
```
----------------------


## Return to Start of Document

* [README](../README.md)
 
----------------------

