# Viewing CLI Commands Help

The `--help` command provides man-page style help for each nctl command. You can view help for any command and subcommand, and all related parameters.

This sections discusses the following main topics:

 - [nctl Help Commands Overview](#nctl-help-commands-overview)
 - [Other nctl Commands](#other-nctl-commands)  

## nctl Help Commands Overview

Access help for any command with the --help or -h parameter. The help option provides a list of options available and brief descriptions for each nctl command.

     nctl -h
```
   Usage: nctl COMMAND [options] [args]...

  Nauta Client

 Displays additional help information when the -h or --help COMMAND is used.

Options:
  -h, --help Displays help messaging information.

Commands:
  config, cfg      Set limits and requested resources in templates.          
  experiment, exp  Start, stop, or manage training jobs.   
  launch, l        Launch the web user-interface or TensorBoard. Runs as a process 
                   in the system console until the user stops the process. 
                   To run in the background, add '&' at the end of the line.
  mount, m         Displays a command to mount folders on a local machine.
  predict, p       Start, stop, and manage prediction jobs and instances.
  user, u          Create, delete, or list users of the platform. 
                   Can only be run by a platform administrator.
  verify, ver      Verifies whether all required external components contain 
                   the proper versions installed.
  version, v       Displays the version of the installed nctl application.

```

You can view help for any command and available subcommand(s). The following example shows generic syntax; brackets are optional parameters, but [subcommand] requires [command].

`nctl [command_name] [subcommand] --help`

## Other nctl Commands

* [nctl experiment](experiment.md)
* [nctl launch](launch.md)
* [nctl mount](mount.md)
* [nctl predict](predict.md)
* [nctl user](user.md)
* [nctl verify](verify.md)
* [nctl version](version.md)

----------------------

## Return to Start of Document

* [README](../README.md)

----------------------

