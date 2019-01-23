
# How to Build the Nauta Package

## Dependencies and Requirements

There are dependencies and requirements (such as having Ubuntu installed) to build Nauta, if you wish to perform your own build. You must download the tarball from the Git repository before starting the build process.

## Ubuntu* 16.04 LTS or 18.04 LTS
- python3-venv
- python3-dev
- binutils
- build-essential
- pip3
- tar
- pigz
- Docker

**Note:**  During platform build process, TensorFlow* is checked by Horovod* installation inside Docker* container. 

### Your Build Machine

You _must_ meet all TensorFlow* requirements: in particular your CPU must have support for SSE instructions. To make sure SSE is available on a cpu, call `cat /proc/cpuinfo`. `sse sse2` should be listed in `flags` field.

The build process hardware should have at least 12 GB of RAM and at least 100GB of space for temporary containers, registries, and so on. The size of final tar.gz file is ~5GB.

The build process requires access to docker command. Remember to add user to docker group by: `sudo usermod -aG docker
[user]` if he/she has not been added there yet. For more information, refer to the 
[Post-install Docker guide](https://docs.docker.com/install/linux/linux-postinstall).

### Proxy Settings
Utilize `http_proxy`, `https_proxy` and `no_proxy` environment variables, if you are behind a proxy. `no_proxy` should include in particular `127.0.0.1` and `localhost`.

If proxy issues occur during the build process, it is recommended that you configure a transparent proxy (for example, a redsocks-based solution).

### Build
In the main directory of Nauta repository invoke: 

`make k8s-installer-build`

During the build process, Docker images related to Nauta are prepared. After a successful build, the `tar.gz` file can be found in the `tools/.workspace` directory.

## Connecting to the Internet

To build Nauta package you need internet connection so that you can untar the tarball, configure your proxy settings, DNS settings, and so on. 

## Tarball—Output of the Build
An artifact’s associated name is: `nauta-{version}-{build-id}.tar.gz` (for example: `nauta-1.0.0-190110100005.tar.gz).`
In addition, the package contains docs, images, config files, and ansible tasks. To install the platform, follow this installation guide with a prepared `tar.gz` artifact.

To interact with an installed Nauta platform, the nctl client is required. For more information refer to the chapter _Client Installation and Configuration_ in section _How to Build Nauta CLI_ in the Nauta User Guide.

## Next Steps: Nauta Installer System Requirements

* [Installer System Requirements](../Installer_System_Requirements/ISR.md)
