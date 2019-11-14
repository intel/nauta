# launch Command

The `launch` command launches a browser for Web UI or TensorBoard. The following main topics are discussed in this section:

- [webui Subcommand](#webui-subcommand)  
- [tensorboard Subcommand](#tensorboard-subcommand)

## webui Subcommand

### Synopsis

The `webui` subcommand launches the Nauta web user interface with credentials. 

**Note:** If you are using CLI through remote access, you will need to setup an X server for tunneling over SSH with port forwarding or use SSH Proxy command tunneling. After establishing a tunnel from the gateway to your local machine, you can use the URL provided by this command. 

### Syntax

`nctl launch webui [options]`

### Arguments

None.

### Options
 
 | Name | Required | Description | 
 |:--- |:--- |:--- |
 |`--no-launch` | No | Run this command without a web browser starting; only proxy tunnel is created.
 |`-p, --port INTEGER RANGE` | No | If given, the application will be exposed on a local machine under [port] port.|
 |`-f, --force`| No | Ignore (most) confirmation prompts during command execution |
 |`-v, --verbose`| No | Set verbosity level: <br>`-v` for INFO, <br>`-vv` for DEBUG |
 |`-h, --help` | No | Displays help messaging information. |
 
### Returns

Link to an exposed application. 

### Examples

`nctl launch webui`

This command returns a Go-to URL. The following is an example only:

```
Launching...Go to http://localhost:14000?token=eyJhbGciOiJSUzI1NiIsImtpZCI6IiJ9.eyJpc3MiOiJrd
WJlcm5ldVzL3NlcnZpY2VhY2NvdW50Iiwia3ViZXJuZXRlcy5pby9zZXJ2aWNlYWNjb3VudC9uY
W1lc3BhY2UiOiJiZXRoYW55Iiwia3ViZXJuZXRlcy5pby9zZXJ2aWNlYWNjb3VudC9zZWNyZXQu
NlcnZpY2Ut…
Proxy connection created.
Press Ctrl-C key to close a port forwarding process...
``` 

## tensorboard Subcommand 

### Synopsis

The `tensorboard` subcommand launches the TensorBoard web user interface front end with credentials, with the indicated experiment loaded. 

**Note:** If you are using CLI through remote access, you will need to setup an X server for tunneling over SSH with port forwarding or use SSH Proxy command tunneling. After establishing a tunnel from the gateway to your local machine, you can use the URL provided by this command.

### Syntax

Format of the command is as follows:

`nctl launch tensorboard [options] EXPERIMENT-NAME`

### Arguments

| Name | Required | Description |
|:--- |:--- |:--- |
|`EXPERIMENT-NAME` | Yes | Experiment name

A user can pass one or more names of experiments separated with spaces. If an experiment that should
be displayed in TensorBoard belongs to a current user, the user has to give only its name. If this experiment
is owned by another user, the name of an experiment should be preceded with a name of this second user
in the following format: `username/experiment-name`

### Options
 
 | Name | Required | Description | 
 |:--- |:--- |:--- |
 |`--no-launch` | No | To create tunnel without launching web browser. |
 |`-tscp` <br>` --tensorboard-service-client-port` <br> `INTEGER RANGE`  | No | Local port on which TensorBoard service client will be started. |
 |`-p, --port INTEGER RANGE` <br> | No | Port on which service will be exposed locally. |
 |`-f, --force`| No | Ignore (most) confirmation prompts during command execution |
 |`-v, --verbose`| No | Set verbosity level: <br>`-v` for INFO, <br>`-vv` for DEBUG |
 |`-h, --help` | No | Displays help messaging information. |
 

### Returns

Link to an exposed application. 

### Example

`nctl launch tensorboard experiment75`

An example might appear as:
```
http://127.0.0.1/tensorboard/token=AB123CA27F
```

----------------------

## Return to Start of Document

* [README](../README.md)
----------------------
