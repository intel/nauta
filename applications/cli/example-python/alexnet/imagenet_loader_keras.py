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

import tensorflow.contrib.keras as keras


def create_generator(path_train, path_val, batch_size=128):
    datagen = keras.preprocessing.image.ImageDataGenerator(data_format='channels_last')
    train_generator = datagen.flow_from_directory(path_train,
                                                  target_size=(227, 227),
                                                  batch_size=batch_size,
                                                  class_mode='categorical')

    validation_generator = datagen.flow_from_directory(path_val,
                                                       target_size=(227, 227),
                                                       batch_size=batch_size,
                                                       class_mode='categorical')
    return train_generator, validation_generator

