#
# Copyright (c) 2019 Intel Corporation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

import os
import urllib3
import signal
import sys
import traceback
import click
import logging

import psutil

from commands.experiment import experiment
from commands.launch import launch
from commands.predict import predict
from commands.user import user
from commands.verify import verify
from commands.mount import mount
from commands.version import version
from util.aliascmd import AliasGroup
from util.logger import initialize_logger, setup_log_file, configure_logger_for_external_packages
from util.config import Config
from cli_state import verify_cli_config_path

logger = initialize_logger(__name__)

BANNER = """Intel® Deep Learning Studio (Intel® DL Studio) Client

            To get further help on commands use COMMAND with -h or --help option."""
CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'], ignore_unknown_options=True)
DEFAULT_LANG = "en_US.UTF-8"
DEFAULT_ENCODING = "UTF-8"

ERROR_MESSAGE = "Other error during starting application."
UTF_ERROR_MESSAGE = f"""Environment localization settings are incorrect. Please set following environment variables:
export LC_ALL={DEFAULT_LANG}
export LC_CTYPE={DEFAULT_LANG}

(en_US part can be replaced by your local language settings in <language>_<territory> format)

On Windows, run following command in order to enable UTF-8 encoding:
chcp 65001
"""


def signal_handler(sig, frame):
    """
    This function is responsible for handling SIGINT (e.g. when user press CTRL+C) and SIGTERM signals.
    :param sig: received signal
    :param frame: stack frame
    """
    logger.debug(f'Received signal {sig}.')
    for proc in psutil.Process(os.getpid()).children(recursive=True):
        logger.debug(f'Terminating {proc.pid} child process.')
        proc.send_signal(signal.SIGTERM)

    logger.debug(f'Finished handling signal {sig}.')
    sys.exit(0)


def configure_cli_logs():
    if os.environ.get('DLS_CTL_LOG_DISABLE'):
        return

    log_level = os.environ.get('DLS_CTL_FILE_LOG_LEVEL', default=logging.DEBUG)
    log_retention = os.environ.get('DLS_CTL_LOG_RETENTION', default=30)

    log_file_directory = os.environ.get('DLS_CTL_LOG_DIRECTORY')
    if not log_file_directory:
        verify_cli_config_path()
        log_file_directory = '{}/logs'.format(Config().config_path)

    if not os.path.isdir(log_file_directory):
        os.mkdir(log_file_directory)

    file_handler = setup_log_file(log_file_directory=log_file_directory, log_level=log_level,
                                  log_backup_count=log_retention)

    # CAN-1237 - by setting level of logs for k8s rest client to INFO I'm removing displaying content of
    # every rest request sent by k8s client
    configure_logger_for_external_packages(pack_name='kubernetes.client.rest',
                                           initial_log_level=logging.INFO,
                                           handlers=[file_handler])
    configure_logger_for_external_packages(pack_name='urllib3',
                                           initial_log_level=logging.CRITICAL,
                                           handlers=[file_handler])


@click.group(context_settings=CONTEXT_SETTINGS, cls=AliasGroup, help=BANNER,
             subcommand_metavar="COMMAND [options] [args]...")
def entry_point():
    configure_cli_logs()


entry_point.add_command(experiment.experiment)
entry_point.add_command(launch.launch)
entry_point.add_command(predict.predict)
entry_point.add_command(user.user)
entry_point.add_command(verify.verify)
entry_point.add_command(version)
entry_point.add_command(mount)

if __name__ == '__main__':
    # Register signal handler
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # at this moment we don't have all click's functions to handle parameters
    verbose_option = any(x.startswith("-vv") or x == "-v" or x == "--verbose" for x in sys.argv)
    try:
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        os.environ["PYTHONIOENCODING"] = DEFAULT_ENCODING

        entry_point()
    except (RuntimeError, UnicodeError) as exe:
        if type(exe) == RuntimeError and "was configured to use ASCII as encoding for the environment" not in str(exe):
            # Reraise exception if it is not related to encoding settings
            raise
        os.environ["LC_ALL"] = DEFAULT_LANG
        os.environ["LANG"] = DEFAULT_LANG
        os.environ["LANGUAGE"] = DEFAULT_LANG
        os.environ["LC_CTYPE"] = DEFAULT_LANG
        try:
            entry_point()
        except Exception as add_exe:
            # Print a message indicating problems with Encoding/Decoding settings
            print(UTF_ERROR_MESSAGE)
            logger.exception(ERROR_MESSAGE)
            print(ERROR_MESSAGE)
            if verbose_option:
                traceback.print_tb(add_exe.__traceback__)
        else:
            # click may not work here due to an exception
            print(ERROR_MESSAGE)
            if verbose_option:
                traceback.print_tb(exe.__traceback__)
    except Exception as exe:
        logger.exception(ERROR_MESSAGE)
        print(ERROR_MESSAGE)
        if verbose_option:
            traceback.print_tb(exe.__traceback__)
