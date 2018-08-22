#
# INTEL CONFIDENTIAL
# Copyright (c) 2018 Intel Corporation
#
# The source code contained or described herein and all documents related to
# the source code ("Material") are owned by Intel Corporation or its suppliers
# or licensors. Title to the Material remains with Intel Corporation or its
# suppliers and licensors. The Material contains trade secrets and proprietary
# and confidential information of Intel or its suppliers and licensors. The
# Material is protected by worldwide copyright and trade secret laws and treaty
# provisions. No part of the Material may be used, copied, reproduced, modified,
# published, uploaded, posted, transmitted, distributed, or disclosed in any way
# without Intel's prior express written permission.
#
# No license under any patent, copyright, trade secret or other intellectual
# property right is granted to or conferred upon you by disclosure or delivery
# of the Materials, either expressly, by implication, inducement, estoppel or
# otherwise. Any license under such intellectual property rights must be express
# and approved by Intel in writing.
#

import click
from tabulate import tabulate

from util.aliascmd import AliasCmd
from cli_state import common_options, pass_state, State
from version import VERSION
from util.config import DLS4EConfigMap
from util.exceptions import KubectlIntError
from util.logger import initialize_logger
from util.system import handle_error
from cli_text_consts import VERSION_CMD_TEXTS as TEXTS


logger = initialize_logger(__name__)

# Timeout for version check request in seconds. This request is repeated 3 times.
PLATFORM_VERSION_REQUEST_TIMEOUT = 10


@click.command(help=TEXTS["help"], short_help=TEXTS["help"], cls=AliasCmd, alias='v')
@common_options(verify_dependencies=False, verify_config_path=False)
@pass_state
def version(state: State):
    """ Returns the version of the installed dlsctl application. """
    platform_version = TEXTS["initial_platform_version"]
    error_msg = ""
    platform_version_fail = False
    try:
        platform_version = DLS4EConfigMap(config_map_request_timeout=PLATFORM_VERSION_REQUEST_TIMEOUT).platform_version
    except KubectlIntError:
        error_msg = TEXTS["kubectl_int_error_msg"]
        platform_version_fail = True
    except Exception:
        error_msg = TEXTS["other_error_msg"]
        platform_version_fail = True

    version_table = [[TEXTS["table_app_row_name"], VERSION],
                     [TEXTS["table_platform_row_name"], platform_version]]

    click.echo(tabulate(version_table,
                        headers=TEXTS["table_headers"],
                        tablefmt="orgtbl"))

    if platform_version_fail:
        handle_error(logger, error_msg, error_msg, add_verbosity_msg=state.verbosity == 0, exit_code=None)
