# Carbon CLI

## Requirements

* kubectl >= 1.9.2
* helm >= 2.8.1
* docker >= 18.03.0-ce

These tools need to be installed on system (i.e. available in terminal by PATH).

Remember about setting `http_proxy`, `https_proxy` and `no_proxy` environment variables, if you're behind
proxy.

## Usage

### Running training:

`dlsctl submit <SCRIPT_NAME> -sfl <FOLDER_NAME> -- <SCRIPT_ARGUMENTS>`

* SCRIPT_NAME - name of a training script - required
* FOLDER_NAME - content of a folder will be copied into docker image created as a result of execution of this command - optional
* SCRIPT_ARGUMENTS - those arguments will be passed to a script as they were given in a command - optional.


for example:

`dlsctl submit mnist_softmax.py -sfl /home/GER/jchrapko/dell_dls/carbon/cli/data/data -- --data_dir /app/`

### Verifying binary dependencies:

`dlsctl verify`


## Development requirements

### Ubuntu 16.04 LTS

* Python 3.6
* python3.6-dev 
* python3.6-venv
* make
* binutils

```
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt-get update
sudo apt-get install python3.6 python3.6-dev python3.6-venv make binutils
```

### Ubuntu 17.10.1

* make
* python3-venv
* python3-dev
* binutils

```
sudo apt update
sudo apt install make python3-venv python3-dev binutils
```


### Windows 10
* Python 3.6.5 64-bit (https://www.python.org/ftp/python/3.6.5/python-3.6.5-amd64.exe)
* make (http://gnuwin32.sourceforge.net/packages/make.htm)
* 7-zip (https://www.7-zip.org/)
* wget (https://eternallybored.org/misc/wget/)
* MSYS2 (http://www.msys2.org/)
* git (https://git-scm.com/download/win)
* Windows 10 SDK (https://developer.microsoft.com/en-us/windows/downloads/windows-10-sdk)

You should have these tools (except Windows SDK) available system-wide via command-line (add them to PATH).

Also, remember about setting `http_proxy`, `https_proxy` and `no_proxy` environment variables, if you're behind
proxy. `no_proxy` should include in particular `127.0.0.1` and `repository.toolbox.nervana.sclab.intel.com` for 
downloading draft binary from our storage.


## Build
Be sure that development requirements above are fulfilled and in `cli` directory run `make build` . Artifcats 
will be available in `dist` directory.

## Installation
You can use dlsctl binary directly from unpacked archive or add it to PATH to have it available globally.

## Run example training
Currently only single-node tensorflow training is supported. 

Assumed that you have kubectl, helm and docker properly configured and running (remember about proper proxy settings
if you're behind one).

Step-by-step instruction to run example training:

1. Build or download CLI (https://github.com/NervanaSystems/carbon/releases)

1. Create some directory:
    ```
    mkdir experiment
    cd experiment
    ```
1. Copy training py script (cli/example-python/mnist/mnist_single_node.py):
    ```
    cp cli/example-python/mnist/mnist_single_node.py .
    ```
1. Download MNIST dataset (from http://yann.lecun.com/exdb/mnist/):
    ```
    mkdir data
    cd data
    wget http://yann.lecun.com/exdb/mnist/train-images-idx3-ubyte.gz http://yann.lecun.com/exdb/mnist/train-labels-idx1-ubyte.gz http://yann.lecun.com/exdb/mnist/t10k-images-idx3-ubyte.gz http://yann.lecun.com/exdb/mnist/t10k-labels-idx1-ubyte.gz
    cd ..
    ```
1. Submit experiment:
    ```
    dlsctl submit mnist_single_node.py -sfl data -- --data_dir /app/
    ```