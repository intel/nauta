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
from util.exceptions import KubernetesError
from util.logger import initialize_logger
from util.system import handle_error
from cli_text_consts import VersionCmdTexts as Texts


logger = initialize_logger(__name__)

# Timeout for version check request in seconds. This request is repeated 3 times.
PLATFORM_VERSION_REQUEST_TIMEOUT = 10


@click.command(help=Texts.HELP, short_help=Texts.HELP, cls=AliasCmd, alias='v')
@common_options(verify_dependencies=False, verify_config_path=False)
@pass_state
def version(state: State):
    """ Returns the version of the installed dlsctl application. """
    platform_version = Texts.INITIAL_PLATFORM_VERSION
    error_msg = ""
    platform_version_fail = False
    try:
        platform_version = DLS4EConfigMap(config_map_request_timeout=PLATFORM_VERSION_REQUEST_TIMEOUT).platform_version
    except KubernetesError:
        error_msg = Texts.KUBECTL_INT_ERROR_MSG
        platform_version_fail = True
    except Exception:
        error_msg = Texts.OTHER_ERROR_MSG
        platform_version_fail = True

    version_table = [[Texts.TABLE_APP_ROW_NAME, VERSION],
                     [Texts.TABLE_PLATFORM_ROW_NAME, platform_version]]

    click.echo(tabulate(version_table,
                        headers=Texts.TABLE_HEADERS,
                        tablefmt="orgtbl"))

    if platform_version_fail:
        handle_error(logger, error_msg, error_msg, add_verbosity_msg=state.verbosity == 0)
