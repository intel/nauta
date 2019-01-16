/**
 * Copyright (c) 2019 Intel Corporation
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *      http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */
import axios from 'axios';
import cookies from 'js-cookie';

const LAUNCH_TENSORBOARD_ENDPOINT = '/api/tensorboard/create';

export function launchTensorBoard (runsList) {
  const token = cookies.get('TOKEN');
  const options = {
    url: LAUNCH_TENSORBOARD_ENDPOINT,
    headers: {'Authorization': token},
    data: {
      items: runsList
    },
    method: 'POST'
  };
  return axios(options);
}

const TENSORBOARD_STATE_ENDPOINT = '/api/tensorboard/status';
const TB_INSTANCE_STATE = {
  CREATING: 'CREATING',
  RUNNING: 'RUNNING'
};

export function checkIsTBInstanceReady (instanceId) {
  const token = cookies.get('TOKEN');
  const options = {
    url: `${TENSORBOARD_STATE_ENDPOINT}/${instanceId}`,
    headers: {'Authorization': token},
    method: 'GET'
  };
  return new Promise((resolve, reject) => {
    axios(options)
      .then((data) => {
        const instanceState = data.data.status;
        if (instanceState === TB_INSTANCE_STATE.RUNNING) {
          resolve(data);
        } else {
          reject(data);
        }
      })
      .catch((err) => {
        reject(err);
      })
  });
}
