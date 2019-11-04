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

import asyncio
import datetime

import kopf
import pykube

from nauta_resources.run import Run, RunStatus

tasks = {}  # dict{namespace: dict{name: asyncio.Task}}

try:
    cfg = pykube.KubeConfig.from_service_account()
except FileNotFoundError:
    cfg = pykube.KubeConfig.from_file()
api = pykube.HTTPClient(cfg)

kopf.EventsConfig.events_loglevel = kopf.config.LOGLEVEL_WARNING


@kopf.on.resume('aipg.intel.com', 'v1', 'runs')
async def handle_run_on_resume(namespace, name, logger, spec, **kwargs):
    try:
        run_state = RunStatus(spec['state'])
    except ValueError:
        raise kopf.PermanentError(f'Run {name} is invalid - cannot infer status from spec: {spec}')

    if run_state in {RunStatus.COMPLETE, RunStatus.FAILED, RunStatus.CANCELLED}:
        logger.info(f'Run {name} already in final state: {run_state.value}.')
        if namespace in tasks and name in tasks[namespace]:
            del tasks[namespace][name]
        return
    elif not tasks.get(namespace, {}).get(name):
        logger.info(f'Resuming monitoring task for run {name}.')
        task = asyncio.create_task(monitor_run(namespace, name, logger))
        tasks.setdefault(namespace, {})
        tasks[namespace][name] = task


@kopf.on.create('aipg.intel.com', 'v1', 'runs')
async def run_created(namespace, name, logger, **kwargs):
    logger.warning(f'Run {name} created.')
    task = asyncio.create_task(monitor_run(namespace, name, logger))
    tasks.setdefault(namespace, {})
    tasks[namespace][name] = task


@kopf.on.delete('aipg.intel.com', 'v1', 'runs')
async def run_deleted(namespace, name, logger, **kwargs):
    logger.warning(f'Run {name} deleted.')
    if namespace in tasks and name in tasks[namespace]:
        task = tasks[namespace][name]
        task.cancel()  # it will also remove from `tasks`


async def monitor_run(namespace, name, logger):
    interval = 1
    retry_counter = 0
    retry_limit = 5
    while True:
        try:
            await asyncio.sleep(interval)
            logger.debug(f'Monitoring Run {name}')
            run: Run = await Run.get(name=name, namespace=namespace)

            if run.state in {RunStatus.COMPLETE, RunStatus.FAILED, RunStatus.CANCELLED}:
                logger.info(f'Run {name} reached final state: {run.state.value}.')
                if namespace in tasks and name in tasks[namespace]:
                    del tasks[namespace][name]
                return

            state_to_set = await run.calculate_current_state()
            if run.state is not state_to_set:
                logger.warning(f'Run {name} state changed from {run.state.value} to {state_to_set.value}')
                utc_timestamp = datetime.datetime.utcnow().replace(microsecond=0).isoformat()
                if run.state is RunStatus.QUEUED:
                    logger.info(f'Setting Run {name} start time.')
                    run.start_timestamp = f'{utc_timestamp}Z'
                if run.state in {RunStatus.QUEUED, RunStatus.RUNNING} and \
                        state_to_set not in {RunStatus.QUEUED, RunStatus.RUNNING}:
                    logger.info(f'Setting Run {name} end time.')
                    run.end_timestamp = f'{utc_timestamp}Z'
                run.state = state_to_set
                await run.update()

        except asyncio.CancelledError:
            logger.info(f'Monitoring of Run {name} is cancelled')
            if namespace in tasks and name in tasks[namespace]:
                del tasks[namespace][name]
            return
        except Exception:
            logger.exception(f'Unexpected error encountered when monitoring Run {name}.')
            retry_counter += 1
            logger.exception(f'Monitoring attempt: #{retry_counter}, retry limit: #{retry_limit}.')
            if retry_counter >= retry_limit:
                raise
