# How to build Nauta CLI 

### Ubuntu 16.04 LTS

* python 3.6
* python3.6-dev 
* python3.6-venv
* build-essential
* binutils
* curl

```
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt-get update
sudo apt-get install python3.6 python3.6-dev python3.6-venv make binutils
```

### Ubuntu 18.04.1 LTS

* python 3.6
* python3-venv
* python3-dev
* binutils
* build-essential
* curl

```
sudo apt update
sudo apt install python3-venv python3-dev binutils build-essential
```

### MacOS Sierra
* python 3.6
* python3-venv
* python3-dev
* binutils
* make
* curl
* docker

### Windows 10
* python 3.6.5 64-bit (https://www.python.org/ftp/python/3.6.5/python-3.6.5-amd64.exe)
* make (http://gnuwin32.sourceforge.net/packages/make.htm)
* 7-zip (https://www.7-zip.org/)
* wget (https://eternallybored.org/misc/wget/)
* MSYS2 (http://www.msys2.org/)
* git (https://git-scm.com/download/win)
* docker (https://docs.docker.com/docker-for-windows/install/)
* Windows 10 SDK (https://developer.microsoft.com/en-us/windows/downloads/windows-10-sdk)

You should have these tools (except Windows SDK) available system-wide via command-line (add them to PATH).

### Proxy settings

Also, remember about setting `http_proxy`, `https_proxy` and `no_proxy` environment variables, if you're behind
proxy. `no_proxy` should include in particular `127.0.0.1` and `localhost`.

## Build
Be sure that development requirements above are fulfilled and in `applications/cli` directory run `make build`.
Artifacts will be available in `dist` directory, including nctl binary.
If you wish to rebuild nctl after any changes you can invoke `make clean build` (it cleans only dist and build directory)
or trigger `make full_clean build` to recreate also .venv directory.

If you want to create tar.gz package with nctl you should invoke `make nctl-build` from main directory in repository.
After successful build tar.gz file can be found in `applications/cli` directory. Package contains nctl binary and all
dependencies like helm, draft etc. Also docs and examples directories will be available.

##### Available make targets
`make clean` - removes build artifacts only

`make full_clean` - removes build artifacts and virtual env

`make build` - builds cli app

`make venv` - creates .venv with all modules required by nctl

`make venv-dev` - internal target used by makefiles

