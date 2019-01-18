# launch Command

This command launches a browser for Web UI or Tensorboard.

- [webui Subcommand](#webui-subcommand)  
- [tensorboard Subcommand](#tensorboard-subcommand)

## webui Subcommand

- [Synopsis](#synopsis)  
- [Arguments](#arguments)  
- [Options](#options)
- [Returns](#returns)
- [Examples](#examples)  

### Synopsis

Launches the Nauta web user interface with credentials.

### Syntax

`nctl launch webui [options]`

### Arguments

None.

### Options
 
 | Name | Required | Description | 
 |:--- |:--- |:--- |
 |`--no-launch` | No | Run this command without a web browser starting; only proxy tunnel is created.
 |`-p, --port <port>` <br> `INTEGER RANGE`| No | If given, application will be exposed on a local machine under [port] port.|
 |`-v, --verbose`| No | Set verbosity level: <br>`-v` for INFO, <br>`-vv` for DEBUG |
 |`-h, --help` | No | Show help message and exit. |
 
### Returns

Link to an exposed application. 

### Examples

`nctl launch webui`

This command returns a Go-to URL. The following is an example only:
<!-- language: lang-none -->
```
Launching...Go to http://localhost:14000?token=eyJhbGciOiJSUzI1NiIsImtpZCI6IiJ9.eyJpc3MiOiJrd
WJlcm5ldVzL3NlcnZpY2VhY2NvdW50Iiwia3ViZXJuZXRlcy5pby9zZXJ2aWNlYWNjb3VudC9uY
W1lc3BhY2UiOiJiZXRoYW55Iiwia3ViZXJuZXRlcy5pby9zZXJ2aWNlYWNjb3VudC9zZWNyZXQu
NlcnZpY2Ut…
Proxy connection created.
Press Ctrl-C key to close a port forwarding process...
``` 

## tensorboard Subcommand 

- [Synopsis](#synopsis_tb)  
- [Arguments](#arguments_tb)  
- [Options](#options_tb)
- [Returns](#returns_tb)
- [Examples](#example_tb)  

### <a name="synopsis_tb"></a>Synopsis

Launches the TensorBoard* web user interface front end with credentials, with the indicated experiment loaded. 

### <a name="syntax_tb"> </a> Syntax

Format of the command is as follows:

`nctl launch tensorboard [options] EXPERIMENT NAME`

### <a name="arguments_tb"> </a> Arguments

| Name | Required | Description |
|:--- |:--- |:--- |
|`EXPERIMENT NAME` | Yes | Experiment name

A user can pass one or more names of experiments separated with spaces. If experiment that should
be displayed in Tensorboard belongs to a current user - user has to give only its name. If this experiment
is owned by another user - name of an experiment should be preceded with a name of this second user
in the following format : `username/experiment_name`

### <a name="options_tb"> </a>Options
 
 | Name | Required | Description | 
 |:--- |:--- |:--- |
 |`--no-launch` | No | To create tunnel without launching web browser. |
 |`-tscp` <br>` --tensorboard-service-client-port` <br> `INTEGER RANGE`  | No | Local port on which tensorboard service client will be started. |
 |` -p, --port INTEGER RANGE` | No | Port on which service will be exposed locally. |
 |`-v, --verbose`| No | Set verbosity level: <br>`-v` for INFO, <br>`-vv` for DEBUG |
 |`-h, --help` | No | Show help message and exit. |
 
 
### <a name="returns_tb"> </a>Returns

Link to an exposed application. 

### <a name="example_tb"> </a> Example

`nctl launch tensorboard experiment75`

An example might look like the following:
<!-- language: lang-none -->

    http://127.0.0.1/tensorboard/token=AB123CA27F  
