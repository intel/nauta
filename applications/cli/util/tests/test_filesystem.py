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

from util.filesystem import copytree_content


def test_copytree_content(mocker):
    fake_src_dir_filelist = ['dir1', 'dir2', 'file1']

    mocker.patch('os.listdir', return_value=fake_src_dir_filelist)
    shutil_copytree = mocker.patch('shutil.copytree')
    shutil_copy2 = mocker.patch('shutil.copy2')
    mocker.patch('os.path.isdir', new=lambda x: 'dir' in os.path.basename(x))

    copytree_content('/home/tomasz/fake_src_dir', '/home/tomasz/fake_dst_dir')

    assert shutil_copytree.call_count == 2
    assert shutil_copy2.call_count == 1


def test_copytree_content_ignored_objects(mocker):
    fake_src_dir_filelist = ['dir1', 'dir2', 'file1']

    mocker.patch('os.listdir', return_value=fake_src_dir_filelist)
    shutil_copytree = mocker.patch('shutil.copytree')
    shutil_copy2 = mocker.patch('shutil.copy2')
    mocker.patch('os.path.isdir', new=lambda x: 'dir' in os.path.basename(x))

    copytree_content('/home/tomasz/fake_src_dir', '/home/tomasz/fake_dst_dir', ignored_objects=['dir2'])

    assert shutil_copytree.call_count == 1
    assert shutil_copy2.call_count == 1
