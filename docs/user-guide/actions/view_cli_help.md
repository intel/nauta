# Viewing CLI Commands Help

The –help command provides man-page style help for each dlsctl command. You can view help for any command and subcommand, and all related parameters.

Entering `dlsctl –help` provides a listing of all dlsctl commands (without subcommands), as shown next.

    $ dlsctl -h

    Usage: dlsctl COMMAND [OPTIONS] [ARGS]...

      Intel® Deep Learning Studio (Intel® DL Studio) Client

      To get further help on commands use COMMAND with -h or --help option.

    Options:
      -h, --help  Show this message and exit.

    Commands:
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
                       by dlsctl are installed in proper versions. If something is
                       missing, the application displays detailed information
                       about it.
      version, v       Displays the version of the installed dlsctl application.


You can view help for any command and available subcommand(s). The following example shows generic syntax; brackets are optional parameters, but [subcommand] requires [command].

`dlsctl [command_name] [subcommand] –help`

 
