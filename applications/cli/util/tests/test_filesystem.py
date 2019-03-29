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

from util.filesystem import copytree_content, get_total_directory_size_in_bytes


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


def test_get_total_directory_size_in_bytes(tmpdir):
    test_dir = tmpdir.mkdir('test-dir')
    test_subdir = test_dir.mkdir('test-subdir')

    files = [{'path': test_dir.join('file-1.bin'), 'size': 1500},
             {'path': test_subdir.join('file-1.bin'), 'size': 10900}]

    for file in files:
        with open(file['path'], "wb") as f:
            f.write(os.urandom(file['size']))

    assert get_total_directory_size_in_bytes(test_dir) == sum(file['size'] for file in files)
