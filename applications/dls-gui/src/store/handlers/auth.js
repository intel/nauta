/**
 * INTEL CONFIDENTIAL
 * Copyright (c) 2018 Intel Corporation
 *
 * The source code contained or described herein and all documents related to
 * the source code ("Material") are owned by Intel Corporation or its suppliers
 * or licensors. Title to the Material remains with Intel Corporation or its
 * suppliers and licensors. The Material contains trade secrets and proprietary
 * and confidential information of Intel or its suppliers and licensors. The
 * Material is protected by worldwide copyright and trade secret laws and treaty
 * provisions. No part of the Material may be used, copied, reproduced, modified,
 * published, uploaded, posted, transmitted, distributed, or disclosed in any way
 * without Intel's prior express written permission.
 *
 * No license under any patent, copyright, trade secret or other intellectual
 * property right is granted to or conferred upon you by disclosure or delivery
 * of the Materials, either expressly, by implication, inducement, estoppel or
 * otherwise. Any license under such intellectual property rights must be express
 * and approved by Intel in writing.
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
