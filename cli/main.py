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

import click
import sys

import draft.cmd as draft
from draft import dependencies_checker
from util.kubectl import start_port_forwarding
from util.logger import initialize_logger

CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])

log = initialize_logger('main')


@click.group(context_settings=CONTEXT_SETTINGS)
def cli():
    pass


@click.command()
def train():
    click.echo('Creating draft container...')
    draft.create()

    click.echo('Running draft container...')
    try:
        process = start_port_forwarding()
    except Exception as exe:
        log.exception("Error during creation of a proxy for a docker registry.")
        click.echo("Error during creation of a proxy for a docker registry.")
        sys.exit(1)
    try:
        output, exit_code = draft.up()
        click.echo(output)
    except Exception as exe:
        log.exception("Error during creating of a draft deployment.")
        click.echo("Error during creating of a draft deployment.")
        sys.exit(1)
    finally:
        try:
            process.kill()
        except Exception as exet:
            log.exception("Error during closing of a proxy for a docker registry.")
            click.echo("Docker proxy hasn't been closed properly. "
                       "Check whether it still exists, if yes - close it manually.")


@click.command()
def verify():
    dependencies_checker.check()


cli.add_command(train)
cli.add_command(verify)

if __name__ == '__main__':
    cli()
