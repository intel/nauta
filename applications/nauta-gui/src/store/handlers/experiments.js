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

const DECODE_TOKEN_ENDPOINT = '/api/experiments/list';

export function getExperiments (limitPerPage, pageNo, orderBy, order, searchBy, names, states, namespaces, types) {
  const token = cookies.get('TOKEN');
  let queryParams = {
    limit: limitPerPage || 5,
    page: pageNo || 1,
    orderBy: orderBy || '',
    order: order || '',
    searchBy: searchBy || '',
    names: Array.isArray(names) && names.length ? names : '*',
    states: Array.isArray(states) && states.length ? states : '*',
    namespaces: Array.isArray(namespaces) && namespaces.length ? namespaces : '*',
    types: Array.isArray(types) && types.length ? types : '*'
  };
  const options = {
    url: DECODE_TOKEN_ENDPOINT,
    headers: {
      'Authorization': token,
      'timezone-offset': new Date().getTimezoneOffset()
    },
    params: queryParams,
    method: 'GET'
  };
  return axios(options);
}

const EXPERIMENTS_ENDPOINT = '/api/experiments';

export function getExperimentsResources (experimentName) {
  const token = cookies.get('TOKEN');
  const options = {
    url: `${EXPERIMENTS_ENDPOINT}/${experimentName}/resources`,
    headers: {'Authorization': token},
    method: 'GET'
  };
  return axios(options);
}
