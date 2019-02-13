# Streaming Inference Example

## Example Flow

Following is the basic task flow for this example.

1. The user has saved a trained Tensorflow Serving compatible model.
1. The user will be sending data for inference in JSON format, or in binary format using gRPC API.
1. The user runs `nctl predict launch` command.
1. The user sends inference data using the `nctl predict stream` command, Tensorflow Serving REST API or Tensorflow Serving gRPC API.

## Tensorflow Serving Basic Example
### Launching a Streaming Inference Instance
Basic models for testing Tensorflow Serving are included in https://github.com/tensorflow/serving repository. This example will use the `saved_model_half_plus_two_cpu` model for showing streaming prediction capabilities.

In order to use that model for streaming inference, perform following steps:
1. Clone https://github.com/tensorflow/serving repository:

   `git clone https://github.com/tensorflow/serving`

2. Perform step 3 or step 4 below, based on preference.

3. Run the following command: 
    ```
    $ nctl predict launch --local-model-location <directory where you have cloned Tensorflow
    Serving>/serving/tensorflow_serving/servables/tensorflow/testdata/saved_model_half_plus_two_cpu 
    ```
4. Alternatively to step 3, you may want to save a trained model on input share, so it can be reused by other experiments/prediction instances. In order to to this, run these commands:

   a. Use the mount command to mount Nauta input folder to local machine.<br>
      `$ nctl mount` <br>
      
   b. Run the resulting command printed by `nctl mount` (in this example, assuming that you will mount `/mnt/input` share described in `nctl` command output). After executing the command printed by the `nctl mount` command, you will be able to access input share on your local file system.
   
   c. Now copy the saved_model_half_plus_two_cpu model to input share:<br> 
       `$ cp -r <directory where you have cloned Tensorflow Serving>/serving/tensorflow_serving/servables/tensorflow/testdata/saved_model_half_plus_two_cpu <directory where you have mounted /mnt/input share>`

   d. Run the following command:
   
    ```
    $ nctl predict launch --model-location /mnt/input/saved_model_half_plus_two_cpu
    ```

**Note**:
`--model-name` can be passed optionally to `nctl predict launch` command. If not provided, it assumes that model name is equal to the last directory in model location:

`/mnt/input/home/trained_mnist_model` -> `trained_mnist_model`

### Using a Streaming Inference Instance
After running the `predict launch` command, `nctl` will create a streaming inference instance that can be used in multiple ways, as described below.

#### Streaming Inference With `nctl predict stream` Command
The `nctl predict stream` command allows performing inference on input data stored in JSON format. This method is convenient for manually testing a trained model and provides a simple way to get inference results. For `saved_model_half_plus_two_cpu`, write the following input data and save it in `inference-data.json` file:

```
{"instances": [1.0, 2.0, 5.0]}
```

The model named `saved_model_half_plus_two_cpu` is a quite simple model: for given `x` input value it predicts result of `x/2 +2` operation.
Having passed the following inputs to the model: `1.0`, `2.0`, and `5.0`, and so expected predictions results are `2.5`, `3.0`, and `4.5`. In order to use that data for prediction, check the name of running prediction instance with `saved_model_half_plus_two_cpu` model (the name will be displayed after `nctl predict launch` command executes; you can also use `nctl predict list` command for listing running prediction instances). Then run following command:

```
$ nctl predict stream --name <prediction instance name> --data inference-data.json
```
Following results will be produced:

```
{ "predictions": [2.5, 3.0, 4.5] }
```

Tensorflow Serving exposes three different method verbs for getting inference results. Selecting the proper method verb depends on model used and the expected results. Please refer to https://www.tensorflow.org/serving/api_rest for more detailed information. These method verbs are:
* classify
* regress
* predict

By default, `nctl predict stream` will use `predict` method verb. You can change it by passing `--method-verb` parameter to `nctl predict stream` command, e.g.:

```
$ nctl predict stream --name <prediction instance name> --data inference-data.json --method-verb classify
```

#### Streaming Inference with Tensorflow Serving REST API
Another way to interact with a running prediction instance is to use Tensorflow Serving REST API. This approach could be useful for more sophisticated use cases, like integrating data-collection scripts/applications with prediction instances.

The URL and authorization header for accessing Tensorflow Serving REST API will be shown after prediction instance is submitted, as in the following example.

```
Prediction instance URL (append method verb manually, e.g. :predict):
https://192.168.0.1:8443/api/v1/namespaces/jdoe/services/saved-mode-621-18-11-07-15-00-34:rest-port/proxy/v1/models/saved_model_half_plus_two_cpu

Authorize with following header:
Authorization: Bearer 
1234567890abcdefghijklmnopqrstuvxyz
```

### Accessing the REST API with curl

Here is an an Example of Accessing REST API Using curl, with the following command:

```
$ curl -k -X POST -d @inference-data.json -H 'Authorization: Bearer <authorization token data>' localhost:8501/v1/models/<model_name, e.g. saved_model_half_plus_two_cpu>:predict
```
#### Using Port Forwarding

Alternatively, the Kubernetes port forwarding mechanism may be used. Create a port forwarding tunnel to the prediction instance with the following command:

```
$ kubectl port-forward service/<prediction instance name> :8501
```
Or if you want to start a port forwarding tunnel in the background:

```
$ kubectl port-forward service/<prediction instance name> <some local port number>:8501 &
```

**Note**: The local port number of tunnel you entered above; it will be produced by `kubectl port-forward` if you do not explicitly specify it.

Now you can access REST API on the following URL:

```
localhost:<local tunnel port number>/v1/models/<model_name, e.g. saved_model_half_plus_two_cpu>:<method verb>
```

### Example of Accessing REST API Using curl

```
$ curl -X POST -d @inference-data.json localhost:8501/v1/models/<model_name, e.g. saved_model_half_plus_two_cpu>:predict
```

#### Streaming Inference with Tensorflow Serving gRPC API

Another way to interact with running prediction instance is to use Tensorflow Serving gRPC. This approach could be useful for more sophisticated use cases, like integrating data collecting scripts/applications with prediction instances. It should provide better performance than REST API.

In order to access Tensorflow Serving gRPC API of running prediction instance, the Kubernetes port forwarding mechanism must be used. Create a port forwarding tunnel to a prediction instance with following command:

```
$ kubectl port-forward service/<prediction instance name> :8500
```
Or if you want to start port forwarding tunnel in background:

```
$ kubectl port-forward service/<prediction instance name> <some local port number>:8500 &
```

**Note**: The local port number of the tunnel you entered above; it will be produced by `kubectl port-forward` if you do not explicitly specify it.

You can access the gRPC API by using a dedicated client gRPC client (such as: https://github.com/tensorflow/serving/blob/master/tensorflow_serving/example/mnist_client.py). Alternatively, use gRPC CLI client of your choice (such as: grpcc or polyglot) and connect to:

```
localhost:<local tunnel port number>
```

## References

* https://www.tensorflow.org/serving/serving_basic
* https://www.tensorflow.org/serving/docker
* https://www.tensorflow.org/serving/api_rest




