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
import time
from pathlib import Path
from typing import List, Tuple

import click
from tabulate import tabulate

from util.cli_state import common_options, pass_state, State
from util.aliascmd import AliasCmd
from util.k8s.k8s_info import get_kubectl_current_context_namespace, check_pods_status, PodStatus
from util.launcher import launch_app
from util.app_names import NAUTAAppNames
from commands.experiment.common import submit_experiment, RUN_MESSAGE, RUN_NAME, RUN_PARAMETERS, RUN_STATUS, \
    JUPYTER_NOTEBOOK_TEMPLATES_NAMES, RunKinds, validate_env_paramater
from util.exceptions import SubmitExperimentError, LaunchError, ProxyClosingError
from util.logger import initialize_logger
from commands.experiment.common import check_experiment_name, validate_pack_params_names
from util.exceptions import K8sProxyCloseError
from util.system import handle_error
from cli_text_consts import ExperimentInteractCmdTexts as Texts
from platform_resources.experiment import ExperimentStatus, Experiment
from platform_resources.experiment_utils import generate_name, list_k8s_experiments_by_label

JUPYTER_CHECK_POD_READY_TRIES = 60

ACCEPTED_NUMBER_OF_NOTEBOOKS = 2

logger = initialize_logger(__name__)


@click.command(short_help=Texts.SHORT_HELP, cls=AliasCmd, alias='i', options_metavar='[options]')
@click.option('-n', '--name', default=None, help=Texts.HELP_N)
@click.option('-f', '--filename', default=None, help=Texts.HELP_F)
@click.option("-p", "--pack-param", type=(str, str), multiple=True, help=Texts.HELP_P,
              callback=validate_pack_params_names)
@click.option('--no-launch', is_flag=True, help=Texts.HELP_NO_LAUNCH)
@click.option('-pn', '--port-number', type=click.IntRange(1024, 65535), help=Texts.HELP_PN)
@click.option("-e", "--env", multiple=True, help=Texts.HELP_E, callback=validate_env_paramater)
@click.option("-t", "--template", help=Texts.HELP_T, default=JUPYTER_NOTEBOOK_TEMPLATES_NAMES[0],
              type=click.Choice(JUPYTER_NOTEBOOK_TEMPLATES_NAMES))
@common_options(admin_command=False)
@pass_state
def interact(state: State, name: str, filename: str, pack_param: List[Tuple[str, str]], no_launch: bool,
             port_number: int, env: List[str], template: str):
    """
    Starts an interactive session with Jupyter Notebook.
    """
    current_namespace = get_kubectl_current_context_namespace()
    jupyters_number = calculate_number_of_running_jupyters(current_namespace)
    if jupyters_number > ACCEPTED_NUMBER_OF_NOTEBOOKS:
        if not click.confirm(Texts.TOO_MANY_JUPYTERS.format(jupyter_number=str(jupyters_number))):
            click.echo(Texts.INTERACT_ABORT_MSG)
            sys.exit(0)

    create_new_notebook = True

    jupyter_experiment = None

    if name:
        try:
            jupyter_experiment = Experiment.get(name=name, namespace=current_namespace)

            if jupyter_experiment and filename:
                handle_error(user_msg=Texts.FILENAME_BUT_SESSION_EXISTS)
                sys.exit(1)

            if jupyter_experiment:
                metadata = jupyter_experiment.metadata
                if metadata and metadata.get("labels") and metadata.get("labels").get("script_name"):
                    filename = metadata.get("labels").get("script_name")
        except Exception:
            handle_error(logger, Texts.EXPERIMENT_GET_ERROR_MSG, Texts.EXPERIMENT_GET_ERROR_MSG)
            sys.exit(1)

        # if experiment exists and is not based on jupyter image - we need to ask a user to choose another name
        if jupyter_experiment and jupyter_experiment.template_name not in JUPYTER_NOTEBOOK_TEMPLATES_NAMES:
            handle_error(user_msg=Texts.NAME_ALREADY_USED.format(name=name))
            sys.exit(1)

        # if experiment exists but its state is different than RUNNING - display info about a need of purging of
        # this experiment
        if jupyter_experiment and jupyter_experiment.state not in \
                [ExperimentStatus.SUBMITTED, ExperimentStatus.CREATING]:
            handle_error(user_msg=Texts.EXP_WITH_THE_SAME_NAME_MUST_BE_PURGED.format(name=name))
            sys.exit(1)

        if not jupyter_experiment and not click.confirm(Texts.CONFIRM_EXPERIMENT_CREATION):
            sys.exit(0)

        if jupyter_experiment:
            create_new_notebook = False
        else:
            try:
                check_experiment_name(value=name)
            except click.BadParameter as exe:
                handle_error(user_msg=str(exe))
                sys.exit(1)

    number_of_retries = 0
    if create_new_notebook:
        number_of_retries = 5
        try:
            exp_name = name
            if not name and not filename:
                exp_name = generate_name("jup")

            click.echo(Texts.SUBMITTING_EXPERIMENT_USER_MSG)
            runs, runs_errors, filename = submit_experiment(run_kind=RunKinds.JUPYTER, script_location=filename,
                                                            script_folder_location=None, template=template,
                                                            name=exp_name, parameter_range=[], parameter_set=(),
                                                            script_parameters=(), pack_params=pack_param,
                                                            env_variables=env)
            click.echo(tabulate({RUN_NAME: [run.cli_representation.name for run in runs],
                                 RUN_PARAMETERS: [run.cli_representation.parameters for run in runs],
                                 RUN_STATUS: [run.cli_representation.status for run in runs],
                                 RUN_MESSAGE: [runs_errors.get(run.name, "") for run in runs]},
                                headers=[RUN_NAME, RUN_PARAMETERS, RUN_STATUS, RUN_MESSAGE], tablefmt="orgtbl"))
            if runs:
                name = runs[0].name
            else:
                # run wasn't created - error
                raise RuntimeError("Run wasn't created")

        except K8sProxyCloseError as exe:
            handle_error(user_msg=exe.message)
            sys.exit(1)
        except SubmitExperimentError as exe:
            handle_error(logger, Texts.SUBMIT_ERROR_MSG.format(exception_message=exe.message),
                         Texts.SUBMIT_ERROR_MSG.format(exception_message=exe.message))
            sys.exit(1)
        except Exception:
            handle_error(logger, Texts.SUBMIT_OTHER_ERROR_MSG, Texts.SUBMIT_OTHER_ERROR_MSG)
            sys.exit(1)
    else:
        # if jupyter service exists - the system only connects to it
        click.echo(Texts.SESSION_EXISTS_MSG)

    url_end = ""
    if filename:
        # only Jupyter notebooks are opened directly, other files are opened in edit mode
        url_end = f"/notebooks/output/experiment/"
        if jupyter_experiment and filename.endswith(".py"):
            filename = filename[:filename.index(".py", -3)] + ".ipynb"
        if not filename.endswith(".ipynb"):
            url_end = "/edit/"
        url_end = url_end + Path(filename).name

    # wait until all jupyter pods are ready
    for i in range(JUPYTER_CHECK_POD_READY_TRIES):
        try:
            if check_pods_status(run_name=name, namespace=current_namespace, status=PodStatus.RUNNING):
                break
        except Exception:
            handle_error(logger, Texts.NOTEBOOK_STATE_CHECK_ERROR_MSG)
            sys.exit(1)
        time.sleep(1)
    else:
        handle_error(user_msg=Texts.NOTEBOOK_NOT_READY_ERROR_MSG)
        sys.exit(1)

    try:
        launch_app(k8s_app_name=NAUTAAppNames.JUPYTER, app_name=name, no_launch=no_launch,
                   number_of_retries=number_of_retries, url_end=url_end, port=port_number)
    except LaunchError as exe:
        handle_error(logger, exe.message, exe.message)
        sys.exit(1)
    except ProxyClosingError:
        handle_error(user_msg=Texts.PROXY_CLOSING_ERROR_MSG)
        sys.exit(1)
    except Exception:
        handle_error(logger, Texts.SESSION_LAUNCH_OTHER_ERROR_MSG, Texts.SESSION_LAUNCH_OTHER_ERROR_MSG)
        sys.exit(1)


def calculate_number_of_running_jupyters(namespace: str=None):
    present_jupyters = list_k8s_experiments_by_label(namespace=namespace, label_selector="runKind=jupyter")

    count = 0
    if present_jupyters:
        for jupyter in present_jupyters:
            if jupyter.spec.state in [ExperimentStatus.SUBMITTED, ExperimentStatus.CREATING]:
                count = count + 1
    return count
