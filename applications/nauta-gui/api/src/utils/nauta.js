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

module.exports.createTensorBoardInstance = function (token, experiments) {
  return Q.Promise(function (resolve, reject) {
    authApi.decodeToken(token)
      .then(function (decoded) {
        const namespace = decoded[K8S_TOKEN_USER_KEY];
        const url = `${getTensorBoardServiceUrl(namespace)}/tensorboard`;
        const options = {
          url: url,
          body: {
            runNames: experiments
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
