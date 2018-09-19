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
const datetimeUtils = require('../../utils/datetime-utils');

const generateExperimentEntities = function (data) {
  if (!Array.isArray(data)) {
    return [];
  }
  return data.map(function (item) {
    let entity = {
      attributes: {
        name: item.metadata.name,
        state: item.spec.state,
        creationTimestamp: item.metadata.creationTimestamp,
        trainingStartTime: item.spec['start-time'],
        trainingEndTime: item.spec['end-time'],
        trainingDurationTime: datetimeUtils.calculateTimeDifferenceFromDateString(
          item.spec['start-time'], item.spec['end-time']),
        trainingTimeInQueue: datetimeUtils.calculateTimeDifferenceFromDateString(
          item.metadata.creationTimestamp, item.spec['start-time']),
        type: item.metadata.labels.runKind,
        namespace: item.metadata.namespace,
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

const prepareDataUsingFilters = function (entities, valuesPattern, searchPattern) {
  if (!Array.isArray(entities)) {
    throw 'Incorrect Array Data';
  }

  let values = {
    name: new Set(),
    state: new Set(),
    namespace: new Set(),
    type: new Set()
  };
  entities.forEach((entity) => {
    values.namespace.add(entity.attributes.namespace);
  });

  let filterParams = {
    name: Array.from(new Set(entities.map((entity) => entity.attributes.name))),
    namespace: Array.from(new Set(entities.map((entity) => entity.attributes.namespace))),
    state: Array.from(new Set(entities.map((entity) => entity.attributes.state))),
    type: Array.from(new Set(entities.map((entity) => entity.attributes.type))),
    searchPattern: searchPattern ? searchPattern.toUpperCase() : ''
  };

  if (valuesPattern) {
    Object.keys(valuesPattern).forEach((attr) => {
      if (Array.isArray(valuesPattern[attr])) {
        filterParams[attr] = valuesPattern[attr];
      }
    });
  }

  const filteredByUserEntities = entities.filter((item) => {
    return filterParams.namespace.includes(item.attributes.namespace);
  });

  const filteredEntities = entities.filter((item) => {
    const filterByValueCondition = filterParams.name.includes(item.attributes.name) &&
      filterParams.namespace.includes(item.attributes.namespace) &&
      filterParams.state.includes(item.attributes.state) &&
      filterParams.type.includes(item.attributes.type);
    const filterBySearchCondition = Object.keys(item.attributes).some((key) => {
      const attrValue = String(item.attributes[key]);
      return attrValue.toUpperCase().includes(filterParams.searchPattern);
    });
    return filterByValueCondition && filterBySearchCondition;
  });

  filteredByUserEntities.forEach((entity) => {
    values.name.add(entity.attributes.name);
    values.state.add(entity.attributes.state);
    values.type.add(entity.attributes.type);
  });

  return {
    data: filteredEntities,
    queryParams: filterParams,
    valuesForFilterableAttrs: {
      name: Array.from(values.name),
      namespace: Array.from(values.namespace),
      state: Array.from(values.state),
      type: Array.from(values.type)
    }
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
    });
  });
  return Array.from(attrsSet);
};

const parseExperiments = function (experiments, queryParams) {
  const entities = generateExperimentEntities(experiments);
  const preparedData = prepareDataUsingFilters(entities, {
    name: queryParams.names,
    namespace: queryParams.namespaces,
    state: queryParams.states,
    type: queryParams.types
  }, queryParams.searchBy);
  const orderedData = applyOrderParams(preparedData.data, queryParams.orderBy, queryParams.order, queryParams.limit, queryParams.page);
  return {
    stats: {
      total: entities.length,
      datetime: Date.now(),
      filteredDataCount: preparedData.data.length,
      a: orderedData.a,
      b: orderedData.b,
      totalPagesCount: orderedData.totalPagesCount,
      pageNumber: orderedData.pageNumber
    },
    filterColumnValues: {
      options: preparedData.valuesForFilterableAttrs,
      current: preparedData.queryParams
    },
    params: extractAttrsNames(preparedData.data),
    data: orderedData.data
  };
};

const getUserExperiments = function (req, res) {
  const runsResourceName = 'runs';
  if (!req.headers.authorization) {
    logger.debug('Missing authorization token');
    res.status(HttpStatus.UNAUTHORIZED).send({message: errMessages.AUTH.MISSING_TOKEN});
    return;
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

const getExperimentResourcesData = function (req, res) {
  if (!req.headers.authorization) {
    logger.debug('Missing authorization token');
    res.status(HttpStatus.UNAUTHORIZED).send({message: errMessages.AUTH.MISSING_TOKEN});
    return;
  }
  const token = req.headers.authorization;
  const experimentName = req.params.experiment;
  if (!experimentName) {
    res.status(HttpStatus.BAD_REQUEST).send({message: errMessages.GENERAL.BAD_REQUEST});
    return;
  }
  const labelName = 'runName';
  const labelValue = experimentName;

  k8s.listPodsByLabelValue(token, labelName, labelValue)
    .then(function (data) {
      logger.info('Pods data retrieved');
      const result = data.items.map((pod) => {
        const podStatusString = pod.status.conditions.map((cond) => {
          let msg = cond.reason ? `, reason: ${cond.reason}` : '';
          msg = cond.message ? `${msg}, message: ${cond.message}` : msg;
          return `${cond.type}: ${cond.status} ${msg}`;
        });
        let containerStatuses = {};
        if (pod.status.containerStatuses) {
          pod.status.containerStatuses.forEach((containerStatus) => {
            containerStatuses[containerStatus.name] = containerStatus.state;
          });
        }
        return {
          name: pod.metadata.name,
          state: podStatusString,
          containers: pod.spec.containers.map((container) => {
            return {
              name: container.name,
              resources: container.resources.requests ? container.resources.requests : container.resources,
              status: k8s.parseContainerState(containerStatuses[container.name])
            }
          })
        };
      });
      res.send(result);
    })
    .catch(function (err) {
      logger.error('Cannot get pods');
      res.status(err.status).send({message: err.message});
    })
};

module.exports = {
  getUserExperiments: getUserExperiments,
  parseExperiments: parseExperiments,
  prepareDataUsingFilters: prepareDataUsingFilters,
  extractAttrsNames: extractAttrsNames,
  applyOrderParams: applyOrderParams,
  generateExperimentEntities: generateExperimentEntities,
  getExperimentResourcesData: getExperimentResourcesData
};
