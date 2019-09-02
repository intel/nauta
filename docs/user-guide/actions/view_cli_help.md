# Viewing CLI Commands Help

The `--help` command provides man-page style help for each nctl command. You can view help for any command and subcommand, and all related parameters.

This section discusses the following main topics:

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
      config, cfg      Sets values of limits and requests for resources in templates 
                       used by the system.
      experiment, exp  Command for starting, stopping, and managing training jobs.
      launch, l        Command for launching web user-interface or tensorboard. It
                       works as process in the system console until user does not
                       stop it. If process should be run as background process,
                       please add '&' at the end of line
      mount, m         Displays a command that can be used to mount client's
                       folders on his/her local machine.
      predict, p       Command for starting, stopping, and managing prediction
                       jobs and instances. To get further help on commands use
                       COMMAND with -h or --help option.
      template, tmp    Command for handling templates used by the system.
      user, u          Command for creating/deleting/listing users of the
                       platform. Can only be run by a platform administrator.
      verify, ver      Command verifies whether all external components required
                       by nctl are installed in proper versions. If something is
                       missing, the application displays detailed information
                       about it.
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

## Return to Start of Document


----------------------

## Return to Start of Document

* [README](../README.md)
---------------------- 
