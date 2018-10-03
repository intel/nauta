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
from util.dependencies_checker import check_dependency, DEPENDENCY_MAP, check_os, save_dependency_versions
from util.logger import initialize_logger
from util.aliascmd import AliasCmd
from util.k8s.kubectl import check_connection_to_cluster
from util.k8s.k8s_info import get_kubectl_current_context_namespace, is_current_user_administrator
from util.system import handle_error
from cli_text_consts import VerifyCmdTexts as Texts
from util.exceptions import KubectlConnectionError, InvalidOsError


logger = initialize_logger(__name__)


@click.command(short_help=Texts.HELP, help=Texts.HELP, cls=AliasCmd, alias='ver')
@common_options(verify_dependencies=False, verify_config_path=True)
@pass_state
def verify(state: State):
    try:
        check_connection_to_cluster()
    except KubectlConnectionError as e:
        handle_error(logger, str(e), str(e), add_verbosity_msg=state.verbosity == 0)
        exit(1)
    except FileNotFoundError:
        handle_error(logger, Texts.KUBECTL_NOT_INSTALLED_ERROR_MSG, Texts.KUBECTL_NOT_INSTALLED_ERROR_MSG,
                     add_verbosity_msg=state.verbosity == 0)
        exit(1)

    try:
        namespace = 'kube-system' if is_current_user_administrator() else get_kubectl_current_context_namespace()
    except Exception:
        handle_error(logger, Texts.GET_K8S_NAMESPACE_ERROR_MSG, Texts.GET_K8S_NAMESPACE_ERROR_MSG,
                     add_verbosity_msg=state.verbosity == 0)
        exit(1)

    try:
        check_os()
        click.echo(Texts.OS_SUPPORTED_MSG)
    except InvalidOsError as exception:
        handle_error(logger, str(exception), str(exception), add_verbosity_msg=True)
        exit(1)

    dependency_versions = {}
    for dependency_name, dependency_spec in DEPENDENCY_MAP.items():
        try:
            supported_versions_sign = '==' if dependency_spec.match_exact_version else '>='
            valid, installed_version = check_dependency(dependency_name=dependency_name,
                                                        dependency_spec=dependency_spec, namespace=namespace)
            dependency_versions[dependency_name] = installed_version
            logger.info(
                Texts.VERSION_CHECKING_MSG.format(
                    dependency_name=dependency_name, installed_version=installed_version,
                    supported_versions_sign=supported_versions_sign,
                    expected_version=dependency_spec.expected_version
                )
            )
            if valid:
                click.echo(Texts.DEPENDENCY_VERIFICATION_SUCCESS_MSG.format(dependency_name=dependency_name))
            else:
                click.echo(
                    Texts.INVALID_VERSION_WARNING_MSG.format(
                        dependency_name=dependency_name, installed_version=installed_version,
                        supported_versions_sign=supported_versions_sign,
                        expected_version=dependency_spec.expected_version
                    )
                )
        except FileNotFoundError:
            handle_error(logger, Texts.DEPENDENCY_NOT_INSTALLED_ERROR_MSG.format(dependency_name=dependency_name),
                         Texts.DEPENDENCY_NOT_INSTALLED_ERROR_MSG.format(dependency_name=dependency_name),
                         add_verbosity_msg=state.verbosity == 0)
            exit(1)
        except (RuntimeError, ValueError, TypeError):
            handle_error(logger, Texts.DEPENDENCY_VERSION_CHECK_ERROR_MSG.format(dependency_name=dependency_name),
                         Texts.DEPENDENCY_VERSION_CHECK_ERROR_MSG.format(dependency_name=dependency_name),
                         add_verbosity_msg=state.verbosity == 0)
            exit(1)
        except Exception:
            handle_error(logger,
                         Texts.DEPENDENCY_VERIFICATION_OTHER_ERROR_MSG.format(dependency_name=dependency_name),
                         Texts.DEPENDENCY_VERIFICATION_OTHER_ERROR_MSG.format(dependency_name=dependency_name),
                         add_verbosity_msg=state.verbosity == 0)
            exit(1)
    else:
        # This block is entered if all dependencies were validated successfully
        # Save dependency versions in a file
        save_dependency_versions(dependency_versions)
