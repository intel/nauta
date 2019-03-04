
# How to Build the Nauta Package

## Nauta Requirements

Before building Nauta, ensure that _your system meets_ the following requirements listed below: hardware, operating system, and proxy settings. 

## How to Clone a Repository

Execute the following commands from the command line:

- `git clone --recursive https://github.com/IntelAI/nauta.git`

- `cd nauta`

### Hardware Requirements

Part of Nauta's build process involves the compilation of Tensorflow. Because of this, your build server _must meet_ all TensorFlow build requirements. In particular, your CPU _must have_ support for SSE instructions. To make sure SSE is available on a CPU, call `cat /proc/cpuinfo`. `sse sse2` should be listed in `flags` field.

**Note:** For SSE information, refer to: https://en.wikipedia.org/wiki/Streaming_SIMD_Extensions

#### Hardware Configuration Requirements 

For the build server, it is recommended to have at least 12 GB of RAM and at least 100GB of space for temporary containers, registries, and so on. The size of the final tar.gz file is ~5GB.

### Operating System Requirements

#### Proxy Settings Requirements 

Set `http_proxy`, `https_proxy` and `no_proxy` environment variables, if you are behind a proxy. `no_proxy` should include the following: `127.0.0.1` and `localhost.` Also docker should be configured to download images from the internet. Check [docker docker manual](https://docs.docker.com/config/daemon/systemd/#httphttps-proxy).

If any proxy issues occur during the build process, it is recommended that you configure a transparent proxy (for example, a Redsocks-based solution).

#### Internet Connection 

To build the Nauta package, you need an internet connection so that you can untar the tarball, configure your proxy settings, DNS settings, and so on.

#### Required Packages

#### Ubuntu* 16.04 LTS or 18.04 LTS

When building Nauta within these versions of Ubuntu (currently, the only validated build environments), the following packages must be installed first:

- binutils
- build-essential
- docker
- make
- pigz
- python3-venv
- python3-dev
- virtualenv

To install the required packages, invoke:

`sudo apt update && sudo apt install python3-venv python3-dev virtualenv binutils build-essential make pigz`

#### Docker 

To install Docker Community Edition* (CE*), follow: [official Docker instructions](https://docs.docker.com/install/linux/docker-ce/ubuntu/).

The build process requires access to the `docker` command. Remember to add your user to the `docker` group by running: `sudo usermod -aG docker [user]` if the user _has not_ been added previously. 

For more information, refer to the [Post-install Docker guide](https://docs.docker.com/install/linux/linux-postinstall).

**Note:**  During the Nauta build process, TensorFlow* is checked by the Horovod* installer inside its Docker* container. 

## Build 

From the main directory of Nauta repository invoke: 

`make k8s-installer-build`

**Note:** Logs from the build process are saved to a file. By default it is `k8s_installer_build.log` inside of the current
working directory. Log file path can be controller through `K8S_INSTALLER_BUILD_LOG_PATH` env variable.

It is also a possibility to clean a temporary data if any error during build process occurs. Invoke:
`make k8s-installer-clean`

**Note:** Command mentioned above is automatically invoked when build process finishes with success.

## Output of the Build

A successful build produces a compressed tarball. The tarball's name appears as follows: `nauta-{version}-{build-id}.tar.gz` (for example: `nauta-1.0.0-190110100005.tar.gz`). It can be found in the `tools/.workspace` directory.  

The tarball contains, among other things, docs, images, config files, and ansible playbooks. To complete the installation of Nauta, follow the rest of this installation guide with a prepared `tar.gz` artifact.

**Note** This guide explains how to build the Nauta application, but to interact with an installed Nauta platform, the `nctl` client is also required. For more information on installing the client, refer to the chapter _Client Installation and Configuration_ in section _How to Build Nauta CLI_ in the [Nauta User Guide](../../user-guide/actions/nctl.md).

## Next Steps: Nauta Installer System Requirements

* [Installer System Requirements](../Installer_System_Requirements/ISR.md)
