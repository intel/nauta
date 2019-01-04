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

from __future__ import (absolute_import, division, print_function)

__metaclass__ = type


def organize_images(images):
    image_names = list(images.keys())
    image_reqs = {}
    for image in image_names:
        if 'required' not in images[image]:
            image_reqs[image] = []
        else:
            image_reqs[image] = [value for key,value in images[image]['required'].items()]
    layers = []

    while len(image_names) > 0:
        layer = []
        for image in image_names:
            if len(image_reqs[image]) == 0:
                layer.append(image)
        if len(layer) == 0:
            raise Exception("Loop error: {}".format(image_names))
        layers.append(layer)
        for image in layer:
            image_names.remove(image)
            for obs_image in image_names:
                if image in image_reqs[obs_image]:
                    image_reqs[obs_image].remove(image)
    return layers


class FilterModule(object):
    """ Carbon tests core jinja2 filters """

    def filters(self):
        return {
          'organize_images': organize_images
        }
