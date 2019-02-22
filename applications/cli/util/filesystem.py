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
import shutil
from typing import List


def copytree_content(src: str, dst: str, ignored_objects: List[str] = None, symlinks=False, ignore=None):
    """
    Similarly to shutil.copytree copies whole tree, but operates on content of 'src' directory, not directory itself -
    like '/home/dir/*' instead of '/home/dir'.
    :param src: source directory to copy
    :param dst: destination directory
    :param ignored_objects: list of ignored files and directories in 'src' directory
    :param symlinks: argument passed to shutil.copytree
    :param ignore: argument passed to shutil.copytree
    """
    for item in os.listdir(src):
        if not ignored_objects or item not in ignored_objects:
            s = os.path.join(src, item)
            d = os.path.join(dst, item)
            if os.path.isdir(s):
                shutil.copytree(s, d, symlinks, ignore)
            else:
                shutil.copy2(s, d)
