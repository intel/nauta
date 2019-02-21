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

const logger = require('./logger');
const HttpStatus = require('http-status-codes');
const errHandler = require('./error-handler');
const request = require('./requestWrapper');
const errMessages = require('./error-messages');
const Q = require('q');
const authApi = require('../../src/handlers/auth/auth');

const K8S_TOKEN_USER_KEY = 'kubernetes.io/serviceaccount/namespace';
const K8S_API_URL = process.env.NODE_ENV === 'dev' ? 'http://localhost:9090' : 'https://kubernetes.default';
const API_GROUP_NAME = 'aggregator.aipg.intel.com';
const EXPERIMENTS_VERSION = 'v1';

module.exports.listNamespacedCustomObject = function (token, resourceName) {
  return Q.Promise(function (resolve, reject) {
    authApi.decodeToken(token)
      .then(function (decoded) {
        const namespace = decoded[K8S_TOKEN_USER_KEY];
        const options = {
          url: `${K8S_API_URL}/apis/${API_GROUP_NAME}/${EXPERIMENTS_VERSION}/namespaces/${namespace}/${resourceName}`,
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

module.exports.listClusterCustomObject = function (token, resourceName) {
  return Q.Promise(function (resolve, reject) {
    authApi.decodeToken(token)
      .then(function () {
        const options = {
          url: `${K8S_API_URL}/apis/${API_GROUP_NAME}/${EXPERIMENTS_VERSION}/${resourceName}`,
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
