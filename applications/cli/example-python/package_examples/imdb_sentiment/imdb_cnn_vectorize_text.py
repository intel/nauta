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

import sys

from keras.datasets import imdb
from keras.preprocessing.text import Tokenizer
from keras.preprocessing import sequence


def vectorize_text(text: str, maxlen = 400, max_features=5000):
    word_index = imdb.get_word_index()
    tokenizer = Tokenizer()
    tokenizer.word_index = word_index
    vectorized_texts = tokenizer.texts_to_sequences([text])
    vectorized_texts = [[v for v in vectorized_texts[0] if v < max_features]]  # Remove words with index > max_features
    vectorized_texts = sequence.pad_sequences(vectorized_texts, maxlen=maxlen)
    return vectorized_texts[0].tolist()


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print(f'Usage: {sys.argv[0]} "text to vectorize"')
        exit(1)
    vectorized_text = vectorize_text(' '.join(sys.argv[1:]))
    print(f'{{"instances": [{vectorized_text}]}}')
