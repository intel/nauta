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

from sys import exit

import click

from util.cli_state import common_options, pass_state, State
from util.dependencies_checker import check_dependency, get_dependency_map, check_os, save_dependency_versions
from util.logger import initialize_logger
from util.aliascmd import AliasCmd
from util.k8s.kubectl import check_connection_to_cluster
from util.k8s.k8s_proxy_context_manager import check_port_forwarding
from util.k8s.k8s_info import get_kubectl_current_context_namespace, is_current_user_administrator
from util.spinner import spinner
from util.system import handle_error
from util.template import verify_values_in_packs
from cli_text_consts import VerifyCmdTexts as Texts
from util.exceptions import KubectlConnectionError, InvalidOsError, InvalidOsVersionError


logger = initialize_logger(__name__)


@click.command(short_help=Texts.HELP, help=Texts.HELP, cls=AliasCmd, alias='ver', options_metavar='[options]')
@common_options(verify_dependencies=False, verify_config_path=True)
@pass_state
def verify(state: State):
    try:
        with spinner(text=Texts.CHECKING_OS_MSG):
            check_os()
        click.echo(Texts.OS_SUPPORTED_MSG)
    except InvalidOsVersionError as exception:
        handle_error(logger, str(exception), str(exception), add_verbosity_msg=True)
    except InvalidOsError as exception:
        handle_error(logger, str(exception), str(exception), add_verbosity_msg=True)
        exit(1)

    dependencies = get_dependency_map()
    kubectl_dependency_name = 'kubectl'
    kubectl_dependency_spec = dependencies[kubectl_dependency_name]

    try:
        with spinner(text=Texts.VERIFYING_DEPENDENCY_MSG.format(dependency_name=kubectl_dependency_name)):
            valid, installed_version = check_dependency(dependency_name=kubectl_dependency_name,
                                                        dependency_spec=kubectl_dependency_spec)
    except FileNotFoundError:
        handle_error(logger, Texts.KUBECTL_NOT_INSTALLED_ERROR_MSG, Texts.KUBECTL_NOT_INSTALLED_ERROR_MSG,
                     add_verbosity_msg=state.verbosity == 0)
        exit(1)

    supported_versions_sign = '>='
    logger.info(
        Texts.VERSION_CHECKING_MSG.format(
            dependency_name=kubectl_dependency_name, installed_version=installed_version,
            supported_versions_sign=supported_versions_sign,
            expected_version=kubectl_dependency_spec.expected_version
        )
    )

    if valid:
        click.echo(Texts.DEPENDENCY_VERIFICATION_SUCCESS_MSG.format(dependency_name=kubectl_dependency_name))
    else:
        handle_error(logger,
                     Texts.KUBECTL_INVALID_VERSION_ERROR_MSG.format(installed_version=installed_version,
                                                                    supported_versions_sign=supported_versions_sign,
                                                                    expected_version=  # noqa
                                                                    kubectl_dependency_spec.expected_version),
                     Texts.KUBECTL_INVALID_VERSION_ERROR_MSG.format(installed_version=installed_version,
                                                                    supported_versions_sign=supported_versions_sign,
                                                                    expected_version=  # noqa
                                                                    kubectl_dependency_spec.expected_version),
                     add_verbosity_msg=state.verbosity == 0)
        exit(1)

    del dependencies[kubectl_dependency_name]

    try:
        with spinner(text=Texts.CHECKING_CONNECTION_TO_CLUSTER_MSG):
            check_connection_to_cluster()
        with spinner(text=Texts.CHECKING_PORT_FORWARDING_FROM_CLUSTER_MSG):
            check_port_forwarding()
    except KubectlConnectionError as e:
        handle_error(logger, str(e), str(e), add_verbosity_msg=state.verbosity == 0)
        exit(1)

    try:
        namespace = 'kube-system' if is_current_user_administrator() else get_kubectl_current_context_namespace()
    except Exception:
        handle_error(logger, Texts.GET_K8S_NAMESPACE_ERROR_MSG, Texts.GET_K8S_NAMESPACE_ERROR_MSG,
                     add_verbosity_msg=state.verbosity == 0)
        exit(1)

    dependency_versions = {}
    for dependency_name, dependency_spec in dependencies.items():
        try:
            supported_versions_sign = '==' if dependency_spec.match_exact_version else '>='
            with spinner(text=Texts.VERIFYING_DEPENDENCY_MSG.format(dependency_name=dependency_name)):
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
                         add_verbosity_msg="client" not in dependency_name)
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

    try:
        list_of_incorrect_packs = None
        with spinner(text=Texts.VERIFYING_RESOURCES_CORRECTNESS):
            list_of_incorrect_packs = verify_values_in_packs()
        if list_of_incorrect_packs:
            click.echo(Texts.INCORRECT_PACKS_EXIST)
            for incorrect_pack in list_of_incorrect_packs:
                click.echo(incorrect_pack)
            exit(1)
        else:
            click.echo(Texts.DEPENDENCY_VERIFICATION_SUCCESS_MSG.format(dependency_name="packs resources' correctness"))
    except Exception as e:
        handle_error(logger, str(e), str(e), add_verbosity_msg=state.verbosity == 0)
        exit(1)
