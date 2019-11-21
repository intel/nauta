# Batch Inference Example

For information about the stream inference testing, refer to [Stream Inference](streaming_inference.md).

This section discusses the following topics: 

 - [Flow Example](#flow-example)
 - [MNIST Example](#mnist-example)  
 - [MNIST Data Preprocessing](#mnist-data-preprocessing)
 - [Start Prediction](#start-prediction)
 - [Other Important Information](#other-important-information)
 - [Useful References](#useful-references)

## Flow Example

An example of the general flow is shown below. These are the universal steps that you need to follow:

1. Acquire the dataset and the trained model.

1. Convert the dataset into _Serialized Protocol Buffers_ (PBs). Refer to [Protocol Buffers](https://developers.google.com/protocol-buffers) for additional PB information.

1. Mount the Samba shared folder by invoking the `nctl mount`command (see the example for further details).

1. Copy the serialized PBs and the trained model to the just-mounted share.

1. Run `nctl predict batch` command.

## MNIST Example

You need to have preprocessed MNIST data for feeding the batch inference. You can generate example data executing the following steps:

## MNIST Data Preprocessing

1. Create venv by executing the following command:

   ```
   python3 -m venv .venv
   ```

1. Install the required dependency in venv:

   ```
   source .venv/bin/activate
   pip install tensorflow-serving-api
   ```
   
1. Create a directory with two subdirectories named input and output.

1. Run the `mnist_converter_pb.py` (from nauta/applications/cli/example-python/package_examples) using just-generated venv:

   ```
   python mnist_converter_pb.py
   ```
   Results of conversion are stored in `conversion_out` directory under `work_dir` parameter. The default is: `/tmp/mnist_test/conversion_out`. Copy them to your input directory.

### Parameters of mnist_converter_pb.py

* `work_dir` - Location where files related with conversion will be stored. Default: `/tmp/mnist_tests`.

* `num_tests` - Number of examples to convert.  Default: `100`.


## Start Prediction

1. Run `nctl mount`.

1. Use the command printed by nctl mount. Replace <NAUTA_FOLDER> with 'input' and <MOUNTPOINT> with your input directory.

1. Use the same command, but this time replace <NAUTA_FOLDER> with 'output' and <MOUNTPOINT> with your output directory.

1. If you mounted wrong directories, use `sudo umount [name of the mounted directory]`. You can run `mount` to check which directories have been mounted.

1. Deactivate and delete python virtual environment. Run:
```
deactivate
rm -rf .venv/
```

1. Create model with a script `mnist_saved_model.py` to your input directory. Run(scroll right to see full contents):
```
nctl experiment submit mnist_saved_model.py -sfl [name of the directory where you store nauta]/nauta/applications/cli/example-python/package_examples -n [experiment name of your choice, eg. mn-model] -- --training_iteration=5 --model_version=1 /mnt/output/home/[mn-model - or a name you chose before]
```
You can try out different numbers of iterations.
Copy the directory with the name of your experiment from output folder to the input.

1. Enter the following command (scroll right to see full contents):

  ```
nctl predict batch --model-location /mnt/input/home/mn-model --data /mnt/input/home/conversion_out --model-name mnist -n check
  ```

1. If you want to see the predictions in human-readable form, use the script below:
```
import os
from tensorflow_serving.apis import predict_pb2
for i in range(100):
    with open(os.path.join(".", "{}.pb".format(i)), mode="rb") as pb_file:
            result_pb = pb_file.read()
            resp = predict_pb2.PredictResponse()
            resp.ParseFromString(result_pb)
            print(resp.outputs["scores"].float_val)
```
As a result for each sample we will get an array of 10 elements presenting probabilities of each sample being a given digit. First element represents how likely it is that the picture represents "0", the last one stands for "9". The higher the number, the more likely it is that this sample is in fact that digit.
```
[0.0156935453414917, 0.06918075680732727, 0.023996423929929733, 0.00025786852347664535, 0.07656218856573105, 0.05128718540072441, 0.1812051236629486, 0.02422264777123928, 0.0640382319688797, 0.49355611205101013]
```
In the example above, the highest value has the element of index 9, so the sample probably represented "9".

## Other Important Information

### Paths 

Paths provided in locations such as, `--model-location` and `--data` need to point (for files/directory) from the container's context, _**not**_ from a user's filesystem or mounts. These paths can be mapped using instructions from `nctl mount`. 

For example, if you mounted Samba `/input` and copied the files there, you should pass: `/mnt/input/home/<file>`.

### Model Name

The`--model-name` is optional, but it _must_ match the model name provided during data preprocessing, since generated requests _must_ define which servable they target. 

In the `mnist_converter_pb.py` script, you can find 
`request.model_spec.name = 'mnist'`. This saves the model name in requests, and that name _must_ match a value passed as: 
`--model-name`

If not provided, it assumes that the model name is equal to last directory in model location:
`/mnt/input/home/trained_mnist_model` --> `trained_mnist_model`

## Useful References

* [Serving a TensorFlow Model](https://www.tensorflow.org/serving/serving_basic)
* [Protocol Buffer Basics: Python](https://developers.google.com/protocol-buffers/docs/pythontutorial)
* [mnist_client.py Script](https://github.com/tensorflow/serving/blob/master/tensorflow_serving/example/mnist_client.py)
* [TensorFlow Serving with Docker](https://www.tensorflow.org/serving/docker)

----------------------
## Return to Start of Document

* [README](../README.md)

----------------------


