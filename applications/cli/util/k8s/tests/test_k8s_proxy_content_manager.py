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


import subprocess

import pytest
import requests
from requests.exceptions import ConnectionError

from util.k8s.k8s_proxy_context_manager import K8sProxy, TunnelSetupError
from util.app_names import DLS4EAppNames
from util.exceptions import K8sProxyCloseError, K8sProxyOpenError
from util.k8s.k8s_proxy_context_manager import kubectl


def test_set_up_proxy(mocker):
    spo_mock = mocker.patch("subprocess.Popen")
    spf_mock = mocker.patch("util.k8s.k8s_proxy_context_manager.kubectl.start_port_forwarding",
                            return_value=(spo_mock, "1000", "1001"))
    mocker.patch("util.k8s.k8s_proxy_context_manager.K8sProxy._wait_for_connection_readiness")
    mocker.patch("psutil.Process")

    with K8sProxy(DLS4EAppNames.ELASTICSEARCH):
        pass

    assert spf_mock.call_count == 1
    # noinspection PyProtectedMember,PyUnresolvedReferences
    assert K8sProxy._wait_for_connection_readiness.call_count == 1


def test_set_up_proxy_open_failure(mocker):
    spf_mock = mocker.patch("util.k8s.k8s_proxy_context_manager.kubectl.start_port_forwarding",
                            side_effect=RuntimeError())
    spc_mock = mocker.patch("subprocess.Popen.kill", side_effect=RuntimeError())
    mocker.patch("util.k8s.k8s_proxy_context_manager.K8sProxy._wait_for_connection_readiness")
    with pytest.raises(K8sProxyOpenError):
        with K8sProxy(DLS4EAppNames.ELASTICSEARCH):
            pass

    assert spf_mock.call_count == 1
    assert spc_mock.call_count == 0
    # noinspection PyProtectedMember,PyUnresolvedReferences
    assert K8sProxy._wait_for_connection_readiness.call_count == 0


def test_set_up_proxy_close_failure(mocker):
    spo_mock = mocker.patch("subprocess.Popen")
    mocker.patch("subprocess.Popen.kill", side_effect=RuntimeError)
    mocker.patch("subprocess.Popen.terminate", side_effect=RuntimeError)
    mocker.patch("util.k8s.k8s_proxy_context_manager.kubectl.start_port_forwarding",
                 return_value=(spo_mock, 1000, 1001))

    mocker.patch("util.k8s.k8s_proxy_context_manager.K8sProxy._wait_for_connection_readiness")
    mocker.patch("psutil.Process", return_value=mocker.MagicMock(children=lambda **kwargs: []))
    mocker.patch("psutil.wait_procs")

    with pytest.raises(K8sProxyCloseError):
        with K8sProxy(DLS4EAppNames.ELASTICSEARCH):
            pass

    # noinspection PyUnresolvedReferences
    assert kubectl.start_port_forwarding.call_count == 1
    # noinspection PyUnresolvedReferences
    assert subprocess.Popen.terminate.call_count == 1 or subprocess.Popen.kill.call_count == 1
    # noinspection PyProtectedMember,PyUnresolvedReferences
    assert K8sProxy._wait_for_connection_readiness.call_count == 1


def test_set_up_proxy_open_readiness_failure(mocker):
    popen_mock = mocker.patch("subprocess.Popen")
    mocker.patch("subprocess.Popen.kill")
    mocker.patch("subprocess.Popen.terminate")
    mocker.patch("util.k8s.k8s_proxy_context_manager.kubectl.start_port_forwarding",
                 return_value=(popen_mock, 1000, 1001))
    mocker.patch("util.k8s.k8s_proxy_context_manager.K8sProxy._wait_for_connection_readiness",
                 side_effect=TunnelSetupError)
    mocker.patch("psutil.Process", return_value=mocker.MagicMock(children=lambda **kwargs: []))
    mocker.patch("psutil.wait_procs")

    with pytest.raises(K8sProxyOpenError):
        with K8sProxy(DLS4EAppNames.ELASTICSEARCH):
            pass

    # noinspection PyUnresolvedReferences
    assert subprocess.Popen.kill.call_count == 1 or subprocess.Popen.terminate.call_count == 1


def test_wait_for_connection_readiness(mocker):
    mocker.patch('requests.get')
    fake_address = 'localhost'
    fake_port = 1234

    # noinspection PyProtectedMember
    K8sProxy._wait_for_connection_readiness(fake_address, fake_port)

    # noinspection PyUnresolvedReferences
    requests.get.assert_called_once_with(f'http://{fake_address}:{fake_port}')


def test_wait_for_connection_readiness_many_tries(mocker):
    effect = [ConnectionError for _ in range(10)]
    # noinspection PyTypeChecker
    effect.append(None)
    fake_address = 'localhost'
    fake_port = 1234

    mocker.patch('requests.get', side_effect=effect)
    mocker.patch('time.sleep')

    # noinspection PyProtectedMember
    K8sProxy._wait_for_connection_readiness(fake_address, fake_port, 15)

    # noinspection PyUnresolvedReferences
    assert requests.get.call_count == 11


def test_wait_for_connection_readiness_many_tries_failure(mocker):
    fake_address = 'localhost'
    fake_port = 1234

    mocker.patch('requests.get', side_effect=ConnectionError)
    mocker.patch('time.sleep')

    with pytest.raises(TunnelSetupError):
        # noinspection PyProtectedMember
        K8sProxy._wait_for_connection_readiness(fake_address, fake_port, 15)

    # noinspection PyUnresolvedReferences
    assert requests.get.call_count == 15
