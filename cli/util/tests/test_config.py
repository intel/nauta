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

import os

import util.config as config


RET_HOME_FOLDER = "/HOME/FOLDER"


def test_create_home_folder_success(mocker):
    mocker.patch.dict("os.environ", {config.ENV_DLSCTL_HOME: RET_HOME_FOLDER})
    os_md_mock = mocker.patch("os.makedirs")
    os_path_exists_mock = mocker.patch("os.path.exists")

    os_path_exists_mock.side_effect = [False]

    home_folder = config.create_home_folder()

    assert home_folder == os.path.join(RET_HOME_FOLDER, config.CONFIG_FOLDER), "home folder wasn't set properly."
    assert os_path_exists_mock.call_count == 1, "presence of a path wasn't checked"
    assert os_md_mock.call_count == 1, "folder wasn't created"
