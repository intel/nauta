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

from util.os_checker import UnsupportedOSError, OSCheckError, OSRequirement, OSSpecification, \
    get_windows_edition_name, check_os


def test_get_windows_edition_name_for_windows_10(mocker):
    release_mock = mocker.patch("util.os_checker.platform.release")
    release_mock.return_value = "10"
    execute_system_command_mock = mocker.patch("util.os_checker.execute_system_command")
    execute_system_command_mock.return_value = "48", 0, None

    windows_edition_name = get_windows_edition_name()

    assert windows_edition_name == "Windows Pro"
    assert execute_system_command_mock.call_count == 1


def test_get_windows_edition_name_for_windows_10_with_failed_command(mocker):
    release_mock = mocker.patch("util.os_checker.platform.release")
    release_mock.return_value = "10"
    execute_system_command_mock = mocker.patch("util.os_checker.execute_system_command")
    execute_system_command_mock.return_value = "48", 1, None

    with pytest.raises(RuntimeError):
        get_windows_edition_name()


def test_get_windows_edition_name_for_windows_10_with_unknown_edition(mocker):
    release_mock = mocker.patch("util.os_checker.platform.release")
    release_mock.return_value = "10"
    execute_system_command_mock = mocker.patch("util.os_checker.execute_system_command")
    execute_system_command_mock.return_value = "10000", 0, None

    windows_edition_name = get_windows_edition_name()

    assert windows_edition_name == "Windows Unknown"
    assert execute_system_command_mock.call_count == 1


def test_get_windows_edition_name_for_windows_older_than_10(mocker):
    release_mock = mocker.patch("util.os_checker.platform.release")
    release_mock.return_value = "7"
    execute_system_command_mock = mocker.patch("util.os_checker.execute_system_command")

    windows_edition_name = get_windows_edition_name()

    assert windows_edition_name == "Windows"
    assert execute_system_command_mock.call_count == 0


def test_os_requirement_passing(mocker):
    requirement = OSRequirement(value=10, getter=lambda: 10)

    assert requirement.is_passed()


def test_os_requirement_not_passing(mocker):
    requirement = OSRequirement(value="aaa", getter=lambda: 10)

    assert not requirement.is_passed()


def test_os_specification_when_compatible(mocker):
    platform_system_mock = mocker.patch("util.os_checker.platform.system")
    platform_system_mock.return_value = "Linux"
    specification = OSSpecification(
        prerequisite_system="Linux",
        system=OSRequirement(value=10, getter=lambda: 10),
        architecture=OSRequirement(value="aaa", getter=lambda: "aaa"),
        major_version=OSRequirement(value=None, getter=lambda: None),
        minor_version=OSRequirement(value=3.5, getter=lambda: 3.5),
        release_type=OSRequirement(value=[], getter=lambda: [])
    )

    assert specification.is_compatible_with_current_os()


def test_os_specification_when_not_compatible_due_to_requirement(mocker):
    platform_system_mock = mocker.patch("util.os_checker.platform.system")
    platform_system_mock.return_value = "Linux"
    specification = OSSpecification(
        prerequisite_system="Linux",
        system=OSRequirement(value=10, getter=lambda: 10),
        architecture=OSRequirement(value="aaa", getter=lambda: "aaa"),
        major_version=OSRequirement(value=None, getter=lambda: None),
        minor_version=OSRequirement(value=3.0, getter=lambda: 3.5),
        release_type=OSRequirement(value=[], getter=lambda: [])
    )

    assert not specification.is_compatible_with_current_os()


def test_os_specification_when_not_compatible_due_to_prerequisite(mocker):
    platform_system_mock = mocker.patch("util.os_checker.platform.system")
    platform_system_mock.return_value = "Windows"
    specification = OSSpecification(
        prerequisite_system="Linux",
        system=OSRequirement(value=10, getter=lambda: 10),
        architecture=OSRequirement(value="aaa", getter=lambda: "aaa"),
        major_version=OSRequirement(value=None, getter=lambda: None),
        minor_version=OSRequirement(value=3.0, getter=lambda: 3.5),
        release_type=OSRequirement(value=[], getter=lambda: [])
    )

    assert not specification.is_compatible_with_current_os()


def test_check_os_with_supported_os(mocker):
    platform_system_mock = mocker.patch("util.os_checker.platform.system")
    platform_system_mock.return_value = "Linux"
    mocker.patch(
        "util.os_checker.SUPPORTED_OS",
        [
            OSSpecification(
                prerequisite_system="Linux",
                system=OSRequirement("Ubuntu", lambda: "Ubuntu"),
                architecture=OSRequirement("64bit", lambda: "64bit"),
                major_version=OSRequirement("16", lambda: "16"),
                minor_version=OSRequirement(None, lambda: None),
                release_type=OSRequirement("LTS", lambda: "LTS")
            )
        ]
    )

    try:
        check_os()
    except Exception:
        pytest.fail()


def test_check_os_with_unsupported_os(mocker):
    platform_system_mock = mocker.patch("util.os_checker.platform.system")
    platform_system_mock.return_value = "Linux"
    mocker.patch(
        "util.os_checker.SUPPORTED_OS",
        [
            OSSpecification(
                prerequisite_system="Linux",
                system=OSRequirement("Ubuntu", lambda: "Centos"),
                architecture=OSRequirement("64bit", lambda: "64bit"),
                major_version=OSRequirement("16", lambda: "16"),
                minor_version=OSRequirement(None, lambda: None),
                release_type=OSRequirement("LTS", lambda: "LTS")
            )
        ]
    )

    with pytest.raises(UnsupportedOSError):
        check_os()


def test_check_os_with_os_check_error(mocker):
    platform_system_mock = mocker.patch("util.os_checker.platform.system")
    platform_system_mock.return_value = "Linux"
    mocker.patch(
        "util.os_checker.SUPPORTED_OS",
        [
            OSSpecification(
                prerequisite_system="Linux",
                system=OSRequirement("Ubuntu", lambda: "Ubuntu"),
                architecture=OSRequirement("64bit", lambda: "64bit"),
                major_version=OSRequirement("16", lambda: "16"),
                minor_version=OSRequirement(None, lambda: None),
                # 1 / 0 raises Exception
                release_type=OSRequirement("LTS", lambda: 1 / 0)
            )
        ]
    )

    with pytest.raises(OSCheckError):
        check_os()
