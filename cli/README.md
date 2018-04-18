# Carbon CLI

## Installation
On Ubuntu 16 (Ubuntu 17+ already contains below packages):
```
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt-get update
sudo apt-get install python3.6 python3.6-dev python3.6-venv
```

## Run exampled training
Currently only single-node tensorflow training is supported. 
Requirements:
* Model file has to be named `training.py`.
* `kubectl` and `helm` with `tiler` has to be installed and configured

Step-by-step instruction to run example training:
1. Build CLI:
    ```
    make build
    cd dist/
    ```
1. [Optional] Setup registry in Draft:
    ```
    draft --home=.draft config set registry 127.0.0.1:{YOUR_FORWARDED_PORT}
    ```
1. [Optional] Forward port to registry:
    ```
    kubectl port-forward registry-docker --namespace=default {YOUR_FORWARDED_PORT}:5000
    ```
1. Download model and run training:
    ```
    wget https://raw.githubusercontent.com/tensorflow/tensorflow/master/tensorflow/examples/tutorials/mnist/mnist_softmax.py -O training.py
    ./main train
    ```
