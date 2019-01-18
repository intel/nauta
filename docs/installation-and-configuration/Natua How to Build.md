
# How to Build the Nauta Package

## Dependencies and Requirements

There are dependencies and requirements to building Nauta. Make sure all dependencies are installed before starting the building process.

## Ubuntu* 16.04 LTS and 18.04 LTS
- python3-venv
- python3-dev
- binutils
- build-essential
- pip3
- tar
- pigz
- Docker

**Note:** During platform build process, TensorFlow* is checked by Horovod* installation inside Docker* container. 

## Your Build Machine

You _must_ meet all TensorFlow requirements: in particular you must implement the set of instructions available on CPU. This may impact the building process on virtual machines without SSE capabilities. 

The build process hardware requirements require at least 12 GB of RAM and at least 50GB of space for temporary containers, registries, and so on. The size of final tar.gz file is ~5GB.

## Proxy Settings

**Utilize:**

`http_proxy`
`https_proxy and no_proxy environment variables, if you are behind a proxy`
`no_proxy should include in particular 127.0.0.1 and localhost`

If proxy issues occur during the build process, it is recommend that your configure a transparent proxy (for example, a redsocks-based solution).

## Build
In the main directory of Nauta repository invoke: 

`make k8s-installer-build`

During the build process, Docker images related to Nauta are prepared. After a successful build, the `tar.gz` file can be found in the `tools/.workspace` directory.

## Artifact Name

An artifact’s associated name is: `nauta-{version}-{build-id}.tar.gz` (for example: `nauta-1.0.0-190110100005.tar.gz`). In addition, the package contains docs, images, config files, and ansible tasks.

