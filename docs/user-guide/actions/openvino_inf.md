# OpenVINO Model Server Overview

The OpenVino Model Server (OVMS) is an OpenVINO serving component intended to provide hosting for the OpenVINO inference runtime. 

OVMS is an external API that is fully compatible with TF Serving providing an alternative prediction solution for Nauta users. OpenVINO provides one of the most performant inference solutions available on Intel platforms. In many cases (especially in small batch scenarios) it outperforms other inference engines including TF Serving. 

OVMS does, however have a limited number of supported topologies and therefore cannot be used as the sole inference runtime on Nauta.  It will be employed as an option for models that meet OpenVINO requirements.

Refer to the [OpenVINO White Paper](https://www.intel.ai/openvino-model-server-boosts-ai-inference-operations/#gs.zb9emx) for more information. 

# Inference on Models Served by the OpenVINO Model Server

To perform a batch or stream inference with OVMS, a model in OpenVINO format is required.
To obtain an MNIST model converted to OVMS format (shown in this example), **refer to [exporting models](model_export.md) for complete instructions.**

This section discusses the following topics: 

 - [Mount the Input Directory and Copy OVMS Compatible Model](#mount-the-input-directory-and-copy-ovms-compatible-model)
 - [Models Structure in the Input Directory ](#models-structure-in-the-input-directory ) 
 - [Stream Inference](#stream-inference)  
 - [Batch Prediction](#batch-prediction)
 - [OVMS Prediction with Local Model](#ovms-prediction-with-local-model)

## Mount the Input Directory and Copy OVMS Compatible Model

1. Mount the Nauta input directory via NFS using the following [mount input](mount_exp_input.md) instructions.
2. Copy the OVMS compatible model to the input directory.

## Models Structure in the Input Directory 

Place and mount the Models in a directory structure, as depicted in the example below.

```
models/
├── model1
│   ├── 1
│   │   ├── ir_model.bin
│   │   └── ir_model.xml
│   └── 2
│       ├── ir_model.bin
│       └── ir_model.xml
└── model2
    └── 1
        ├── ir_model.bin
        ├── ir_model.xml
        └── mapping_config.json
```

In case of MNIST model conversion with `model export` command, a directory storing one version of the model is created. Due to prediction prerequisite, the model directory structure _must_ meet the following structure requirements:


```
models/
└── <directory from model export output>
    └── 1
        ├── saved_model.bin
        ├── saved_model.mapping
        └── saved_model.xml
```


## Stream Inference

When the correct model structure is prepared, run model server instance with:


```
nctl predict launch -n ovmsexample --runtime ovms --model-location /mnt/input/home/models/mnist
```


When `nctl predict list` reports the prediction as running (scroll to the right to see the full details):


```
| Prediction instance   | Parameters   | Submission date        | Start date             | Duration      | Owner    | Status   | Template name             | Template version   |
|-----------------------+--------------+------------------------+------------------------+---------------+----------+----------+---------------------------+--------------------|
| ovmsexample           |              | 2019-07-29 03:01:08 PM | 2019-07-29 03:01:12 PM | 0d 0h 26m 13s | user1    | RUNNING  | openvino-inference-stream | 0.1.0              |
```

Perform stream inference by executing the following command:

```
nctl predict stream --name ovmsexample --data input.json
```
An example content of an `input.json` file can be found in examples of nctl located in:

`<nctl_directory>/examples/ovms_inference`.

For `input.json` file delivered in the example result of the stream inference, it will be:

```
{"predictions": [[0.0006329981843009591, 1.111995175051561e-06, 0.00018445802561473101, 0.08759918063879013, 1.9286260055650928e-07, 0.9085237383842468, 2.53505368164042e-05, 0.0012352498015388846, 0.0017150170169770718, 8.265616634162143e-05]]}
```
The output of the prediction, in case of MNIST digit recognition model is a vector of 10 elements. This is the _Index_: the vector that has highest value, and represents predicted class. In this case, the highest value was reported at _Index 5_, which corresponds to class of 'five' digits.

**Note:** Similar JSON files can be generated with python script in: `<nctl_directory>/examples/ovms_inference`, as shown in the example below. 

```
cd <nctl_directory>/examples/ovms_inference
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```


When venv is prepared and invoked, it appears as:

```
python generate_json.py --image_id <IMAGE ID>
```
The `IMAGE ID` argument determines with s picture from MNIST what will be used.

## Batch Prediction

To perform batch prediction, generate the correct protobuffers for inference. This step is similar to [MNIST Data Preprocessing](batch_inf_example.md#mnist-data-preprocessing), but with one difference. During the model conversion to an OV format, some of the model signatures information is missing. To perform prediction on
the converted MNIST model, one additional parameter has to be used with `mnist_converter_pb.py`:

```
mnist_converter_pb.py --model_input_name="x/placeholder_port_0"
```

After file generation, move the directory that contains the `.pb` files to the `/input` mount point.

When all files are prepared, schedule a prediction with the following command:

```
nctl predict batch -n ovmsbatch -rt ovms --model-location /mnt/input/home/models/mnist --data /mnt/input/home/ovms_inference
```
**Note:** The above command assumes that`.pb` files are stored in the `ovms_inference` directory in the `/input` shared folder.

When a batch prediction reaches the `FINISHED` state (as shown in the example), it displays the results (scroll to the right to see the full details). =======

```
| Prediction instance         | Parameters   | Submission date        | Start date             | Duration     | Owner    | Status   | Template name            | Template version   |
|-----------------------------+--------------+------------------------+------------------------+--------------+----------+----------+--------------------------+--------------------|
| mnist-526-19-07-30-00-34-07 |              | 2019-07-30 12:34:35 AM | 2019-07-30 12:34:45 AM | 0d 0h 0m 17s | user1   | COMPLETE | openvino-inference-batch | 0.1.0              |
```

To understand these results of the `/output` mount point, refer to [Working with Datasets](working_with_datasets.md#mounting-and-accessing-folders).

## OVMS Prediction with Local Model

Nauta platform models can also be forwarded without the `/input` mount. This can be performed with the `--local-model-location` option. 

```
nctl predict launch -n localovms --runtime ovms --local-model-location /tmp/models/mnist/
```
**Note:** The above command assumes the MNIST in the OV format is stored in the `/tmp/models/mnist` folder.

----------------------

## Return to Start of Document

* [README](../README.md)

----------------------
