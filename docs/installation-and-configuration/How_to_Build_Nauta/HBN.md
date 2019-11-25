
# How to Build the Nauta Package

## Nauta Requirements

Before building Nauta, ensure that _your system meets_ the following requirements listed below: hardware, operating system, and proxy settings.

This section discusses the following main topics:

- [How to Clone the Nauta Repository](#how-to-clone-the-nauta-repository)
- [Hardware Requirements](#hardware-requirements)  
- [Overall Operating System Requirements](#overall-operating-system-requirements)
- [Build](#build)
- [Output of the Build](#output-of-the-build)

## How to Clone the Nauta Repository

Execute the following commands from the command line:

- `git clone --recursive https://github.com/IntelAI/nauta.git`

- `cd nauta`

**Note:** For full installation information, refer to the Installation Nauta Installation Procedures section of the [Nauta Installation, Configuration, and Administration Guide](../README.md)

### Hardware Requirements

Part of Nauta's build process involves the compilation of TensorFlow. Therefore, your build server _must meet_ all TensorFlow build requirements. In particular, your CPU _must have_ support for AVX and SSE instructions. To make sure required flags are available on a CPU, call `cat /proc/cpuinfo`. In flags field, instruction sets `avx, sse, sse2, ssse3, sse4_1, sse4_2` should be listed.

**Note:** For SSE information, refer to:  [Streaming SIMD Extensions](https://en.wikipedia.org/wiki/Streaming_SIMD_Extensions) and for AVX information, refer to: [Advanced Vector Extensions](https://en.wikipedia.org/wiki/Advanced_Vector_Extensions).

#### Hardware Configuration Requirements 

For the build server, _**you must**_ have at least 12 GB of RAM and at least 100GB of space for temporary containers, registries, and so on. The size of the final `tar.gz` file is ~5GB.

### Overall Operating System Requirements

To make your Nauta build successful, _**you must**_ set your proxies, ensure you have internet connection and ensure the required packages are installed as shown below. 

### Proxy Setting Requirements 

Set `http_proxy`, `https_proxy` and `no_proxy` environment variables, if you are behind a proxy. `no_proxy` should include the following: `127.0.0.1` and `localhost`.

If proxy issues occur during the build process, as a workaround it is recommended that you configure a transparent proxy (for example, a Redsocks-based solution).
 
**Note:** Docker _should be_ configured to download images from the internet, follow: [official Docker instructions](https://docs.docker.com/config/daemon/systemd/#httphttps-proxy) for more details.

### Internet Connection 

To build the Nauta package, you need an internet connection so that you can untar the tarball, configure your proxy settings, DNS settings, and so on.

### Required Packages: Ubuntu 16.04 LTS or 18.04 LTS

When building Nauta within these versions of Ubuntu (currently, the _only validated_ build environment), the following packages _**must be**_ installed first:

- binutils
- build-essential
- docker
- make
- pigz
- python3-venv
- python3-dev
- virtualenv
- git

To install the required packages, invoke:

`sudo apt update && sudo apt install python3-venv python3-dev virtualenv binutils build-essential make pigz git`

### Docker Community Edition Information  

To install Docker Community Edition (CE), follow: [official Docker instructions](https://docs.docker.com/install/linux/docker-ce/ubuntu/).

The build process requires access to the `docker` command. Remember to add your user to the `docker` group by running: `sudo usermod -aG docker [user]` if the user _has not_ been previously added. 

For more information, refer to the [Post-install Docker guide](https://docs.docker.com/install/linux/linux-postinstall).

**Note:** During the Nauta build process, TensorFlow is checked by the Horovod installer inside its Docker container. 

## Build 

From the main directory of Nauta repository invoke: 

`make k8s-installer-build`

### Build Logs

Logs from the build process are saved to a file and persists if build fails. By default, it is `k8s_installer_build.log` in `tools/.workspace` directory. The Log file path can be controlled through `K8S_INSTALLER_BUILD_LOG_PATH` environment variable.

In addition, it is also possible to clean temporary data if any error during build process occurs by invoking: 

`make k8s-installer-clean`

**Note:** The command shown above is automatically invoked when build process finishes with success.

## Output of the Build

A successful build produces a compressed tarball. The tarball's name and software version appears as follows: `nauta-{version}-{build-id}.tar.gz` (for example: `nauta-1.0.0-190110100005.tar.gz`), This is located in the `tools/.workspace` directory.  

The tarball contains, among other things, docs, images, config files, and ansible playbooks. See [ansible-playbook](https://docs.ansible.com/ansible/latest/cli/ansible-playbook.html) for more information. To complete the installation of Nauta, follow the rest of this installation guide with a prepared `tar.gz` artifact.

**Note:** This guide explains how to build the Nauta application, but to interact with an installed Nauta platform, the `nctl` client is also required. For more information on installing the client, refer to the chapter _Client Installation and Configuration_ in section _How to Build Nauta CLI_ in the [Nauta User Guide](../../user-guide/actions/nctl.md).

## Next Steps: Nauta Installer System Requirements

* [Installer System Requirements](../Installer_System_Requirements/ISR.md)

----------------------

## Return to Start of Document

* [README](../README.md)

----------------------

