# Viewing CLI Commands Help

The `--help` command provides man-page style help for each nctl command. You can view help for any command and subcommand, and all related parameters.

Entering `nctl --help` or `nctl -h` provides a listing of all nctl commands (without subcommands), as shown next.

    $ nctl -h

    Usage: nctl COMMAND [OPTIONS] [ARGS]...

     Nauta Client
     
     To get further help on commands use COMMAND with -h or --help option.

    Options:
      -h, --help  Show this message and exit.

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
      user, u          Command for creating/deleting/listing users of the
                       platform. Can only be run by a platform administrator.
      verify, ver      Command verifies whether all external components required
                       by nctl are installed in proper versions. If something is
                       missing, the application displays detailed information
                       about it.
      version, v       Displays the version of the installed nctl application.


You can view help for any command and available subcommand(s). The following example shows generic syntax; brackets are optional parameters, but [subcommand] requires [command].

`nctl [command_name] [subcommand] --help`

## Overview of the nctl Commands

* [nctl experiment](experiment.md)
* [nctl launch](launch.md)
* [nctl mount](mount.md)
* [nctl predict](predict.md)
* [nctl user](user.md)
* [nctl verify](verify.md)
* [nctl version](version.md)

