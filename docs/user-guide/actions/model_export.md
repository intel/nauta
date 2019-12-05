# Exporting Models

The section discusses how to transform a model from one format to another using the `model export` functionality.

 - [Obtaining a Model For Exporting](#obtaining-a-model-for-exporting)  
 - [Checking a list of Available Exports' Formats](#checking-a-list-of-available-exports-formats)
 - [Exporting the model to OpenVINO format](#exporting-the-model-to-openvino-format)
 
## Obtaining a Model For Exporting

To use the flow for exporting models, select a model that will export to another format. To successfully do this, create
a model using the `mnist_saved_model.py` example script, which is delivered together with `nctl` application. This script 
trains the model and then stores it in a shared folder. 

To generate the model, use the following command:
 
 `nctl exp submit examples/mnist_saved_model.py -sfl examples/ -n generate-model -- /mnt/output/experiment`
 
This command trains a model using TensorFlow framework and stores it in the `output/generate-model` shared folder. Passing 
this  command the `-sfl` (`--script-folder-location`) option is required, as the `mnist_saved_model.py` script requires the presence of the `mnist_input_data.py` script. This script is located in a folder with examples in the nctl distribution.
 
To check whether the script has been created, mount the locally shared folder (referenced above)  and check if it contains 
the _One_ subfolder (the script generates only _One_ model, which is stored in a folder named as an ordinary number 
of this model).

## Checking a List of Available Exports' Formats 

To check what are the available exports' formats, execute the following command:

 `nctl model export formats`

This command displays a list of formats, for example:

 ```
 | Name     | Parameters description                                                       |
 |----------+------------------------------------------------------------------------------|
 | openvino | --input_shape [x,y,....] - shape of an input                                 |
 |          | --input [name] - names of input layers                                       |
 |          | --output [name] - names of output layers                                     |
 |          | Rest of parameters can be found in a description of OpenVino model optimizer |
 ```
 
 ## Exporting the Model to OpenVINO Format
 
The `model export formats` command shows that you can export the model to `openvino` format. Use the `model export` command in the following format to export the model.
 
 `nctl model export <model_location> <format> -- <format_specific_parameters>`
 
_Where:_
 - `<model_location>` - This is the location of a model that is going to be exported.
 - `<format>` - This is the format of the exported model. 
 - `<format_specific_paramaters>` -  These are the parameters required during the export process. Their number and format is dependent on the model and the chosen format. 
  
To export the model created in the previous step, use the following command (scroll to the right to see full contents):
 
```
 nctl model export /mnt/output/home/generate-model/1 openvino -- --input_shape [1,784] --input x --output y
 
```
 
The parameters `input_shape`, `input` and `output` are required to perform a successful export to `openvino` format. 
 - `input_shape` - Describes the shape of the input vector of the exported model.
 - `input`, `output` - Describes the names of input and output vectors.
 
Successful execution of this command produces the following output: 

 ```
 | Operation     | Start date           | End date   | Owner     | State   |
 |---------------+----------------------+------------+-----------+---------|
 | openvino_1    | 2019-07-17T16:13:40Z |            | jdoe      | Queued  |
 
 Successfully created export workflow
 ```    

**Note:** The name of the operation is just an example, your naming may differ from the example.

The duration of the export operation depends on a chosen format. To check the status of the operation, use the following command:

`nctl model status`

This command returns a list of export operations with their statuses. If an export operation is finished, its status 
is `Succeeded`. When this occurs, an exported model can be found in the `output/openvino_1` shared folder. 
This folder contains the following files: `saved_model.bin`, `saved_model.mapping` and `saved_model.xml`. 

If you export the operation and issues occur, details of those issues can be found in the logs from an export. To review the logs and issues, use the following command:

`nctl model logs openvino_1`


----------------------

## Return to Start of Document

* [README](../README.md)

----------------------
