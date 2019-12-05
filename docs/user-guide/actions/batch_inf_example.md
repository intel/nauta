# TensorFlow Serving Batch Inference Example

For information about the stream inference testing, refer to [Stream Inference](streaming_inference.md).

This section discusses the following topics: 

 - [Flow Example](#flow-example)
 - [MNIST Example](#mnist-example)  
 - [MNIST Data Preprocessing](#mnist-data-preprocessing)
 - [Start Prediction](#start-prediction)
 - [Other Important Information](#other-important-information)
 - [Useful References](#useful-references)

## Flow Example

Below are the general steps required to run batch inference on Nauta.

1. Acquire the dataset and the trained model.

2. Convert the dataset into _Serialized Protocol Buffers_ (PBs). Refer to [Protocol Buffers](https://developers.google.com/protocol-buffers) for additional PB information.

3. Mount the Samba shared folder by invoking the `nctl mount`command (see the example for further details).

4. Copy the serialized PBs and the trained model to the just-mounted share folder.

5. Run `nctl predict batch` command.

**Note:** Be aware, if the general flow requirements are not met you will not be able to complete the example.

## MNIST Example

You _must_ preprocess MNIST data for feeding the batch inference. You can generate example data by executing the following steps:

## MNIST Data Preprocessing

1.  Execute the following command to create venv:

    ```
    python3 -m venv .venv
    ```

2. Install the required dependency in venv:

   ```
   source .venv/bin/activate
   pip install tensorflow-serving-api
   ```
   
3. Create a directory with two subdirectories named input and output.

4. Run the `mnist_converter_pb.py` (from the installed examples folder) using just-generated venv:

   ```
   python mnist_converter_pb.py
   ```
   The results of conversion are stored in `conversion_out` directory under `work_dir` parameter. The default is: `/tmp/mnist_test/conversion_out`. Copy them to your input directory.

### Parameters of mnist_converter_pb.py

* `work_dir` - Location where files related with conversion will be stored. The default is: `/tmp/mnist_tests`.

* `num_tests` - Number of examples to convert.  The default is: `100`.

## Start Prediction

1. Run `nctl mount`.

2. Use the command printed by `nctl mount`. Replace **<NAUTA_FOLDER>** with _input_ and <MOUNTPOINT> with your input directory.

3. Use the same command, but this time replace **<NAUTA_FOLDER>** with _output_ and <MOUNTPOINT> with your output directory.

4. If you mounted the wrong directories, use the `sudo umount [name of the mounted directory]`. You can run `mount` to check which directories have been mounted.

5. Deactivate and delete python virtual environment. 

6. Execute the following commmand:

```
deactivate
rm -rf .venv/
```

7. Create a model with the script `mnist_saved_model.py` to your input directory. 

8. Execute the following commmand:

```
nctl experiment submit mnist_saved_model.py -sfl /nauta/applications/cli/examples --name mn-model  -- --training_iteration=5 --model_version=1 --export_dir /mnt/output/home/mn-model
```
*  **Notes:** 

    * Where you see `--name`, this indicates the experiment name of your choice. This example uses mn-model.
    
    * The `-sfl/--script-folder-location` must include the directory where Nauta examples are stored, including   `mnist_saved_model.py`.

* You can try out a number different  of iterations. 

9. Copy the directory with the name of your experiment from output folder to the input.

10. Execute the following command:

  ```
nctl predict batch --model-location /mnt/input/home/predict-model --data /mnt/input/home/conversion_out --model-name mnist --name batch-predict
  ```

11. Use the script below to see predictions in a human-readable form:
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

As a result of each sample, you will get an array of 10 elements that present the possibility of each sample being a given digit. The first element represents how likely it is that the picture represents "0", the last element represents "9". The higher the number, the more likely it is that this sample is that digit. An example is shown below.

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
