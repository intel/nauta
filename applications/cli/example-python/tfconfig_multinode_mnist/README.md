# Distributed MNIST training example

1. Download MNIST dataset from http://yann.lecun.com/exdb/mnist/ and put all 4 .gz files to 'data' directory next to
   training.py file
1. Submit training:
```
nctl exp s training.py -sfl data -t multinode-tf-training-tfjob -- --data_dir /app
```


