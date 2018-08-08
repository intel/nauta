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
from cli_state import common_options
from version import VERSION
from util.config import DLS4EConfigMap
from util.exceptions import KubectlIntError
from util.logger import initialize_logger

logger = initialize_logger(__name__)

HELP = "Displays the version of the installed dlsctl application."

# Timeout for version check request in seconds. This request is repeated 3 times.
PLATFORM_VERSION_REQUEST_TIMEOUT = 10


@click.command(short_help=HELP, cls=AliasCmd, alias='v')
@common_options(verify_dependencies=False, verify_config_path=False)
def version():
    """
    Returns the version of the installed dlsctl application.
    """
    platform_version = "Failed to get platform version."
    error_msg = ""
    platform_version_fail = False
    try:
        platform_version = DLS4EConfigMap(config_map_request_timeout=PLATFORM_VERSION_REQUEST_TIMEOUT).platform_version
    except KubectlIntError:
        error_msg = 'Platform version check failure may occur for example due to invalid path to kubectl config, ' \
                    'invalid k8s credentials or k8s cluster being unavailable. Check your KUBECONFIG environment ' \
                    'variable and make sure that the k8s cluster is online. Run this command with -v or -vv option ' \
                    'for more info.'
        logger.exception(error_msg)
        platform_version_fail = True
    except Exception:
        error_msg = 'Unexpected error occurred during platform version check. Use -v or -vv option for more info.'
        logger.exception(error_msg)
        platform_version_fail = True

    version_table = [["dlsctl application", VERSION],
                     ["dls4e platform", platform_version]]

    click.echo(tabulate(version_table,
                        headers=['Component', 'Version'],
                        tablefmt="orgtbl"))

    if platform_version_fail:
        click.echo(error_msg)
