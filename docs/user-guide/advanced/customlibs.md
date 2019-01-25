# Installing libraries and dependencies
To install an OS library or dependency that is not included in standard NAUTA docker image it is required to modify draft pack definition.
In order to install a pip dependency (like numpy or pandas), refer to `experiment submit` command documentations.

## Modifying existing draft packs
The draft packs are located in the nctl_config_ folder. Navigate to _.draft/packs_ folder to list existing packs.
The default pack used by _nctl_ client is _tf-training-tfjob_. Edit the _Dockerfile_ located in selected pack to make necessary changes.

Example _Dockerfile_:

    FROM nauta/tensorflow:1.9.0-py3
    
    WORKDIR /app

    ADD training.py .
    
    ENV PYTHONUNBUFFERED 1
    

### Installing OS packages
The images in Nauta are based on CentOS. To install system package add the following lines to _Dockerfile_:

    RUN yum update
    RUN yum install package1 package2

### Proxy
Depending on the network configuration it may be required to setup proxy servers

     ARG http_proxy=corporate-proxy.com:911
     ARG https_proxy=corporate-proxy.com:912

### Example Dockerfile modification
Below is an example _Dockerfile_ showing installation of additional packages

  
    FROM nauta/tensorflow:1.9.0-py3
    
    WORKDIR /app

    ARG http_proxy=corporate-proxy.com:911
    ARG https_proxy=corporate-proxy.com:912
         
    RUN yum update
    RUN yum install libsndfile
    
    ADD training.py .
    
    ENV PYTHONUNBUFFERED 1
