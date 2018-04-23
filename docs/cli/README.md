# DLSCTL

## **dlsctl** commands

<ol>
<li> <b>submit</b> - submits one single-node training job on a kuberenetes cluster. Format of the command is as follows:

_dlsctl submit <script_name> -sfl <folder_name> -- <script_arguments>_

arguments:<br>
_<script_name>_ - name of a python script with a description of training. Obligatory<br>
_<script_arguments>_ - string with a list of arguments that are passed to a training script. Optional<br>

options:<br>
_-sfl/-script_folder_location <folder_name>_ - location of a folder content of which is copied into a docker image created
by _dlsctl submit_ command. _dlsctl_ copies the whole content preserving its structure - including subfolder. Optional<br>

example:<br>
_dlsctl submit mnist_cnn.py -sfl /data -- --data_dir=/app/data --num_gpus=0_<br>
Starts a single node training job using mnist_cnn.py script located in a folder from which _dlsctl_ command was issued. Content of
the /data folder is copied into docker image (into /app folder - which is a work directory of docker images created using
tf-training pack). Arguments _--data-dir_ and _--num_gpus_ are passed to a script.
</li>
</ol>


## K8S roles definitions

Below is a list of k8s roles and rolebindings needed by _dlsctl_ application. \<USERNAME> is a name of
user who wants to get access to k8s through _dlsctl_ application.

**I) ClusterRoles**
1) Type : ClusterRole<br>
Name : \<USERNAME>-common-access<br>
PolicyRule:

  | Resources | Non-Resource URLs | Resource Names | Verbs |
  |:--- |:---|:---|:---|
  | namespaces.* | [] | [\<USERNAME>] | [get watch list delete] |


2) Type : ClusterRole<br>
Name: \dls-common-access<br>
PolicyRule:

  | Resources | Non-Resource URLs | Resource Names | Verbs |
  |:--- |:--- |:--- |:--- |
  | namespaces.* | [] | [namespaces] | [get watch list delete] |

**II) ClusterRoleBindings**
1) Name: \<USERNAME>-common-access<br>
   Role:<br>
	+ Kind:  ClusterRole<br>
	+ Name:  \<USERNAME>-common-access<br>

	Subjects:

  | Kind | Name | Namespace |
  |:--- |:--- |:--- |
  | ServiceAccount | \<USERNAME> | auth |

2) Name: \<USERNAME>-dls-common-access<br>
Role:
	+ Kind:  ClusterRole
	+ Name:  dls-common-access

	Subjects:

  |Kind | Name | Namespace |
  |:--- |:--- |:---|
  | ServiceAccount | \<USERNAME> | auth |
=======
## Example TensorFlow trainings

All trainings have been tested using Python 3.5.2 and TensorFlow 1.7.0


### MNIST digit recognition

#### Preparing dataset
To run any training job on MNIST dataset enter `cli/python_examples/mnist/`. Make sure you downloaded compressed MNIST dataset and placed it in `/datasets/mnist/`. You can do it by calling `python download_mnist.py --data_dir=/datasets/mnist/` helper script from `cli/python_examples/mnist/` directory.

#### Single node, deep neural net MNIST training
To run simple, single node training on MNIST dataset run: `python mnist_single_node.py --data_dir=/datasets/mnist/`

#### Multi node, shallow neural net MNIST training
To run multi node training on MNIST dataset prepare 3 terminal windows (preferably via `tmux`) and enter `cli/python_examples/mnist/` directory. Multi node training will use 2 worker nodes and one parameter servers (PS). To start training run one command per terminal window:

* first window: `python mnist_multi_node.py --job_name="worker" --task_index=0 --data_dir=/datasets/mnist/ --ps_hosts=localhost:2222 --worker_hosts=localhost:2223,localhost:2224`
* second window: `python mnist_multi_node.py --job_name="worker" --task_index=1 --data_dir=/datasets/mnist/ --ps_hosts=localhost:2222 --worker_hosts=localhost:2223,localhost:2224`
* third window: `python mnist_multi_node.py --job_name="ps" --task_index=0 --data_dir=/datasets/mnist/ --ps_hosts=localhost:2222 --worker_hosts=localhost:2223,localhost:2224`

#### Multi node, deep neural net MNIST training
The steps are exactly the same as for the above shallow network training. The only difference is that the script's name is `mnist_deep_multi_node.py`


### IMDB reviews sentiment analysis with LSTM
The code is based on https://www.oreilly.com/learning/perform-sentiment-analysis-with-lstms-using-tensorflow tutorial.

#### Preparing dataset
Download `wordVectors.npy` (word2vec mapping) and `ids_matrix_imdb.npy` (word2vec embedding) and place them in `/datasets/imdb/`. Files are available under https://ftp.nervana.sclab.intel.com/data/lstm_reviews/ and can be easily downloaded using `wget`. An alternative is visiting https://github.com/adeshpande3/LSTM-Sentiment-Analysis.git and downloading it from there.

#### Single node LSTM
To run sentiment analysis on vectorized IMDB dataset run: `python imdb_lstm.py --data_dir=/datasets/imdb/`


### Image recognition with AlexNet using Imagenet dataset

#### Preparing dataset
Download Imagenet dataset and place it in directory of your choice. Note that file structure must be compliant with following template:
```
-> /datasets/alexnet/
  -> i1k-extracted/
    -> train/
      -> 0/
      -> 1/
      ...
      -> 999/
    -> val/
      -> 0/
      -> 1/
      ...
      -> 999/
  ```
It is vital for the directory to have identical structure - `i1k-extracted/` parent dir with 2 subdirs: `train/` and `val/`. Each od them needs to to have 1000 subdirectories named from 0 to 999. 
 
#### Single node AlexNet training in TF
The code is based on: https://github.com/kratzert/finetune_alexnet_with_tensorflow
To run single node AlexNet training implemented in pure TF enter directory `cli/python_examples/alexnet/` and run: `python alexnet_single_node.py --training_epoch=NUM_EPOCHS --batch_size=BATCH_SIZE --model_version=MODEL_VERSION --data_dir=/PATH/TO/IMAGENET --output_dir=OUTPUT_DIR`


#### Single node AlexNet training in Keras
To run single node AlexNet training implemented in Keras enter directory `cli/python_examples/alexnet/` and run: `python alexnet_single_node_keras.py --data_dir=/PATH/TO/IMAGENET`
 
#### Multi node AlexNet training in Keras
To run multi node training on Imagenet dataset prepare 3 terminal windows (preferably via `tmux`) and enter `cli/python_examples/alexnet` directory. Multi node training will use 2 worker nodes and one parameter servers (PS). To start training run one command per terminal window:

* first window: `python alexnet_multi_node_keras.py -job_name="ps" --task_index=0 --ps_hosts=localhost:2222 --worker_hosts=localhost:2223,localhost:2224 --data_dir=/datasets/alexnet/`
* second window: `python alexnet_multi_node_keras.py -job_name="worker" --task_index=0 --ps_hosts=localhost:2222 --worker_hosts=localhost:2223,localhost:2224 --data_dir=./datasets/alexnet/`
* third window: `python alexnet_multi_node_keras.py -job_name="worker" --task_index=1 --ps_hosts=localhost:2222 --worker_hosts=localhost:2223,localhost:2224 --data_dir=/datasets/alexnet/`
