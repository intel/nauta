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

from licensing import license_acceptance_manager


def test_save_license_accepted(mocker):
    open_mock = mocker.patch('builtins.open')
    mocker.patch.object(license_acceptance_manager.Config, 'get_config_path', new=lambda: "/fake/path")

    license_acceptance_manager.save_license_accepted()

    assert open_mock.call_count == 1


@pytest.mark.parametrize(['path_isfile_return_value', 'license_accepted_expected_value'],
                         [(True, True),
                          (False, False)])
def test_is_license_already_accepted(mocker, path_isfile_return_value: bool, license_accepted_expected_value: bool):
    mocker.patch.object(license_acceptance_manager.Config, 'get_config_path', new=lambda: "/fake/path")
    mocker.patch('os.path.isfile', new=lambda *args: path_isfile_return_value)

    license_accepted = license_acceptance_manager.is_license_already_accepted()

    assert license_accepted == license_accepted_expected_value


# noinspection PyUnresolvedReferences
@pytest.mark.parametrize(['click_confirm_return_value', 'expected_license_accepted'],
                         [
                             (True, True),
                             (False, False)
                         ])
def test_check_license_acceptance(mocker, click_confirm_return_value: bool, expected_license_accepted: bool):
    mocker.patch.object(license_acceptance_manager, 'is_license_already_accepted', new=lambda: False)
    mocker.spy(license_acceptance_manager, 'is_license_already_accepted')
    mocker.patch.object(license_acceptance_manager, 'save_license_accepted')
    mocker.patch('click.confirm', new=lambda *args, **kwargs: click_confirm_return_value)

    license_accepted = license_acceptance_manager.check_license_acceptance()

    assert license_accepted == expected_license_accepted
    assert license_acceptance_manager.is_license_already_accepted.call_count == 1
    assert license_acceptance_manager.save_license_accepted.call_count == 1 if expected_license_accepted else True


# noinspection PyUnresolvedReferences
def test_check_license_acceptance_already_accepted(mocker):
    mocker.patch.object(license_acceptance_manager, 'is_license_already_accepted', new=lambda: True)
    mocker.spy(license_acceptance_manager, 'is_license_already_accepted')
    license_accepted = license_acceptance_manager.check_license_acceptance()

    assert license_accepted
    assert license_acceptance_manager.is_license_already_accepted.call_count == 1