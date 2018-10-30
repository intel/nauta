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

from functools import wraps
import sys

import click
import yaspin

from util.logger import set_verbosity_level, initialize_logger
from util.config import Config, ConfigInitError
from util.dependencies_checker import check_all_binary_dependencies, check_os
from util.k8s.k8s_info import get_kubectl_current_context_namespace, is_current_user_administrator
from util.exceptions import InvalidDependencyError, InvalidOsError
from util.system import handle_error, get_current_os, OS
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
            raise ConfigInitError(Texts.DLSCTL_CONFIG_NOT_SET_ERROR_MSG)
    except ConfigInitError as e:
        error_msg = Texts.DLSCTL_CONFIG_INIT_ERROR_MSG.format(exception_msg=str(e))
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
