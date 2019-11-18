# How to Build the Nauta Command Line Interface

## Build Requirements

### Ubuntu 16.04 LTS and Ubuntu 18.04 LTS

* python 3.6
* python3.6-dev
* python3.6-venv
* build-essential
* binutils
* curl
* git

You can use the following command to install the required dependencies:
```
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt update && sudo apt install python3.6 python3.6-dev python3.6-venv build-essential binutils curl
```
## MacOS High Sierra (or later) Requirements

* python 3.6
* python3-venv
* python3-dev
* binutils
* make
* curl
* git

### Proxy Settings

Make sure you have the following settings: http_proxy, https_proxy, and no_proxy environment variables if you are behind proxy. The no_proxy must include: 127.0.0.1 and localhost.

## Building nctl

Make sure the development requirements above are met. In the applications/cli directory run: make build. As a result, artifacts are available in `dist` directory, including `nctl` binary.

Should you need to rebuild nctl after any changes, you can invoke `make clean build` (it cleans only the dist and build directories) or trigger `make full_clean build` to recreate also _.venv_ directory.

If you want to create `tar.gz` package with nctl, invoke `make nctl-build` from main directory in the repository.
After a successful build, the tar.gz file can be found in applications/cli directory. The Package contains the nctl binary and all dependencies, such as Helm, docs, and example directories.

### Available make Commands and Targets

`make clean` - Removes build artifacts only

`make full_clean` - Removes build artifacts and virtual env

`make build` - Builds cli app

`make pack` - Creates a tar.gz package with `nctl` artifacts 

`make venv` - Creates _.venv_ with all modules required by nctl

----------------------
 
## Return to Start of Document

* [README](../README.md)

----------------------
 
