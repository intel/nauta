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
const request = require('request');
const logger = require('./logger');
const HttpStatus = require('http-status-codes');
const errHandler = require('./error-handler');
const errMessages = require('./error-messages');
const Q = require('q');

module.exports = function (options) {
  return Q.Promise(function (resolve, reject) {
    request(options, function (err, response, body) {
      if (err) {
        logger.error('Request to api failed.', err);
        reject(errHandler(HttpStatus.INTERNAL_SERVER_ERROR, err));
      }
      if (response) {
        if (response.statusCode === HttpStatus.INTERNAL_SERVER_ERROR) {
          logger.debug('Internal Server Error');
          reject(errHandler(HttpStatus.INTERNAL_SERVER_ERROR, errMessages.GENERAL.INTERNAL_SERVER_ERROR));
        }
        if (response.statusCode === HttpStatus.UNAUTHORIZED) {
          logger.debug('Unauthorized request to API');
          reject(errHandler(HttpStatus.UNAUTHORIZED, errMessages.AUTH.UNAUTHORIZED_OPERATION));
        }
        if (response.statusCode === HttpStatus.FORBIDDEN) {
          logger.debug('Forbidden request to API');
          reject(errHandler(HttpStatus.FORBIDDEN, errMessages.AUTH.FORBIDDEN_OPERATION));
        }
        logger.debug('Data from API has been retrieved');

        try {
          const data = JSON.parse(body);
          resolve(data);
        } catch (err) {
          logger.warn('Cannot parse response body');
        }
        resolve(body);
      }
    });
  })
};
