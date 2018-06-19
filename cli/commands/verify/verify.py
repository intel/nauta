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

import sys

import click

from cli_state import common_options, pass_state, State
from util.dependencies_checker import check_dependency, DEPENDENCY_MAP
from util.logger import initialize_logger
from util.aliascmd import AliasCmd


HELP = "Command verifies whether all external components required by dlsctl are installed " \
       "in proper versions. If something is missing, the application displays detailed " \
       "information about it."

log = initialize_logger(__name__)


@click.command(short_help=HELP, cls=AliasCmd, alias='ver')
@common_options(verify_dependencies=False, verify_config_path=True)
@pass_state
def verify(state: State):
    for dependency_name, dependency_spec in DEPENDENCY_MAP.items():
        try:
            valid, installed_version = check_dependency(dependency_spec)
            if valid:
                click.echo(f'{dependency_name} verified successfully.')
            else:
                supported_versions_sign = '==' if dependency_spec.match_exact_version else '>='
                click.echo(f'{dependency_name} installed version ({installed_version}) '
                           f'was not tested, supported version {supported_versions_sign}'
                           f' {dependency_spec.expected_version}')
        except FileNotFoundError:
            error_msg = f'{dependency_name} is not installed.'
            log.exception(error_msg)
            click.echo(error_msg)
            sys.exit(1)
        except (RuntimeError, ValueError, TypeError):
            error_msg = f'Failed to get {dependency_name} version.'
            log.exception(error_msg)
            click.echo(error_msg)
            sys.exit(1)
