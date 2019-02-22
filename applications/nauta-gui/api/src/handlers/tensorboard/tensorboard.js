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
const _ = require('lodash');
const logger = require('../../utils/logger');
const nauta = require('../../utils/nauta');
const errMessages = require('../../utils/error-messages');
const HttpStatus = require('http-status-codes');

const createTensorBoardInstance = function (req, res) {
  if (!req.headers.authorization) {
    logger.debug('Missing authorization token');
    res.status(HttpStatus.UNAUTHORIZED).send({message: errMessages.AUTH.MISSING_TOKEN});
    return;
  }
  if (!req.body || !req.body.items || !req.body.items.length) {
    logger.debug('Missing request body with experiments data');
    res.status(HttpStatus.BAD_REQUEST).send({message: errMessages.GENERAL.BAD_REQUEST});
    return;
  }
  const token = req.headers.authorization;
  const experiments = req.body.items;
  logger.debug('Experiments data received');

  nauta.createTensorBoardInstance(token, experiments)
    .then((instance) => {
      logger.debug('Received tensorboard instance url', instance);
      logger.info('Tensorboard instance has been created');
      res.send(instance);
    })
    .catch(function (err) {
      logger.error('Cannot create required tensorboard instance', err);
      res.status(err.status).send({message: err.message});
    });
};

const getTensorBoardInstanceState = function (req, res) {
  if (!req.headers.authorization) {
    logger.debug('Missing authorization token');
    res.status(HttpStatus.UNAUTHORIZED).send({message: errMessages.AUTH.MISSING_TOKEN});
    return;
  }
  if (!req.params.id) {
    logger.debug('Missing request param with instance id');
    res.status(HttpStatus.BAD_REQUEST).send({message: errMessages.GENERAL.BAD_REQUEST});
    return;
  }
  const token = req.headers.authorization;
  const instanceId = req.params.id;
  logger.debug('Instance ID received: ', instanceId);

  nauta.getTensorboardInstanceState(token, instanceId)
    .then((data) => {
      logger.debug('Received status of TB instance', data);
      logger.info(`Status for ${instanceId} TB instance received`);
      res.send(data);
    })
    .catch(function (err) {
      logger.error('Cannot get status of tensorboard instance', err);
      res.status(err.status).send({message: err.message});
    });
};

module.exports = {
  createTensorBoardInstance: createTensorBoardInstance,
  getTensorBoardInstanceState: getTensorBoardInstanceState
};
