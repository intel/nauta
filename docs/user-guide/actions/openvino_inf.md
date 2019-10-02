# Inference on models served by OpenVINO model server

To perform batch or stream inference with OVMS, a model in OpenVINO format is required.
For this example you can obtain MNIST model converted to OVMS format following [exporting models](model_export.md) instruction.

### Mount input directory and copy OVMS compatible model

1. Mount Nauta input directory via NFS following [mount input](mount_exp_input.md) instruction.
2. Copy OVMS compatible model to the input directory.

### Models structure in the input directory 
Models should be placed and mounted in a directory structure as depicted below:
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
In case of MNIST model converted with `model export` command, there will be created a directory storing one version of the model. Due to 
prediction prerequisite, model directory structure has to meet the following structure:
```
models/
└── <directory from model export output>
    └── 1
        ├── saved_model.bin
        ├── saved_model.mapping
        └── saved_model.xml
```

## Stream inference
When proper model structure is prepared, run model server instance with:
```
nctl predict launch -n ovmsexample --runtime ovms --model-location /mnt/input/home/models/mnist
```

When `nctl predictl list` reports our prediction as running:
```
| Prediction instance   | Parameters   | Submission date        | Start date             | Duration      | Owner    | Status   | Template name             | Template version   |
|-----------------------+--------------+------------------------+------------------------+---------------+----------+----------+---------------------------+--------------------|
| ovmsexample           |              | 2019-07-29 03:01:08 PM | 2019-07-29 03:01:12 PM | 0d 0h 26m 13s | mzylowsk | RUNNING  | openvino-inference-stream | 0.1.0              |
```

Stream inference can be performed with command:
```
nctl predict stream --name ovmsexample --data input.json
```
Example content of input.json file can be found in examples of nctl (<nctl_directory>/examples/ovms_inference).

For input.json delivered in example result of stream inference will be:
```
{"predictions": [[0.0006329981843009591, 1.111995175051561e-06, 0.00018445802561473101, 0.08759918063879013, 1.9286260055650928e-07, 0.9085237383842468, 2.53505368164042e-05, 0.0012352498015388846, 0.0017150170169770718, 8.265616634162143e-05]]}
```
Output of the prediction, in case of MNIST digit recognition model, is a vector of 10 elements. Index at which this vector has highest value, represents predicted class. In our case, highest value was reported at index 5, which corresponds to class of 'five' digits.

Similar JSON files can be generated with python script in <nctl_directory>/examples/ovms_inference:
```
cd <nctl_directory>/examples/ovms_inference
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```
And when venv is prepared invoke:
```
python generate_json.py --image_id <IMAGE ID>
```
`IMAGE ID` is a argument that determine with picture from MNIST will be used.

## Batch prediction
To perform batch prediction you have to generate proper protobuffers for inference.
This step is similar to [MNIST Data Preprocessing](batch_inf_example.md#mnist-data-preprocessing), but with one difference.
During model conversion to OV format, some information about model signatures is missing. To perform prediction on
the converted MNIST model, one additional parameter has to be used with `mnist_converter_pb.py`:
```
mnist_converter_pb.py --model_input_name="x/placeholder_port_0"
```

After file generation, move directory with .pb files to the `/input` mount point.

When all files are prepared, schedule prediction with:
```
nctl predict batch -n ovmsbatch -rt ovms --model-location /mnt/input/home/models/mnist --data /mnt/input/home/ovms_inference
```
Command above assumes that pb files are stored in `ovms_inference` directory in the `/input` shared folder.

When batch prediction hits the `FINISHED` state:
```
| Prediction instance         | Parameters   | Submission date        | Start date             | Duration     | Owner    | Status   | Template name            | Template version   |
|-----------------------------+--------------+------------------------+------------------------+--------------+----------+----------+--------------------------+--------------------|
| mnist-526-19-07-30-00-34-07 |              | 2019-07-30 12:34:35 AM | 2019-07-30 12:34:45 AM | 0d 0h 0m 17s | mzylowsk | COMPLETE | openvino-inference-batch | 0.1.0              |
```

Results are available in the `/output` mount point (check [Mount output instruction](mount_exp_output.md)).

## OVMS prediction with local model:
On Nauta platform models also can be forwarded without `/input` mount. This can be performed with `--local-model-location` option.
For example, scheduling stream prediction can be possible with command:
```
nctl predict launch -n localovms --runtime ovms --local-model-location /tmp/models/mnist/
```
Above command assumes MNIST in OV format is stored in /tmp/models/mnist.

----------------------

## Return to Start of Document

* [README](../README.md)

----------------------
