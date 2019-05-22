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


class KubernetesError(Exception):
    """Error raised in case of problems during interacting with Kubernetes"""
    pass


class KubectlConnectionError(Exception):
    """Error raised in case of problems with closing local proxy"""


class InvalidRegularExpressionError(RuntimeError):
    """Error raised when user provided regular expression is invalid"""
    pass


class ExceptionWithMessage(Exception):
    """Exception with placeholder for a message"""
    def __init__(self, message: str = None):
        self.message = message if message else ''


class K8sProxyOpenError(ExceptionWithMessage):
    """Error raised in case of any problems during establishing k8s proxy error"""
    pass


class K8sProxyCloseError(ExceptionWithMessage):
    """Error raised in case of any problems during closing k8s proxy error"""
    pass


class LocalPortOccupiedError(ExceptionWithMessage):
    """Error raised in case when app is not able to use a local port"""
    pass


class SubmitExperimentError(ExceptionWithMessage):
    """Error raised in case of any problems during experiment's submitting"""
    pass


class LaunchError(ExceptionWithMessage):
    """Error raised in case of any problems with launching other apps"""
    pass


class ProxyClosingError(ExceptionWithMessage):
    """Error raised in case of problems with closing local proxy"""


class ScriptConversionError(Exception):
    """Error raised in case of problems during conversion of python scripts into Jupyter notebooks"""
    pass


class InvalidDependencyError(Exception):
    """
    Error raised when nctl fails to obtain some dependency version, or when this version does not meet the
    requirements.
    """
    pass


class InvalidOsError(Exception):
    """Error raised when nctl fails to read user's OS version, or this version does not meet the requirements."""
    pass


class InvalidOsVersionError(Exception):
    """Error raised when os version does not meet the requirements."""
    pass
