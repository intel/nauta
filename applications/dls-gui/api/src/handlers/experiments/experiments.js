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

const generateExperimentEntities = function (data) {
  if (!Array.isArray(data)) {
    return [];
  }
  return data.map(function (item) {
    let entity = {
      attributes: {
        creationTimestamp: item.metadata.creationTimestamp,
        name: item.metadata.name,
        namespace: item.metadata.namespace,
        state: item.spec['state']
      },
      params: {
        podSelector: item.spec['pod-selector']['matchLabels'],
        podCount: item.spec['pod-count'],
        parameters: item.spec['parameters']
      }
    };
    if (item.spec['metrics']) {
      Object.keys(item.spec['metrics']).map((metricName) => {
        entity.attributes[metricName] = item.spec['metrics'][metricName];
      });
    }
    return entity;
  });
};

const extractValuesForFilterableAttrs = function (entities) {
  let values = {
    name: new Set(),
    state: new Set(),
    namespace: new Set()
  };
  entities.forEach((entity) => {
    values.name.add(entity.attributes.name);
    values.state.add(entity.attributes.state);
    values.namespace.add(entity.attributes.namespace);
  });
  return {
    name: Array.from(values.name),
    namespace: Array.from(values.namespace),
    state: Array.from(values.state)
  };
};

const applyQueryFilters = function (entities, valuesPattern, searchPattern) {
  if (!Array.isArray(entities)) {
    throw 'Incorrect Array Data';
  }

  let filterParams = {
    name: Array.from(new Set(entities.map((entity) => entity.attributes.name))),
    namespace: Array.from(new Set(entities.map((entity) => entity.attributes.namespace))),
    state: Array.from(new Set(entities.map((entity) => entity.attributes.state))),
    searchPattern: searchPattern ? searchPattern.toUpperCase() : ''
  };

  if (valuesPattern) {
    Object.keys(valuesPattern).forEach((attr) => {
      if (Array.isArray(valuesPattern[attr])) {
        filterParams[attr] = valuesPattern[attr];
      }
    });
  }

  const filteredEntities = entities.filter((item) => {
    const filterByValueCondition = filterParams.name.includes(item.attributes.name) &&
      filterParams.namespace.includes(item.attributes.namespace) &&
      filterParams.state.includes(item.attributes.state);
    const filterBySearchCondition = Object.keys(item.attributes).some((key) => {
      const attrValue = String(item.attributes[key]);
      return attrValue.toUpperCase().includes(filterParams.searchPattern);
    });
    return filterByValueCondition && filterBySearchCondition;
  });

  return {
    data: filteredEntities,
    queryParams: filterParams
  }
};

const applyOrderParams = function (entities, orderBy, order, limitPerPage, pageNo) {
  if (!Array.isArray(entities)) {
    throw 'Incorrect Array Data';
  }
  const orderParams = {
    orderBy: orderBy || '',
    order: order || '',
    limitPerPage: limitPerPage || entities.length || 1,
    pageNo: pageNo || 1
  };
  const sortedEntities = _.orderBy(entities, [`attributes[${orderParams.orderBy}]`], [orderParams.order]);
  const a = (orderParams.pageNo - 1) * orderParams.limitPerPage;
  const b = orderParams.pageNo * orderParams.limitPerPage;
  const slicedEntities = sortedEntities.slice(a, b);
  const totalPages = Math.ceil(entities.length / orderParams.limitPerPage);
  return {
    data: slicedEntities,
    a: slicedEntities.length ? a + 1 : 0,
    b: b > entities.length ? entities.length : b,
    totalPagesCount: Math.ceil(entities.length / orderParams.limitPerPage),
    pageNumber: orderParams.pageNo > totalPages ? totalPages : orderParams.pageNo
  }
};

const extractAttrsNames = function (data) {
  if (!Array.isArray(data)) {
    throw 'Incorrect Array Data';
  }
  let attrsSet = new Set();
  data.map((exp) => {
    _.keys(exp.attributes).forEach((p) => {
      attrsSet.add(p);
    })
  });
  return Array.from(attrsSet);
};

const parseExperiments = function (experiments, queryParams) {
  const entities = generateExperimentEntities(experiments);
  const valuesForFilterableAttrs = extractValuesForFilterableAttrs(entities);
  const filteredDataWithMetadata = applyQueryFilters(entities, {
    name: queryParams.names,
    namespace: queryParams.namespaces,
    state: queryParams.states
  }, queryParams.searchBy);
  const orderedData = applyOrderParams(filteredDataWithMetadata.data, queryParams.orderBy, queryParams.order, queryParams.limit, queryParams.page);
  return {
    stats: {
      total: entities.length,
      datetime: Date.now(),
      filteredDataCount: filteredDataWithMetadata.data.length,
      a: orderedData.a,
      b: orderedData.b,
      totalPagesCount: orderedData.totalPagesCount,
      pageNumber: orderedData.pageNumber
    },
    filterColumnValues: {
      options: valuesForFilterableAttrs,
      current: filteredDataWithMetadata.queryParams
    },
    params: extractAttrsNames(entities),
    data: orderedData.data
  };
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
  k8s.listClusterCustomObject(token, runsResourceName)
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
  getUserExperiments: getUserExperiments,
  parseExperiments: parseExperiments,
  extractAttrsNames: extractAttrsNames,
  applyOrderParams: applyOrderParams,
  applyQueryFilters: applyQueryFilters,
  extractValuesForFilterableAttrs: extractValuesForFilterableAttrs,
  generateExperimentEntities: generateExperimentEntities
};
