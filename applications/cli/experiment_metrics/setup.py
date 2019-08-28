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

import setuptools

setuptools.setup(
    name='experiment_metrics',
    version='0.0.1',
    description='a pip-installable library for experiment metrics update',
    packages=['experiment_metrics'],
    keywords=['experiment', 'library', 'metrics'],
    install_requires=[
        'kubernetes==9.0.0',
    ],
)
