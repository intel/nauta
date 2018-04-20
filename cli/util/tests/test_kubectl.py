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

from pytest import raises

import util.kubectl as kubectl


def test_start_port_forwarding_success(mocker):
    popen_mock = mocker.patch('subprocess.Popen')
    esc_mock = mocker.patch('util.kubectl.execute_system_command', side_effect=[("local-registry-12345\n", 0),
                                                                                ("31025", 0)])
    srp_mock = mocker.patch("util.kubectl.set_registry_port", side_effect=[("", 0)])

    process = kubectl.start_port_forwarding()

    assert process, "proxy process doesn't exist."
    assert popen_mock.call_count == 1, "kubectl proxy-forwarding command wasn't called"
    assert esc_mock.call_count == 2, "pod and port data weren't gathered"
    assert srp_mock.call_count == 1, "draft.set_registry_port command wasn't called"


def test_start_port_forwarding_missing_pod(mocker):
    popen_mock = mocker.patch("subprocess.Popen")
    # missing pod name
    esc_mock = mocker.patch("util.kubectl.execute_system_command", side_effect=[("", 0),
                                                                                ("31025", 0)])

    with raises(RuntimeError, message="Missing pod name during creation of registry port proxy."):
        kubectl.start_port_forwarding()

    assert popen_mock.call_count == 0, "kubectl proxy-forwarding command was called"
    assert esc_mock.call_count == 1, "port data were gathered"

    # returned code = 1
    esc_mock.reset_mock()
    esc_mock.side_effect = [("local-registry-12345\n", 1),
                            ("31025", 0)]

    with raises(RuntimeError, message="Missing pod name during creation of registry port proxy."):
        kubectl.start_port_forwarding()

    assert popen_mock.call_count == 0, "kubectl proxy-forwarding command was called"
    assert esc_mock.call_count == 1, "port data were gathered"


def test_start_port_forwarding_missing_port(mocker):
    popen_mock = mocker.patch("subprocess.Popen")
    # missing port name
    esc_mock = mocker.patch("util.kubectl.execute_system_command", side_effect=[("local-registry-12345\n", 0),
                                                                                ("", 0)])

    with raises(RuntimeError, message="Missing pod port during creation of registry port proxy."):
        kubectl.start_port_forwarding()

    assert popen_mock.call_count == 0, "kubectl proxy-forwarding command was called"
    assert esc_mock.call_count == 2, "incorrect number of kubectl calls"

    # returned code = 1
    esc_mock.reset_mock()
    esc_mock.side_effect = [("local-registry-12345\n", 0),
                            ("31025", 1)]

    with raises(RuntimeError, message="Missing pod port during creation of registry port proxy."):
        kubectl.start_port_forwarding()

    assert popen_mock.call_count == 0, "kubectl proxy-forwarding command was called"
    assert esc_mock.call_count == 2, "incorrect number of kubectl calls"


def test_start_port_forwarding_lack_of_process(mocker):
    popen_mock = mocker.patch('subprocess.Popen', side_effect=[None])
    esc_mock = mocker.patch('util.kubectl.execute_system_command', side_effect=[("local-registry-12345\n", 0),
                                                                                ("31025", 0)])
    srp_mock = mocker.patch("util.kubectl.set_registry_port", side_effect=[("", 0)])

    with raises(RuntimeError, message="Registry port proxy hasn't been created."):
        kubectl.start_port_forwarding()

    assert popen_mock.call_count == 1, "kubectl proxy-forwarding command wasn't called"
    assert esc_mock.call_count == 2, "incorrect number of kubectl calls"
    assert srp_mock.call_count == 1, "draft.set_registry_port command wasn't called"


def test_start_port_forwarding_other_error(mocker):
    popen_mock = mocker.patch('subprocess.Popen',
                              side_effect=Exception("Other error during creation of registry port proxy."))
    esc_mock = mocker.patch('util.kubectl.execute_system_command', side_effect=[("local-registry-12345\n", 0),
                                                                                ("31025", 0)])
    srp_mock = mocker.patch("util.kubectl.set_registry_port", side_effect=[("", 0)])

    with raises(RuntimeError, message="Other error during creation of registry port proxy."):
        kubectl.start_port_forwarding()

    assert popen_mock.call_count == 1, "kubectl proxy-forwarding command wasn't called"
    assert esc_mock.call_count == 2, "incorrect number of kubectl calls"
    assert srp_mock.call_count == 1, "draft.set_registry_port command wasn't called"


def test_start_port_forwarding_draft_config_fail(mocker):
    popen_mock = mocker.patch('subprocess.Popen')
    esc_mock = mocker.patch('util.kubectl.execute_system_command', side_effect=[("local-registry-12345\n", 0),
                                                                                ("31025", 0)])
    srp_mock = mocker.patch("util.kubectl.set_registry_port", side_effect=[("Error message", 1)])

    with raises(RuntimeError, message="Setting draft config failed."):
        kubectl.start_port_forwarding()

    assert popen_mock.call_count == 0, "kubectl proxy-forwarding command was called"
    assert esc_mock.call_count == 2, "incorrect number of kubectl calls"
    assert srp_mock.call_count == 1, "draft.set_registry_port command wasn't called"
