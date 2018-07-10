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
const request = require('./requestWrapper');
const Q = require('q');
const authApi = require('../../src/handlers/auth/auth');

const K8S_TOKEN_USER_KEY = 'kubernetes.io/serviceaccount/namespace';
const TENSORBOARD_SERVICE_NAME = 'tensorboard-service';

const getTensorBoardServiceUrl = function (namespace) {
  const devUrl = `http://localhost:9090/api/v1/namespaces/${namespace}/services/tensorboard-service:web/proxy`;
  const prodUrl = `http://${TENSORBOARD_SERVICE_NAME}.${namespace}`;
  return process.env.NODE_ENV === 'dev' ? devUrl : prodUrl;
};

module.exports.createTensorBoardInstance = function (token, experimentName) {
  return Q.Promise(function (resolve, reject) {
    authApi.decodeToken(token)
      .then(function (decoded) {
        const namespace = decoded[K8S_TOKEN_USER_KEY];
        const url = `${getTensorBoardServiceUrl(namespace)}/tensorboard`;
        const options = {
          url: url,
          body: {
            runNames: experimentName
          },
          json: true,
          method: 'POST'
        };
        logger.debug('Performing request to tensorboard service');
        return request(options);
      })
      .then(function (data) {
        resolve(data);
      })
      .catch(function (err) {
        reject(err);
      });
  });
};

module.exports.getTensorboardInstanceState = function (token, instanceId) {
  return Q.Promise(function (resolve, reject) {
    authApi.decodeToken(token)
      .then(function (decoded) {
        const namespace = decoded[K8S_TOKEN_USER_KEY];
        const url = `${getTensorBoardServiceUrl(namespace)}/tensorboard/${instanceId}`;
        const options = {
          url: url,
          method: 'GET'
        };
        logger.debug('Performing request to tensorboard service');
        return request(options);
      })
      .then(function (data) {
        resolve(data);
      })
      .catch(function (err) {
        reject(err);
      });
  });
};
