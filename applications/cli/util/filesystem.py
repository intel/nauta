#
# Copyright (c) 2019 Intel Corporation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
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


def get_total_directory_size_in_bytes(directory: str) -> int:
    size = 0
    for path, dirs, files in os.walk(directory):
        for file in files:
            full_filename = os.path.join(path, file)
            size += os.path.getsize(full_filename)
    return size
