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
const logger = require('../../utils/logger');
const errHandler = require('../../utils/error-handler');
const errMessages = require('../../utils/error-messages');
const Q = require('q');
const HttpStatus = require('http-status-codes');

const K8S_TOKEN_USER_KEY = 'kubernetes.io/serviceaccount/namespace';

const parseJwtToken = function (token) {
  try {
    const base64Url = token.split('.')[1];
    const base64 = base64Url.replace('-', '+').replace('_', '/');
    return JSON.parse(Buffer.from(base64, 'base64').toString());
  } catch (err) {
    logger.debug('Cannot parse provided token');
    return null;
  }
};

const decodeToken = function (token) {
  return Q.Promise(function (resolve, reject) {
    if (!token) {
      reject(errHandler(HttpStatus.UNAUTHORIZED, errMessages.AUTH.INVALID_TOKEN));
    }
    const decoded = parseJwtToken(token);
    if (decoded && decoded[K8S_TOKEN_USER_KEY]) {
      logger.debug('Provided token is valid');
      resolve(decoded);
    } else {
      logger.debug('Provided token is invalid');
      reject(errHandler(HttpStatus.UNAUTHORIZED, errMessages.AUTH.INVALID_TOKEN));
    }
  });
};

const getUserAuthority = function (req, res) {
  if (!req.body.token) {
    logger.debug('Missing token in request body');
    res.status(HttpStatus.BAD_REQUEST).send({message: errMessages.AUTH.MISSING_TOKEN});
    return;
  }
  decodeToken(req.body.token)
    .then(function (decoded) {
      logger.info('Token decoded. Data sent to user');
      res.send({decoded: {username: decoded[K8S_TOKEN_USER_KEY]}});
    })
    .catch(function (err) {
      logger.debug('Cannot decode provided token');
      res.status(err.status).send({message: err.message});
    });
};

module.exports = {
  getUserAuthority: getUserAuthority,
  decodeToken: decodeToken,
  parseJwtToken: parseJwtToken
};
