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

import base64

import pytest
from click.testing import CliRunner

from util.exceptions import KubectlIntError
from commands.user.create import check_users_presence, generate_kubeconfig, create
from util.helm import delete_user, delete_helm_release


test_username = "test_username"
test_namespace = "test_namespace"
test_address = "test_address"
test_token = "test_token"
test_cacert = "test_cacert"
test_cacert_encoded = base64.b64encode(test_cacert.encode('utf-8')).decode('utf-8')
test_samba_password = "test_samba_password"

KUBECONFIG = f'''
current-context: user-context
apiVersion: v1
clusters:
- cluster:
    api-version: v1
    server: https://{test_address}:8443
    # certificate-authority-data: {test_cacert_encoded}
    # BUG/TASK: CAN-261
    insecure-skip-tls-verify: true
  name: dls-cluster
contexts:
- context:
    cluster: dls-cluster
    namespace: {test_namespace}
    user: {test_username}
  name: user-context
kind: Config
preferences:
  colors: true
users:
- name: {test_username}
  user:
    token: {test_token}
'''


def test_check_users_presence_success(mocker):
    mocker.patch("util.k8s.kubectl.find_namespace", return_value=False)
    mocker.patch("util.k8s.kubectl.execute_system_command", return_value=(test_username, 0))
    assert check_users_presence(test_username)

    mocker.patch("util.k8s.kubectl.find_namespace", return_value=True)
    assert check_users_presence(test_username)


def test_check_users_presence_failure(mocker):
    mocker.patch("util.k8s.kubectl.find_namespace", return_value=False)
    mocker.patch("util.k8s.kubectl.execute_system_command", return_value=(test_username, 1))
    with pytest.raises(KubectlIntError):
        check_users_presence(test_username+"_wrong")


def test_generate_kubeconfig():
    output = generate_kubeconfig(username=test_username,
                                 namespace=test_namespace,
                                 address=test_address,
                                 token=test_token,
                                 cacrt=test_cacert)

    assert output == KUBECONFIG


def test_delete_helm_release_success(mocker):
    mocker.patch("util.helm.execute_system_command", return_value=(f"release \"{test_username}\" deleted", 0))
    assert delete_helm_release(test_username)


def test_delete_helm_release_failure(mocker):
    mocker.patch("util.helm.execute_system_command", return_value=("", 1))
    with pytest.raises(RuntimeError):
        delete_helm_release(test_username)


def test_delete_user_success(mocker):
    dns_mock = mocker.patch("util.helm.delete_namespace")
    dhr_mock = mocker.patch("util.helm.delete_helm_release")

    user_deleted = delete_user(test_username)

    assert user_deleted
    assert dns_mock.call_count == 1
    assert dhr_mock.call_count == 1


def test_delete_user_failure(mocker):
    dns_mock = mocker.patch("util.helm.delete_namespace", side_effect=RuntimeError)
    dhr_mock = mocker.patch("util.helm.delete_helm_release")

    user_deleted = delete_user(test_username)

    assert not user_deleted
    assert dns_mock.call_count == 1
    assert dhr_mock.call_count == 0


def test_create_user_failure(mocker):  # noqa: F811
    cup_mock = mocker.patch("commands.user.create.check_users_presence", return_value=True)
    esc_mock = mocker.patch("commands.user.create.execute_system_command", return_value=("", 0))
    gut_mock = mocker.patch("commands.user.create.get_users_token", return_value=test_samba_password)

    runner = CliRunner()
    runner.invoke(create, [test_username])

    assert cup_mock.call_count == 1, "users presence wasn't checked"
    assert esc_mock.call_count == 0, "user was created"
    assert gut_mock.call_count == 0, "users password was taken"
