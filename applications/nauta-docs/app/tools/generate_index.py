#!/usr/bin/python
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

import getopt
import sys
import os
import re
from collections import deque


class ConversionParameters(object):
    docs_directory = "."


class Chapter(object):
    def __init__(self, title, file):
        self.title = title
        self.file = file
        self.subchapters = list()


def add_chapters_to_menu(local_chapters, file, menu):
    if len(local_chapters) == 0:
        return
    local_chapters = deque(local_chapters)
    while len(local_chapters):
        new_chapter = Chapter(remove_hash(local_chapters.popleft()), file)
        subchapters = list()
        while len(local_chapters):
            if local_chapters[0].startswith("##"):
                subchapters.append(remove_hash(local_chapters.popleft()))
            else:
                break
        new_chapter.subchapters = subchapters
        menu.append(new_chapter)


def remove_hash(text):
    while text.startswith('#'):
        text = text[1:]
    return text


def get_chapters(file, menu):
    local_chapters = list()
    with open(file, 'r', encoding="utf-8") as f:
        for line in f:
            if re.match(r'^#{1,2}[^#]', line):
                local_chapters.append(line)
        add_chapters_to_menu(local_chapters, file, menu)


def convert_directory(param, menu):
    for path, dirs, files in os.walk(param.docs_directory, topdown=True):
        for file in files:
            if file.endswith(".md"):
                get_chapters(os.path.join(path, file), menu)


def handle_parameters(argv):
    help_line = 'generate_index.py -d <docs-directory>'

    if len(argv) == 0:
        print(help_line)
        sys.exit(1)
    try:
        opts, args = getopt.getopt(argv, "h:d:", ["docs-directory="])
    except getopt.GetoptError:
        print(help_line)
        sys.exit(1)
    params = ConversionParameters()
    for opt, arg in opts:
        if opt == '-h':
            print(help_line)
            sys.exit()
        elif opt in ("-d", "--docs-directory"):
            params.docs_directory = arg
    return params


def fix_link(link, directory):
    link = link.replace(".md", ".html")
    return "/documentation" + link.replace(directory, "")


def generate_html(menu, directory):
    print("<ul>")
    for option in menu:
        print(f'<li><a href="{fix_link(option.file, directory)}">{option.title}</a><ul>')
        for suboption in option.subchapters:
            print(f'<li><a href="{fix_link(option.file, directory)}">{suboption}</a></li>')
        print("</ul></li>")
    print("</ul>")


def sort_menu(menu):
    menu.sort(key=lambda x: x.title)


if __name__ == "__main__":
    params = handle_parameters(sys.argv[1:])
    menu = list()
    convert_directory(params, menu)
    sort_menu(menu)
    generate_html(menu, params.docs_directory)
