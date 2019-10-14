# Viewing the CLI Commands Help 

View man-page style help for any command and subcommand, and all related parameters by using the `--help` option.

This section discusses the following main topics:

 - [nctl Help Commands Overview](#nctl-help-commands-overview)
 - [Other nctl Commands](#other-nctl-commands)

## nctl Help Commands Overview

Entering the `nctl --help` or `nctl -h` command provides a listing of all nctl commands (without subcommands), as shown below.

     nctl -h
```
Usage: nctl COMMAND [options] [args]...

    Nauta Client

  Displays additional help information when the -h or --help COMMAND is
  used.

Options:
  -h, --help  Displays help messaging information.

Commands:
  config, cfg      Set limits and requested resources in templates.
  experiment, exp  Start, stop, or manage training jobs.
  launch, l        Launch the web user-interface or TensorBoard. Runs as a
                   process in the system console until the user stops the
                   process. To run in the background, add '&' at the end of
                   the line.
  model, mo        Manage the processing, conversion, and packaging of models.
  mount, m         Displays a command that can be used to mount a client's
                   folder on their local machine.
  predict, p       Start, stop, and manage prediction jobs and instances.
  template, tmp    Manage experiment templates used by the system.
  user, u          Create, delete, or list users of the platform. Can only be
                   run by a platform administrator.
  verify, ver      Verifies if all required external components contain the
                   proper installed versions.
  version, v       Displays the version of the installed nctl application.

```

You can view command-help for any command and available subcommand(s). The following example shows generic syntax; brackets are optional parameters, but a [subcommand] requires the [command] syntax.

`nctl [command_name] [subcommand] --help`

## Other nctl Commands

* [nctl config](config.md)
* [nctl experiment](experiment.md)
* [nctl launch](launch.md)
* [nctl model](model.md)
* [nctl mount](mount.md)
* [nctl predict](predict.md)
* [nctl template](template.md)
* [nctl user](user.md)
* [nctl verify](verify.md)
* [nctl version](version.md)

----------------------

## Return to Start of Document

* [README](../README.md)
---------------------- 
