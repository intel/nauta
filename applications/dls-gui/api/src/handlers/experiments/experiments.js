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
const errMessages = require('../../utils/error-messages');
const HttpStatus = require('http-status-codes');
const k8s = require('../../utils/k8s');

const parseExperiments = function (experiments, queryParams) {
  let data = {};
  experiments.forEach(function (experiment) {
    let entity = {
      creationTimestamp: experiment.metadata.creationTimestamp,
      name: experiment.metadata.name,
      namespace: experiment.metadata.namespace,
      podSelector: experiment.spec['pod-selector']['matchLabels'],
      podCount: experiment.spec['pod-count'],
      state: experiment.spec['state'],
      parameters: experiment.spec['parameters']
    };
    Object.keys(experiment.spec['metrics']).map((metricName) => {
      entity[metricName] = experiment.spec['metrics'][metricName];
    });
    data[entity.name] = entity;
  });

  let result = {
    stats: {
      total: experiments.length,
      datetime: Date.now()
    }
  };

  let fullData = _.values(data);

  if (queryParams) {
    if (queryParams.searchBy) {
      logger.debug('Filtering data by');
      const pattern = queryParams.searchBy;
      fullData = _.filter(fullData, (item) => {
        if (item.name.toUpperCase().indexOf(pattern.toUpperCase()) !== -1) {
          return item;
        }
      });
      result.stats.total = fullData.length;
    }
    if (queryParams.orderBy && queryParams.order) {
      logger.debug('Sorting by');
      const orderByColumn = queryParams.orderBy;
      const order = queryParams.order;
      fullData = _.orderBy(fullData, [orderByColumn], [order]);
    }
    if (queryParams.limit && queryParams.page) {
      logger.debug('Getting page limiting by number of rows');
      const page = queryParams.page;
      const limit = queryParams.limit;
      const a = (page - 1) * limit;
      const b = page * limit;
      result.stats.a = a + 1;
      result.stats.b = b > fullData.length ? fullData.length : b;
      result.stats.totalPagesCount = Math.ceil(fullData.length / limit);
      result.stats.pageNumber = page > result.stats.totalPagesCount ? result.stats.totalPagesCount : page;
      fullData = fullData.slice(a, b);
    }
  }
  let set = new Set();
  fullData.map((exp) => {
    _.keys(exp).forEach((p) => {
      set.add(p);
    })
  });
  result.params = Array.from(set);
  result.data = fullData;
  return result;
};

const getUserExperiments = function (req, res) {
  const runsResourceName = 'runs';
  if (!req.headers.authorization) {
    logger.debug('Missing authorization token');
    res.status(HttpStatus.UNAUTHORIZED).send({message: errMessages.AUTH.MISSING_TOKEN});
  }
  const token = req.headers.authorization;
  const queryParams = req.query;
  logger.debug(queryParams);
  k8s.listNamespacedCustomObject(token, runsResourceName)
    .then(function (data) {
      logger.info('Experiments retrieved');
      logger.debug('Preparation data');
      const experiments = parseExperiments(data.items, queryParams);
      res.send(experiments);
    })
    .catch(function (err) {
      logger.error('Cannot get experiments');
      res.status(err.status).send({message: err.message});
    })
};

module.exports = {
  parseExperiments: parseExperiments,
  getUserExperiments: getUserExperiments
};
