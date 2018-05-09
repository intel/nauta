# DLSCTL

## **dlsctl** commands

#### General options/flags
 Here is a list of flags/options that can used with any command from a list of commands given below:  
 _-v/-vv/--verbose_ </b> - verbose. If this option is given, application displays on a console logs from execution of a certain command. If _-v_ option is
 given - basic logs on INFO/EXCEPTION/ERROR levels are displayed. If _-vv_ option (it may contain more vs - for example _-vvv_)
 is given - detailed logs on INFO/DEBUG/EXCEPTION/ERROR levels are displayed.  

 _-s_ - silent. If the option is given - all commands that return some kind of ids (for example submit command returns a name of a
 submitted experiment) return it in a plain format (without any tables or paramater names - just plain id). Detailed description of
 how this flag is interpreted by a certain command can be found in a description of commands.

#### Format of messages returned by commands

If option -s isn't given - _dlsctl_ command returns its outcome in a tabluar format. If except of outcome of the command
additional messages are also returned - they appear before the table with output.
If option -s is given - _dlsctl_ command returns only its outcome, additional messages are hidden. Outcome in this case is
displayed as a plain text - without any names etc. More details concerning formatting of output using this option
can be found in a description of a _-s_ option and in description of certain commands.

Here is an example output of _submit_ command:
<!-- language: lang-none -->

    dlsctl submit training.py
    
    
    | Experiment         | Status   |
    +--------------------+----------+
    | t20180423121021851 | Received |

    dlsctl submit error_training.py

    Missing pod name during creation of registry port proxy.<br>

    | Experiment         | Status   |
    +--------------------+----------+
    | t20180423121021851 | Error    |
    

    dlsctl submit -s error_training.py</i> </li>

    t20180423121021851


### List of commands

- [submit](commands/SUBMIT.md) - submits one single-node training job on kubernetes cluster. 
- [adduser](commands/ADDUSER.md) - creates and initializes a new DLS4E user.
- [mounts](commands/MOUNTS.md) - mounts a user's directory on a local machine
- [list](commands/LIST.md) - displays a list of experiments
- [logs](commands/LOGS.md) - displays logs from an experiment
- [view](commands/VIEW.md) - displays details of an experiment
- [launch](commands/LAUNCH.md) - exposes a DLS4E web app to a user
- [cancel](commands/CANCEL.md) - cancels an experiment
- [interact](commands/INTERACT.md) - starts interactive session with Jupyter Notebook
- [predict](commands/PREDICT.md) - starts predictions
- [verify](commands/VERIFY.md) - verifies installation of _dlsctl_ application
- [version](commands/VERSION.md) - displays version of _dlsctl_ application
- [template_list](commands/TEMPLATE_LIST.md) - displays a list of available templates

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
