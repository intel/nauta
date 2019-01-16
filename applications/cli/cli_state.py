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

from functools import wraps
import sys

import click

from util.logger import set_verbosity_level, initialize_logger
from util.config import Config, ConfigInitError
from util.dependencies_checker import check_all_binary_dependencies, check_os
from util.k8s.k8s_info import get_kubectl_current_context_namespace, is_current_user_administrator
from util.exceptions import InvalidDependencyError, InvalidOsError
from util.system import handle_error
from cli_text_consts import CliStateTexts as Texts

logger = initialize_logger(__name__)

# Timeout for dependency verification request in seconds. This request is repeated 3 times.
VERIFY_REQUEST_TIMEOUT = 10


class State:
    def __init__(self):
        self.verbosity = 0


pass_state = click.make_pass_decorator(State, ensure=True)


def verbosity_option(f):
    def callback(ctx, param, value):
        set_verbosity_level(value)
        return value

    return click.option('-v', '--verbose', count=True,
                        expose_value=False,
                        help='Set verbosity level: \n -v for INFO \n -vv for DEBUG',
                        callback=callback)(f)


def verify_cli_dependencies():
    try:
        namespace = 'kube-system' if is_current_user_administrator(request_timeout=VERIFY_REQUEST_TIMEOUT) \
            else get_kubectl_current_context_namespace()
    except Exception:
        error_msg = Texts.KUBECTL_NAMESPACE_ERROR_MSG
        handle_error(logger, error_msg, error_msg, add_verbosity_msg=True)
        sys.exit(1)
    try:
        check_os()
        check_all_binary_dependencies(namespace=namespace)
    except (InvalidDependencyError, InvalidOsError):
        error_msg = Texts.INVALID_DEPENDENCY_ERROR_MSG
        handle_error(logger, error_msg, error_msg, add_verbosity_msg=True)


def verify_cli_config_path():
    try:
        config = Config()
        if not config.config_path:
            raise ConfigInitError(Texts.NCTL_CONFIG_NOT_SET_ERROR_MSG)
    except ConfigInitError as e:
        error_msg = Texts.NCTL_CONFIG_INIT_ERROR_MSG.format(exception_msg=str(e))
        handle_error(logger, error_msg, error_msg)
        sys.exit(1)


def common_options(verify_dependencies=True, verify_config_path=True):
    """
    Common options decorator for Click command functions. Adds verbosity option and optionally runs CLI dependencies
    verification before command run.
    :param verify_dependencies: if set to True, CLI dependencies will be verified before command run
    :param verify_config_path: if set to True, CLI config path will be verified before command run
    :return: decorated command
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            logger.debug(f'Running command {func.__name__} with following arguments: {kwargs}')
            if verify_config_path:
                verify_cli_config_path()
            if verify_dependencies:
                verify_cli_dependencies()

            return func(*args, **kwargs)
        wrapper = verbosity_option(wrapper)
        return wrapper
    return decorator
