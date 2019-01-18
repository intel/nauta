#
# INTEL CONFIDENTIAL
# Copyright (c) 2018 Intel Corporation
#
# The source code contained or described herein and all documents related to
# the source code ("Material") are owned by Intel Corporation or its suppliers
# or licensors. Title to the Material remains with Intel Corporation or its
# suppliers and licensors. The Material contains trade secrets and proprietary
# and confidential information of Intel or its suppliers and licensors. The
# Material is protected by worldwide copyright and trade secret laws and treaty
# provisions. No part of the Material may be used, copied, reproduced, modified,
# published, uploaded, posted, transmitted, distributed, or disclosed in any way
# without Intel's prior express written permission.
#
# No license under any patent, copyright, trade secret or other intellectual
# property right is granted to or conferred upon you by disclosure or delivery
# of the Materials, either expressly, by implication, inducement, estoppel or
# otherwise. Any license under such intellectual property rights must be express
# and approved by Intel in writing.
#

import sys

import click
import yaspin
import yaspin.core

from util.system import get_current_os, OS

SPINNER_COLOR = "green"
IS_TERMINAL_INTERACTIVE = sys.stdout.isatty()


def set_frames_string():
    fallback_frames = "\\|/-"
    if get_current_os() == OS.WINDOWS:
        return fallback_frames
    try:
        utf_frames = "⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏"
        utf_frames.encode(sys.stdout.encoding)
        return utf_frames
    except UnicodeEncodeError:
        return fallback_frames


NctlSpinner = yaspin.Spinner(frames=set_frames_string(), interval=80)


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
