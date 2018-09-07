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
import time
from pathlib import Path
from typing import List, Tuple

import click
from tabulate import tabulate

from cli_state import common_options, pass_state, State
from util.aliascmd import AliasCmd
from util.k8s.k8s_info import get_kubectl_current_context_namespace, check_pods_status, PodStatus
from util.launcher import launch_app
from util.app_names import DLS4EAppNames
from commands.experiment.common import submit_experiment, RUN_MESSAGE, RUN_NAME, RUN_PARAMETERS, RUN_STATUS, \
    JUPYTER_NOTEBOOK_TEMPLATE_NAME, RunKinds
from util.exceptions import SubmitExperimentError, LaunchError, ProxyClosingError
from util.logger import initialize_logger
from platform_resources.experiments import get_experiment, generate_name
from commands.experiment.common import check_experiment_name, validate_pack_params_names
from util.exceptions import K8sProxyCloseError
from util.system import handle_error
from cli_text_consts import EXPERIMENT_INTERACT_CMD_TEXTS as TEXTS


JUPYTER_CHECK_POD_READY_TRIES = 60

logger = initialize_logger(__name__)


@click.command(short_help=TEXTS["help"], cls=AliasCmd, alias='i')
@click.option('-n', '--name', default=None, help=TEXTS["help_n"])
@click.option('-f', '--filename', default=None, help=TEXTS["help_f"])
@click.option("-p", "--pack_param", type=(str, str), multiple=True, help=TEXTS["help_p"],
              callback=validate_pack_params_names)
@click.option('--no-launch', is_flag=True, help=TEXTS["help_no_launch"])
@click.option('-pn', '--port_number', type=click.IntRange(1024, 65535), help=TEXTS["help_pn"])
@common_options()
@pass_state
def interact(state: State, name: str, filename: str, pack_param: List[Tuple[str, str]], no_launch: bool,
             port_number: int):
    """
    Starts an interactive session with Jupyter Notebook.
    """
    current_namespace = get_kubectl_current_context_namespace()
    create_new_notebook = True

    jupyter_experiment = None

    if name:
        try:
            jupyter_experiment = get_experiment(namespace=current_namespace, name=name)
        except Exception:
            handle_error(logger, TEXTS["experiment_get_error_msg"], TEXTS["experiment_get_error_msg"])
            sys.exit(1)

        # if experiment exists and is not based on jupyter image - we need to ask a user to choose another name
        if jupyter_experiment and jupyter_experiment.template_name != JUPYTER_NOTEBOOK_TEMPLATE_NAME:
            handle_error(user_msg=TEXTS["name_already_used"].format(name=name))
            sys.exit(1)

        if not jupyter_experiment and not click.confirm(TEXTS["confirm_experiment_creation"]):
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

            click.echo(TEXTS["submitting_experiment_user_msg"])
            runs, filename = submit_experiment(run_kind=RunKinds.JUPYTER, script_location=filename,
                                               script_folder_location=None, template=JUPYTER_NOTEBOOK_TEMPLATE_NAME,
                                               name=exp_name, parameter_range=[], parameter_set=(),
                                               script_parameters=(), pack_params=pack_param)
            click.echo(tabulate({RUN_NAME: [run.cli_representation.name for run in runs],
                                 RUN_PARAMETERS: [run.cli_representation.parameters for run in runs],
                                 RUN_STATUS: [run.cli_representation.status for run in runs],
                                 RUN_MESSAGE: [run.message for run in runs]},
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
            handle_error(logger, TEXTS["submit_error_msg"].format(exception_message=exe.message),
                         TEXTS["submit_error_msg"].format(exception_message=exe.message))
            sys.exit(1)
        except Exception:
            handle_error(logger, TEXTS["submit_other_error_msg"], TEXTS["submit_other_error_msg"])
            sys.exit(1)
    else:
        # if jupyter service exists - the system only connects to it
        click.echo(TEXTS["session_exists_msg"])

    url_end = ""
    if filename:
        # only Jupyter notebooks are opened directly, other files are opened in edit mode
        if not jupyter_experiment:
            if ".ipynb" in filename:
                url_end = "/notebooks/"
            else:
                url_end = "/edit/"
            url_end = url_end + Path(filename).name
        else:
            click.echo(TEXTS["attaching_script_not_supported_msg"])

    # wait until all jupyter pods are ready
    for i in range(JUPYTER_CHECK_POD_READY_TRIES):
        try:
            if check_pods_status(run_name=name, namespace=current_namespace, status=PodStatus.RUNNING):
                break
        except Exception:
            handle_error(logger, TEXTS["notebook_state_check_error_msg"])
            sys.exit(1)
        time.sleep(1)
    else:
        handle_error(user_msg=TEXTS["notebook_not_ready_error_msg"])
        sys.exit(1)

    try:
        launch_app(k8s_app_name=DLS4EAppNames.JUPYTER, app_name=name, no_launch=no_launch,
                   number_of_retries=number_of_retries, url_end=url_end, port=port_number)
    except LaunchError as exe:
        handle_error(logger, exe.message, exe.message)
        sys.exit(1)
    except ProxyClosingError:
        handle_error(user_msg=TEXTS["proxy_closing_error_msg"])
        sys.exit(1)
    except Exception:
        handle_error(logger, TEXTS["session_launch_other_error_msg"], TEXTS["session_launch_other_error_msg"])
        sys.exit(1)
