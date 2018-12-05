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


import platform
from typing import NamedTuple, Union, Any, Callable
from distutils.version import LooseVersion

import distro

from util.logger import initialize_logger
from util.system import execute_system_command


logger = initialize_logger("util.os_checker")


class UnsupportedOSError(Exception):
    """ This error is raised when current OS is not compatible with any of the supported OS. """
    pass


class OSCheckError(Exception):
    """
    This error is raised when during gathering info about current OS occurs an error that forbids any further
    compatibility check.
    """
    pass


class OSRequirement(
    NamedTuple("OSRequirement", [("value", Union[str, Any]), ("getter", Callable)])
):

    def is_passed(self):
        return self.value == self.getter()


class OSSpecification(
    NamedTuple(
        "OSSpecification",
        [("prerequisite_system", str), ("system", OSRequirement), ("architecture", OSRequirement),
         ("major_version", OSRequirement), ("minor_version", OSRequirement), ("release_type", OSRequirement)])
):

    def __str__(self):
        return "System: {}, Architecture: {}, Major version: {}, Minor version: {}, Release type: {}".format(
            self.system.value, self.architecture.value, self.major_version.value, self.minor_version.value,
            self.release_type.value)

    def is_compatible_with_current_os(self):
        if self.prerequisite_system != platform.system():
            return False
        return all(
            [requirement.is_passed() for requirement in
             [self.system, self.architecture, self.major_version, self.minor_version, self.release_type]])


# Sources:
# https://docs.microsoft.com/en-us/windows/desktop/api/sysinfoapi/nf-sysinfoapi-getproductinfo
# https://docs.microsoft.com/en-us/windows/desktop/CIMWin32Prov/win32-operatingsystem
WINDOWS_EDITIONS = {
    4: "Enterprise",
    48: "Pro"
}


def get_windows_edition_name():
    if LooseVersion(platform.release()) < LooseVersion("10"):
        return "Windows"
    windows_edition_str, exit_code, _ = execute_system_command(
        ["powershell.exe", "(Get-WmiObject Win32_OperatingSystem).OperatingSystemSKU"])
    if exit_code != 0:
        raise RuntimeError("Failed to retrieve windows edition number.")
    windows_edition_number = int(windows_edition_str)
    return ("Windows "
            + (WINDOWS_EDITIONS[windows_edition_number] if windows_edition_number in WINDOWS_EDITIONS else "Unknown"))


SUPPORTED_OS = [
    OSSpecification(
        prerequisite_system="Linux",
        system=OSRequirement("Ubuntu", distro.name),
        architecture=OSRequirement("64bit", lambda: platform.architecture()[0]),
        major_version=OSRequirement("16", lambda: distro.info()["version_parts"]["major"]),
        minor_version=OSRequirement(None, lambda: None),
        release_type=OSRequirement("LTS", lambda: distro.os_release_attr("version").partition("LTS")[1])
    ),
    OSSpecification(
        prerequisite_system="Linux",
        system=OSRequirement("Red Hat Enterprise Linux Server", distro.name),
        architecture=OSRequirement("64bit", lambda: platform.architecture()[0]),
        major_version=OSRequirement("7", lambda: distro.info()["version_parts"]["major"]),
        minor_version=OSRequirement(None, lambda: None),
        release_type=OSRequirement("", lambda: distro.os_release_attr("version").partition("LTS")[1])
    ),
    OSSpecification(
        prerequisite_system="Windows",
        system=OSRequirement("Windows Pro", get_windows_edition_name),
        architecture=OSRequirement("64bit", lambda: platform.architecture()[0]),
        major_version=OSRequirement("10", platform.release),
        minor_version=OSRequirement(None, lambda: None),
        release_type=OSRequirement(None, lambda: None)
    ),
    OSSpecification(
        prerequisite_system="Windows",
        system=OSRequirement("Windows Enterprise", get_windows_edition_name),
        architecture=OSRequirement("64bit", lambda: platform.architecture()[0]),
        major_version=OSRequirement("10", platform.release),
        minor_version=OSRequirement(None, lambda: None),
        release_type=OSRequirement(None, lambda: None)
    ),
    OSSpecification(
        prerequisite_system="Darwin",
        system=OSRequirement("Darwin", distro.name),
        architecture=OSRequirement("64bit", lambda: platform.architecture()[0]),
        major_version=OSRequirement("10", lambda: platform.mac_ver()[0].split(".")[0]),
        minor_version=OSRequirement("13", lambda: platform.mac_ver()[0].split(".")[1]),
        release_type=OSRequirement(None, lambda: None)
    )
]


def check_os():
    """ Check if user's OS is supported by dlsctl. """
    logger.info("List of supported OS:")
    for os_spec in SUPPORTED_OS:
        logger.info(os_spec)

    try:
        for os_spec in SUPPORTED_OS:
            if os_spec.is_compatible_with_current_os():
                logger.info("Detected supported OS compatible with specification:")
                logger.info(os_spec)
                break
        else:
            raise UnsupportedOSError("This OS is unsupported.")
    except UnsupportedOSError:
        raise
    except Exception as exe:
        raise OSCheckError("An error occurred during OS info gathering.") from exe
