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

import pytest
from util.k8s.k8s_proxy_context_manager import K8sProxy
from util.app_names import DLS4EAppNames
from util.exceptions import K8sProxyCloseError, K8sProxyOpenError


def test_set_up_proxy(mocker):
    spo_mock = mocker.patch("subprocess.Popen")
    spf_mock = mocker.patch("util.k8s.k8s_proxy_context_manager.kubectl.start_port_forwarding",
                            return_value=(spo_mock, "1000", "1001"))

    with K8sProxy(DLS4EAppNames.ELASTICSEARCH):
        pass

    assert spf_mock.call_count == 1


def test_set_up_proxy_open_failure(mocker):
    spf_mock = mocker.patch("util.k8s.k8s_proxy_context_manager.kubectl.start_port_forwarding",
                            side_effect=RuntimeError())
    spc_mock = mocker.patch("subprocess.Popen.kill", side_effect=RuntimeError())
    with pytest.raises(K8sProxyOpenError):
        with K8sProxy(DLS4EAppNames.ELASTICSEARCH):
            pass

    assert spf_mock.call_count == 1
    assert spc_mock.call_count == 0


def test_set_up_proxy_close_failure(mocker):
    spo_mock = mocker.patch("subprocess.Popen")
    spc_mock = mocker.patch("subprocess.Popen.kill", side_effect=RuntimeError())
    spf_mock = mocker.patch("util.k8s.k8s_proxy_context_manager.kubectl.start_port_forwarding",
                            return_value=(spo_mock, "1000", "1001"))

    with pytest.raises(K8sProxyCloseError):
        with K8sProxy(DLS4EAppNames.ELASTICSEARCH):
            pass

    assert spf_mock.call_count == 1
    assert spc_mock.call_count == 1
