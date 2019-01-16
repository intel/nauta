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

const DECODE_TOKEN_ENDPOINT = '/api/auth/decode';

export function decodeAuthK8SToken (token) {
  const body = {
    token: token
  };
  return axios.post(DECODE_TOKEN_ENDPOINT, body);
}

export function getK8SDashboardCsrfToken () {
  const CSRF_TOKEN_ENDPOINT = '/dashboard/api/v1/csrftoken/login';
  return axios.get(CSRF_TOKEN_ENDPOINT);
}

export function getK8SDashboardCookieContent (csrfToken, authToken) {
  const LOGIN_ENDPOINT = '/dashboard/api/v1/login';
  const options = {
    url: LOGIN_ENDPOINT,
    headers: {'X-CSRF-TOKEN': csrfToken},
    data: {
      kubeConfig: '',
      password: '',
      token: authToken,
      username: ''
    },
    method: 'POST'
  };
  return axios(options);
}
