# Exporting models

The section discusses how to transform a model from one format into another using `model export` functionality.

 - [Obtaining a model to be exported](#obtaining-a-model-to-be-exported)  
 - [Checking a list of available exports' formats](#checking-a-list-of-available-exports-formats)
 - [Exporting the model to openvino format](#exporting-the-model-to-openvino-format)
 
## Obtaining a model to be exported

First step in the flow of exporting models is to get a model that will be exported to another format. The easiest way
to get such a model is to create it using `mnist_saved_model.py` example script, which is delivered together with `nctl` 
application. This script trains model and then stores it on a shared folder. To generate the model use the following
command:

 `nctl exp submit examples/mnist_saved_model.py -sfl examples/ -n generate-model -- /mnt/output/experiment`

This command trains a model using TensorFlow framework and stores it in the `output/generate-model` shared folder. Passing
to this command an `-sfl` option is required, as the `mnist_saved_model.py` script requires a presence of a `mnist_input_data.py`
script which is located in a folder with examples in `nctl` distribution.

To check, whether the script has been created - mount locally the shared folder mentioned above and check, whether it contains
the `1` subfolder (the script generates only one model, which is stored in a folder named as an ordinary number of this model).    

## Checking a list of available exports' formats 

To check what are the available exports' formats use the following command:

 `nctl model export formats`

This command displays a list of formats - for example:

 ```
 | Name     | Parameters description                                                       |
 |----------+------------------------------------------------------------------------------|
 | openvino | --input_shape [x,y,....] - shape of an input                                 |
 |          | --input [name] - names of input layers                                       |
 |          | --output [name] - names of output layers                                     |
 |          | Rest of parameters can be found in a description of OpenVino model optimizer |
 ```
 
 ## Exporting the model to openvino format
 
The `model export formats` command shows, that we can export our model to `openvino` format. To do this use the 
 `model export` command in the following format:
 
 `nctl model export <model_location> <format> -- <format_specific_parameters>`
 
Where:
 - `<model_location>` - location of a model that is going to be exported
 - `<format>` - format of an exported model
 - `<format_specific_paramaters>` - parameters required during a process of an export. Their number and format depends
on a model and a chosen format.
  
To export the model created in the previous step, use the following command:
 
 `nctl model export /mnt/output/home/generate-model/1 openvino -- --input_shape [1,784] --input x --output y`
 
Parameters `input_shape`, `input` and `output` are required to perform a successful export to `openvino` format. First
describes a shape of an input vector of an exported model, second and third describes names of input and output vectors.
 
Successful execution of this command produces the following output (name of an operation is example - it may be different
as it is generated automatically by the system):

 ```
 | Operation     | Start date           | End date   | Owner     | State   |
 |---------------+----------------------+------------+-----------+---------|
 | openvino_1    | 2019-07-17T16:13:40Z |            | jdoe      | Queued  |
 
 Successfully created export workflow
 ```    

The export operation may take a while. To check its status use the following command:

`nctl model status`

This command returns a list of export operations with their statuses. If an export operation is finished, its status
is `Succeeded`. In such case an exported model can be found in the `output/openvino_1` shared folder - this folder 
contains the following files: `saved_model.bin`, `saved_model.mapping` and `saved_model.xml`. 

In case of any problems with an export operation, details of those issues can be found in logs from an export - to get them use
the following command:

`nctl model logs openvino_1`


----------------------

## Return to Start of Document

* [README](../README.md)

----------------------
