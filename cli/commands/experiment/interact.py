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

from cli_state import common_options, pass_state, State
from util.aliascmd import AliasCmd
from util.k8s.k8s_info import get_kubectl_current_context_namespace
from util.launcher import launch_app
from util.app_names import DLS4EAppNames
from commands.experiment.common import submit_experiment
from util.exceptions import SubmitExperimentError
from util.logger import initialize_logger
from platform_resources.experiments import list_experiments
from commands.experiment.common import validate_experiment_name
from util.exceptions import K8sProxyCloseError


HELP = "Launches a local browser with Jupyter Notebook. If the script name argument " \
       "is given, then script is put into the opened notebook."
HELP_N = "The name of this Jupyter Notebook session."
HELP_F = "File with a notebook that should be opened in Jupyter notebook."

JUPYTER_NOTEBOOK_TEMPLATE_NAME = "jupyter"

log = initialize_logger(__name__)


@click.command(short_help=HELP, cls=AliasCmd, alias='i')
@click.option('-n', '--name', default=None, help=HELP_N, callback=validate_experiment_name)
@click.option('-f', '--filename', default=None, help=HELP_F)
@common_options()
@pass_state
def interact(state: State, name: str, filename: str):
    """
    Starts an interactive session with Jupyter Notebook.
    """
    current_namespace = get_kubectl_current_context_namespace()
    create_new_notebook = True

    if name:
        try:
            jupyters_list = list_experiments(namespace=current_namespace, name_filter=f'^{name}$')
        except Exception:
            err_message = "Problems during loading a list of experiments."
            log.exception(err_message)
            click.echo(err_message)
            sys.exit(1)

        # if experiment exists and is not based on jupyter image - we need to ask a user to choose another name
        if jupyters_list and jupyters_list[0].template_name != JUPYTER_NOTEBOOK_TEMPLATE_NAME:
            click.echo(f"The chosen name ({name}) is already used by an experiment other than Jupyter Notebook. "
                       f"Please choose another one")
            sys.exit(1)

        if not jupyters_list and not click.confirm("Experiment with a given name doesn't exist. "
                                                   "Should the app continue and create a new one? "):
            sys.exit(0)

        if jupyters_list:
            create_new_notebook = False

    number_of_retries = 0
    if create_new_notebook:
        number_of_retries = 5
        try:
            runs = submit_experiment(state=state, script_location=filename, script_folder_location=None,
                                     template=JUPYTER_NOTEBOOK_TEMPLATE_NAME,
                                     name=name, parameter_range=[], parameter_set=[], script_parameters=[])
            if runs:
                name = runs[0].name
            else:
                # run wasn't created - error
                raise RuntimeError("Run wasn't created")

        except K8sProxyCloseError as exe:
            click.echo(exe.message)
        except SubmitExperimentError as exe:
            err_message = f"Error during starting jupyter notebook session: {exe.message}"
            log.exception(err_message)
            click.echo(err_message)
            sys.exit(1)
        except Exception:
            err_message = "Other error during starting jupyter notebook session."
            log.exception(err_message)
            click.echo(err_message)
            sys.exit(1)
    else:
        # if jupyter service exists - the system only connects to it
        click.echo("Jupyter notebook's session exists. dlsctl connects to this session ...")

    url_end = ""
    if filename:
        url_end = f"/notebooks/{filename}"
    launch_app(k8s_app_name=DLS4EAppNames.JUPYTER, app_name=name, no_launch=False, number_of_retries=number_of_retries,
               url_end=url_end)
