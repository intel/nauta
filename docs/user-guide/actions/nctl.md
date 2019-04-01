# How to Build the Nauta Command Line Interface (nctl)

## NCTL Development Requirements

### Ubuntu 16.04 LTS and Ubuntu 18.04 LTS

* python 3.6
* python3.6-dev
* python3.6-venv
* build-essential
* binutils
* curl
* git

```
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt update && sudo apt install python3.6 python3.6-dev python3.6-venv build-essential binutils curl
```
### MacOS High Sierra
* python 3.6
* python3-venv
* python3-dev
* binutils
* make
* curl
* git

### Windows 10
* Python 3.6.5 64-bit (https://www.python.org/ftp/python/3.6.5/python-3.6.5-amd64.exe)
* make (http://gnuwin32.sourceforge.net/packages/make.htm)
* 7-zip (https://www.7-zip.org/)
* wget (https://eternallybored.org/misc/wget/)
* MSYS2 (http://www.msys2.org/)
* Git (https://git-scm.com/download/win)
* Windows 10 SDK (https://developer.microsoft.com/en-us/windows/downloads/windows-10-sdk)

Ensure that you have these tools (except Windows SDK) available system-wide via command-line (add them to PATH).

### Proxy Settings

Ensure that you have the following settings: `http_proxy`, `https_proxy` and `no_proxy` and environment variables, if you are behind proxy. The `no_proxy` must include: `127.0.0.1` and `localhost`.

## Build

Ensure that the development requirements above are met and in the `applications/cli` directory run `make build`.
Artifacts will be available in `dist` directory, including nctl binary.

Should you need to rebuild nctl after any changes, you can invoke `make clean build` (it cleans only the dist and build directories) or trigger `make full_clean build` to recreate also _.venv_ directory.

If you want to create `tar.gz` package with nctl, invoke `make nctl-build` from main directory in the repository.
After successful build, the `tar.gz` file can be found in `applications/cli` directory. The Package contains the nctl binary and all dependencies, such as helm, draft and so on. Also, docs and examples directories will be available.

**Note:** Building Nauta CLI on Windows requires a `bash` console. One possible solution is to install MSYS (http://www.mingw.org/wiki/msys). If the build process is started from Windows `cmd` console, it will fail. 

##### Available Make Targets

`make clean` - Removes build artifacts only

`make full_clean` - Removes build artifacts and virtual env

`make build` - Builds cli app

`make venv` - Creates _.venv_ with all modules required by nctl

`make venv-dev` - Internal target used by makefiles




