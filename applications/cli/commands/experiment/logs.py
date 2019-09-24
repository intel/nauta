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

import click

from cli_text_consts import ExperimentLogsCmdTexts as Texts
from commands.common.logs_utils import get_logs
from logs_aggregator.log_filters import SeverityLevel
from util.cli_state import common_options
from util.logger import initialize_logger
from util.k8s.k8s_info import PodStatus
from util.aliascmd import AliasCmd
from platform_resources.run import RunKinds

logger = initialize_logger(__name__)

LOG_RUNS_KINDS = [RunKinds.TRAINING, RunKinds.JUPYTER]


@click.command(help=Texts.HELP, short_help=Texts.SHORT_HELP, cls=AliasCmd, alias='lg', options_metavar='[options]')
@click.argument('experiment-name', required=False, metavar='[experiment_name]')
@click.option('-s', '--min-severity', type=click.Choice([level.name for level in SeverityLevel]), help=Texts.HELP_S)
@click.option('-sd', '--start-date', help=Texts.HELP_SD)
@click.option('-ed', '--end-date', help=Texts.HELP_ED)
@click.option('-i', '--pod-ids', help=Texts.HELP_I)
@click.option('-p', '--pod-status', type=click.Choice([status.name for status in PodStatus]),
              help=Texts.HELP_P)
@click.option('-m', '--match', help=Texts.HELP_M)
@click.option('-o', '--output', help=Texts.HELP_O, is_flag=True)
@click.option('-pa', '--pager', help=Texts.HELP_PAGER, is_flag=True, default=False)
@click.option('-fl', '--follow', help=Texts.HELP_F, is_flag=True, default=False)
@common_options(admin_command=False)
@click.pass_context
def logs(ctx: click.Context, experiment_name: str, min_severity: str, start_date: str,
         end_date: str, pod_ids: str, pod_status: str, match: str, output: bool, pager: bool, follow: bool):
    """
    Show logs for a given experiment.
    """
    # check whether we have runs with a given name
    min_severity = SeverityLevel[min_severity] if min_severity else None
    pod_status = PodStatus[pod_status] if pod_status else None
    get_logs(experiment_name=experiment_name, min_severity=min_severity, start_date=start_date, end_date=end_date,
             pod_ids=pod_ids, pod_status=pod_status, match=match, output=output, pager=pager, follow=follow,
             runs_kinds=LOG_RUNS_KINDS, instance_type="experiment")
