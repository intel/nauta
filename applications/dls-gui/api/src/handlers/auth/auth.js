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

const logger = require('../../utils/logger');
const jwt = require('jsonwebtoken');

module.exports.decodeToken = function (req, res) {
  if (!req.body.token) {
    logger.debug('Missing token in request body');
    res.status(400).send({error: 'Missing token'});
    return;
  }
  try {
    const decoded = jwt.decode(req.body.token);
    if (!decoded) {
      throw new Error('Cannot decode received token');
    }
    if (!decoded['kubernetes.io/serviceaccount/service-account.name']) {
      throw new Error('Token decoded but is not valid for DLS4E');
    }
    logger.debug('Token decoded. Data sent to user');
    res.send({decoded: decoded});
  } catch (err) {
    logger.debug('Cannot decode provided token');
    res.status(401).send({error: 'Cannot decode provided token'});
  }
};
