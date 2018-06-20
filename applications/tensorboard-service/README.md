# Tensorboard service

Tensorboard service is an API service which manages Tensorboard instances for viewing runs' statistics.

* Creates on-demand Tensorboard instances for user
* Manages running Tensorboard instances and deletes them if not used for certain period of time


## API

### Create Tensorboard instance

* `run name` - name of a run from which logs should be connected to tensorboard

### Request
    POST /create/{run name}
### Response
    Status: 200 OK
    {
      "url": "..."
    }


## Design

Tensorboard service is an instance of a pod containing 2 containers:

* api service - handles tensorboard creation requests from user
* garbage collector - daemon process which checks stale Tensorboard instances and deletes their resources after
some time of inactivity

Every platform user has tensorboard service running in own namespace due to authentication and isolation from other
namespaces.

API service, when receiving creation request, creates a deployment of tensorboard in current namespace. The deployment
defines tensorboard pod, which has volume mounted with run's outputs used further by tensorboard. Since
directories in `output-home` volume are created with runs' names, it can be simply mapped to which path
tensorboard pod should be mounted.

Tensorboard sessions are automatically closed after 30 mins of inactivity. Activity is deducted from Tensorboard's logs,
where request/response serving activity can be parsed and compared with current time. Tensorboard pods and all related
resources are freed by garbage collector.
