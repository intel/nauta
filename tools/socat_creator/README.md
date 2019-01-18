## SOCAT IMAGE CREATOR

The goal of scripts located here is to build an approved docker image with _socat_. 
This image is based on approved centos image used by other components of the system. The image is used later
by _nctl_ application to properly connect to docker registry on Windows and MacOS operating 
systems.

The tool consists of the following files:
1) Dockerfile.socat - Dockerfile that creates an image with socat and several additional 
tools (mainly for debugging purposes)
2) Dockerfile.final - Dockerfile used at the end of a process - it creates the final image
that encapsulates stretched image built based on the imgae from _Dockerfile.socat_
3) Makefile - configuration file for _make_ tool
4) socat_script.sh - script responsible for running socat inside of the container.

# Process of creation of an image

The following steps should be taken to build a new image (for example when a new internal
image of Centos has been created):
1) update Dockerfile.socat file with a new version of the Centos image. Name should be taken
from the _container_images.txt_ file which can be found within artifacts of the latest 
approved build of the _nauta_ system. The name taken from the mentioned file should be 
placed after the FROM keyword at the begining of the Dockerfile.socat file.
2) run _make create_ command 
3) copy the _socat-container-image.tar.gz_ file created in the second step to the 
_https://s3.toolbox.nervana.sclab.intel.com/minio/repository/files/_ location.
After adding this file, each consequent build of the _nctl_ application will contain
the latest version of the socat image.

   