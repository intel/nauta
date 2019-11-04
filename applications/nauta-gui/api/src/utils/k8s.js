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
const logger = require('./logger');
const HttpStatus = require('http-status-codes');
const errHandler = require('./error-handler');
const request = require('./requestWrapper');
const errMessages = require('./error-messages');
const Q = require('q');
const authApi = require('../../src/handlers/auth/auth');

const K8S_TOKEN_USER_KEY = 'kubernetes.io/serviceaccount/namespace';
const K8S_API_URL = process.env.NODE_ENV === 'dev' ? 'http://localhost:9090' : 'https://kubernetes.default';
const API_GROUP_NAME = 'aipg.intel.com';
const EXPERIMENTS_VERSION = 'v1';

module.exports.listNamespacedCustomObject = function (token, resourceName, customApiGroupName) {
  return Q.Promise(function (resolve, reject) {
    authApi.decodeToken(token)
      .then(function (decoded) {
        const namespace = decoded[K8S_TOKEN_USER_KEY];
        const options = {
          url: `${K8S_API_URL}/apis/${customApiGroupName || API_GROUP_NAME}/${EXPERIMENTS_VERSION}/namespaces/${namespace}/${resourceName}`,
          headers: {
            authorization: `Bearer ${token}`
          }
        };
        logger.debug('Performing request to kubernetes API for fetching experiments data');
        return request(options);
      })
      .then(function (data) {
        if (typeof (data) === 'object') {
          resolve(data);
        }
        reject(errHandler(HttpStatus.INTERNAL_SERVER_ERROR, errMessages.K8S.CUSTOM_OBJECT.CANNOT_LIST));
      })
      .catch(function (err) {
        reject(err);
      });
  });
};

module.exports.listClusterCustomObject = function (token, resourceName, customApiGroupName) {
  return Q.Promise(function (resolve, reject) {
    authApi.decodeToken(token)
      .then(function () {
        const options = {
          url: `${K8S_API_URL}/apis/${customApiGroupName || API_GROUP_NAME}/${EXPERIMENTS_VERSION}/${resourceName}`,
          headers: {
            authorization: `Bearer ${token}`
          }
        };
        logger.debug('Performing request to kubernetes API for fetching all experiments data');
        return request(options);
      })
      .then(function (data) {
        if (typeof (data) === 'object') {
          resolve(data);
        }
        reject(errHandler(HttpStatus.INTERNAL_SERVER_ERROR, errMessages.K8S.CUSTOM_OBJECT.CANNOT_LIST));
      })
      .catch(function (err) {
        reject(err);
      });
  });
};

module.exports.listPodsByLabelValue = function (token, labelName, labelValue) {
  return Q.Promise(function (resolve, reject) {
    authApi.decodeToken(token)
      .then(function () {
        let url = `${K8S_API_URL}/api/v1/pods`;
        if (labelName && labelValue) {
          url = `${url}?labelSelector=${labelName}=${labelValue}`
        }
        const options = {
          url: url,
          headers: {
            authorization: `Bearer ${token}`
          }
        };
        logger.debug('Performing request to kubernetes API for fetching pods data');
        return request(options);
      })
      .then(function (data) {
        if (typeof (data) === 'object') {
          resolve(data);
        }
        reject(errHandler(HttpStatus.INTERNAL_SERVER_ERROR, errMessages.K8S.PODS.CANNOT_LIST));
      })
      .catch(function (err) {
        reject(err);
      });
  });
};

const getFormattedState = function (stateObj) {
  let result = '';
  Object.keys(stateObj).forEach((key) => {
    result += `${key}: ${stateObj[key]}; `;
  });
  return result;
};

module.exports.parseContainerState = function (state) {
  if (!state) {
    return 'Not created';
  }
  if (state.running) {
    return `Running, ${typeof (state.running) === 'object' ? getFormattedState(state.running) : state.running}`;
  }
  if (state.terminated) {
    return `Terminated, ${typeof (state.terminated) === 'object' ? getFormattedState(state.terminated) : state.terminated}`;
  }
  if (state.waiting) {
    return `Waiting, ${typeof (state.waiting) === 'object' ? getFormattedState(state.waiting) : state.waiting}`;
  }
};
