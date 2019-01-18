# Basic Concepts

The following concepts and terms are relevant to using this software.

## User

The user is a data scientist who wants to perform deep learning experiments to train models that will, after training and testing, be deployed in production. Using Nauta, the user can define and schedule containerized deep learning experiments using Kubernetes* on single or multiple worker nodes, and check the status and results of those experiments to further adjust and run additional experiments, or prepare the trained model for deployment.

## Administrator

The administrator or admin creates and monitors users and resources. Admins cannot be users (data scientists), and are not permitted to perform any of the user experiments or related tasks. Also, users (data scientists) cannot be admins. An admin who wants to run experiments must create a separate user account for that purpose.

## Resources
In this context, resources are the system compute and memory resources the user will assign to a model training experiment. The user can specify the number of processing nodes and the amount of SDRAM in the system that will be reserved for a given experiment or job. The job will not be allowed to exceed the specified memory limit. In a multi-user environment, care should be taken to not dedicate too many resources to a given job, because other applications and services may be impacted.

## Data
Data is the set of observations used to run experiments to train, test and validate your model. Unlabeled data is used in inference and prediction. 

## Experiments
Performing deep learning experimentation is what the Nauta application was developed for, and each experiment is executed by a deep learning script. You can run a single experiment, or run multiple experiments in parallel using the same script, or run different multiple experiments with different scripts. The script needs to be tailored to process whatever data you are using to train your model.

## Predictions
After experiments have been run and the model has been trained, you can pass in new (unlabeled) data exemplars, to obtain predicted labels and other details returned. This process is called inference. In general, generating predictions involves pre-processing the new input data, running it through the model, and then collecting the results from the last layer of the network.

The Nauta software supports both batch and streaming inference. Batch inference involves processing a set of prepared input data to a referenced trained model and writing the inference results to a folder. Streaming inference is where the user deploys the model on the system and processes singular data as it is received.
 
