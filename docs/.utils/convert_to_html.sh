#!/usr/bin/env bash

set -x

cd user-guide
find . -name "*.md*" | while read file; do \
    pandoc -f markdown \
    --template=../.utils/template.html \
    --toc --toc-depth=3 --standalone \
    --lua-filter=../.utils/links.lua \
    --metadata version="$1" \
    --metadata title="Nauta documentation: ${file%.*}.html" \
    "$file" -o "${file%.*}.html"; done
