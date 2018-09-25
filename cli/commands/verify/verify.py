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

from sys import exit

import click

from cli_state import common_options, pass_state, State
from util.dependencies_checker import check_dependency, DEPENDENCY_MAP, check_os
from util.logger import initialize_logger
from util.aliascmd import AliasCmd
from util.k8s.kubectl import check_connection_to_cluster
from util.k8s.k8s_info import get_kubectl_current_context_namespace, is_current_user_administrator
from util.system import handle_error
from cli_text_consts import VERIFY_CMD_TEXTS as TEXTS
from util.exceptions import KubectlConnectionError, InvalidOsError


logger = initialize_logger(__name__)


@click.command(short_help=TEXTS["help"], help=TEXTS["help"], cls=AliasCmd, alias='ver')
@common_options(verify_dependencies=False, verify_config_path=True)
@pass_state
def verify(state: State):
    try:
        check_connection_to_cluster()
    except KubectlConnectionError as e:
        handle_error(logger, str(e), str(e), add_verbosity_msg=state.verbosity == 0)
        exit(1)
    except FileNotFoundError:
        handle_error(logger, TEXTS["kubectl_not_installed_error_msg"], TEXTS["kubectl_not_installed_error_msg"],
                     add_verbosity_msg=state.verbosity == 0)
        exit(1)

    try:
        namespace = 'kube-system' if is_current_user_administrator() else get_kubectl_current_context_namespace()
    except Exception:
        handle_error(logger, TEXTS["get_k8s_namespace_error_msg"], TEXTS["get_k8s_namespace_error_msg"],
                     add_verbosity_msg=state.verbosity == 0)
        exit(1)

    try:
        check_os()
        click.echo(TEXTS["os_supported_msg"])
    except InvalidOsError as exception:
        handle_error(logger, str(exception), str(exception), add_verbosity_msg=True)
        exit(1)

    for dependency_name, dependency_spec in DEPENDENCY_MAP.items():
        try:
            supported_versions_sign = '==' if dependency_spec.match_exact_version else '>='
            valid, installed_version = check_dependency(dependency_spec, namespace=namespace)
            logger.info(
                TEXTS["version_checking_msg"].format(
                    dependency_name=dependency_name, installed_version=installed_version,
                    supported_versions_sign=supported_versions_sign,
                    expected_version=dependency_spec.expected_version
                )
            )
            if valid:
                click.echo(TEXTS["dependency_verification_success_msg"].format(dependency_name=dependency_name))
            else:
                click.echo(
                    TEXTS["invalid_version_warning_msg"].format(
                        dependency_name=dependency_name, installed_version=installed_version,
                        supported_versions_sign=supported_versions_sign,
                        expected_version=dependency_spec.expected_version
                    )
                )
        except FileNotFoundError:
            handle_error(logger, TEXTS["dependency_not_installed_error_msg"].format(dependency_name=dependency_name),
                         TEXTS["dependency_not_installed_error_msg"].format(dependency_name=dependency_name),
                         add_verbosity_msg=state.verbosity == 0)
            exit(1)
        except (RuntimeError, ValueError, TypeError):
            handle_error(logger, TEXTS["dependency_version_check_error_msg"].format(dependency_name=dependency_name),
                         TEXTS["dependency_version_check_error_msg"].format(dependency_name=dependency_name),
                         add_verbosity_msg=state.verbosity == 0)
            exit(1)
        except Exception:
            handle_error(logger,
                         TEXTS["dependency_verification_other_error_msg"].format(dependency_name=dependency_name),
                         TEXTS["dependency_verification_other_error_msg"].format(dependency_name=dependency_name),
                         add_verbosity_msg=state.verbosity == 0)
            exit(1)
