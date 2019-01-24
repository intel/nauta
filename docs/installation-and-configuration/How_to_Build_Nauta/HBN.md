
# How to Build the Nauta Package

## Dependencies and Requirements
Before building Nauta, please ensure that your system meets the requirements listed below, and that your have downloaded the tarball from the Git repository to your build environment.

## Ubuntu* 16.04 LTS or 18.04 LTS
When building Nauta within these versions of Ubuntu (currently, the only validated build environments), the following packages must be installed first:

- python3-venv
- python3-dev
- virtualenv
- binutils
- build-essential
- make
- pigz
- docker

To install required packages invoke:

`sudo apt update && sudo apt install python3-venv python3-dev virtualenv binutils build-essential make pigz`

To install Docker CE just follow [official docker instruction](https://docs.docker.com/install/linux/docker-ce/ubuntu/).

**Note:**  During the Nauta build process, TensorFlow* will checked by the Horovod* installer inside its Docker* container. 

### Your Build Machine

Part of Nauta's build process involves the compilation of Tensorflow*. Because of this, your build server must meet all TensorFlow* build requirements. In particular, your CPU must have support for SSE instructions. To make sure SSE is available on a cpu, call `cat /proc/cpuinfo`. `sse sse2` should be listed in `flags` field.

The build server should have at least 12 GB of RAM and at least 100GB of space for temporary containers, registries, and so on. The size of the final tar.gz file is ~5GB.

The build process requires access to the `docker` command. Remember to add your user to the `docker` group by running : `sudo usermod -aG docker
[user]` if the user has not been added previously. For more information, refer to the 
[Post-install Docker guide](https://docs.docker.com/install/linux/linux-postinstall).

### Proxy Settings
Utilize `http_proxy`, `https_proxy` and `no_proxy` environment variables, if you are behind a proxy. `no_proxy` should include in particular `127.0.0.1` and `localhost`.

If proxy issues occur during the build process, it is recommended that you configure a transparent proxy (for example, a redsocks-based solution).

### Build
Unpack the downloaded tarball, then from the main directory of Nauta repository invoke: 

`make k8s-installer-build`

During the build process, Docker* images related to Nauta are prepared. After a successful build, the resulting `tar.gz` file will be found in the `tools/.workspace` directory.

## Tarball—Output of the Build
A successful build produces a compressed tarball. The tarball's name will be in the following form: `nauta-{version}-{build-id}.tar.gz` (for example: `nauta-1.0.0-190110100005.tar.gz).`
The tarball contains, among other things, docs, images, config files, and ansible playbooks. To complete the installation of Nauta, follow the rest of this installation guide with a prepared `tar.gz` artifact.

Note that this guide explains how to build the Nauta application, but to interact with an installed Nauta platform, the `nctl` client is also required. For more information on installing the client, refer to the chapter _Client Installation and Configuration_ in section _How to Build Nauta CLI_ in the [Nauta User Guide](../../user-guide/actions/nctl.md).

## Next Steps: Nauta Installer System Requirements

* [Installer System Requirements](../Installer_System_Requirements/ISR.md)
