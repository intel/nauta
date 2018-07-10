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

const _ = require('lodash');
const logger = require('../../utils/logger');
const dls4e = require('../../utils/dls4e');
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

  dls4e.createTensorBoardInstance(token, experiments)
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

  dls4e.getTensorboardInstanceState(token, instanceId)
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
