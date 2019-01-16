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

import click
import yaspin
import yaspin.core

from util.system import get_current_os, OS

SPINNER_COLOR = "green"
IS_TERMINAL_INTERACTIVE = sys.stdout.isatty()

NctlSpinner = yaspin.Spinner(frames='\\|/-', interval=80) if get_current_os() == OS.WINDOWS \
    else yaspin.Spinner('⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏', interval=80)


class DummySpinner(yaspin.core.Yaspin):
    def __init__(self, text: str, *args, **kwargs):
        self.text = text
        super().__init__(text=text, *args, **kwargs)

    def __enter__(self):
        click.echo(self.text)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def __call__(self, *args, **kwargs):
        click.echo(self.text)

    def hide(self):
        pass

    def show(self):
        pass


def spinner(text: str, color: str = SPINNER_COLOR, spinner: yaspin.Spinner = NctlSpinner,
            *args, **kwargs) -> yaspin.core.Yaspin:
    if IS_TERMINAL_INTERACTIVE:
        return yaspin.yaspin(spinner=spinner, text=text, color=color, *args, **kwargs)
    else:
        return DummySpinner(text=text)
