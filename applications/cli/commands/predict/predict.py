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

from commands.predict import launch, list, cancel, stream, batch
from util.logger import initialize_logger
from util.aliascmd import AliasGroup
from cli_text_consts import PredictCmdTexts as Texts


logger = initialize_logger(__name__)


@click.group(short_help=Texts.HELP, cls=AliasGroup, alias='p', help=Texts.HELP,
             subcommand_metavar="COMMAND [options] [args]...")
def predict():
    pass


predict.add_command(cancel.cancel)
predict.add_command(launch.launch)
predict.add_command(list.list_inference_instances)
predict.add_command(stream.stream)
predict.add_command(batch.batch)
