
# How to Build the Nauta Package

## Building Nauta Platform

### Dependencies and Requirements

There are dependencies and requirements to building Nauta. Make sure all dependencies are installed before starting the building process.

### Ubuntu* 16.04 LTS and 18.04 LTS
- python3-venv
- python3-dev
- virtualenv
- binutils
- build-essential
- pigz
- docker

To install required packages invoke:

`sudo apt update && sudo apt install python3-venv python3-dev virtualenv binutils build-essential pigz`

To install Docker CE just follow [official docker instruction](https://docs.docker.com/install/linux/docker-ce/ubuntu/).

**Note:** During platform build process, Horovod* is checking if TensorFlow* is able to run on build machine, please see hardware requirements section below. 

### Your Build Machine

You _must_ meet all TensorFlow* requirements: in particular your CPU must have support for SSE instructions. To make sure SSE is available on cpu, call `cat /proc/cpuinfo`. `sse sse2` should be listed in `flags` field.

The build process hardware should have at least 12 GB of RAM and at least 100GB of space for temporary containers, registries, and so on. The size of final tar.gz file is ~5GB.

The build process requires access to docker command. Remember to add user to docker group by: `sudo usermod -aG docker
[user]` if he/she hasn't been added there yet. See also [post-install docker guide](https://docs.docker.com/install/linux/linux-postinstall).

### Proxy Settings
Utilize `http_proxy`, `https_proxy` and `no_proxy` environment variables, if you're behind proxy. `no_proxy` should include in particular `127.0.0.1` and `localhost`.

If proxy issues occur during the build process, it is recommend that your configure a transparent proxy (for example, a redsocks-based solution).

### Build
In the main directory of Nauta repository invoke: 

`make k8s-installer-build`

During the build process, Docker images related to Nauta are prepared. After a successful build, the `tar.gz` file can be found in the `tools/.workspace` directory.

### Artifact Name

An artifact’s associated name is: `nauta-{version}-{build-id}.tar.gz` (for example: `nauta-1.0.0-190110100005.tar.gz`). In addition, the package contains docs, images, config files, and ansible tasks.
To install platform just follow installation guide with prepared tar.gz artifact. 

To interact with installed Nauta platform, nctl app is required. Instruction about nctl build process is available in
user-guide in nctl chapter.
