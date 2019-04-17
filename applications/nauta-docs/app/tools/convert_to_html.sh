#!/usr/bin/env bash
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

set -x
TOC_DEPTH=3

cd user-guide
find . -name "*.md*" | while read file; do
    pretty_filename=`(echo ${file} | cut -c 3-)`

    pandoc -f markdown \
    --template=/app/tools/template.html \
    --toc --toc-depth=${TOC_DEPTH} --standalone \
    --lua-filter=/app/tools/links.lua \
    --metadata version="$1" \
    --metadata filename="${pretty_filename}" \
    --metadata title="Nauta user-guide: ${pretty_filename%.*}.html" \
    "$file" -o "${file%.*}.html";

    sed -e 's/<figcaption>Image<\/figcaption>//g' "${file%.*}.html" -i
done
