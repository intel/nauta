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
const elasticsearch = require('elasticsearch');
const logger = require('../../utils/logger');
const errMessages = require('../../utils/error-messages');
const HttpStatus = require('http-status-codes');
const k8s = require('../../utils/k8s');
const elasticsearchUtils = require('../../utils/nauta-elasticsearch');
const datetimeUtils = require('../../utils/datetime-utils');

const generateExperimentEntities = function (runsData, expsData) {
  if (!Array.isArray(runsData) || !Array.isArray(expsData)) {
    return [];
  }
  const runsExtendedInfo = {};
  expsData.forEach(function (exp) {
    const name = exp.metadata.name;
    runsExtendedInfo[name] = {
      'template-name': exp.spec['template-name'],
      'template-namespace': exp.spec['template-namespace'],
      'template-version': exp.spec['template-version']
    }
  });
  return runsData.map(function (item) {
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
        parameters: item.spec['parameters'],
        'template-name': runsExtendedInfo[item.metadata.name]['template-name'],
        'template-namespace': runsExtendedInfo[item.metadata.name]['template-namespace'],
        'template-version': runsExtendedInfo[item.metadata.name]['template-version']
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

const TIME_ATTRIBUTES = ['creationTimestamp', 'trainingStartTime', 'trainingEndTime'];

const prepareDataUsingFilters = function (entities, valuesPattern, searchbox) {
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
    searchPattern: searchbox && searchbox.pattern ? searchbox.pattern.toUpperCase() : '',
    searchTimezone: searchbox && searchbox.timezoneOffset ? searchbox.timezoneOffset : new Date().getTimezoneOffset()
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
      let attrValue = String(item.attributes[key]);
      if (attrValue && TIME_ATTRIBUTES.includes(key)) {
        attrValue = datetimeUtils.getLocaleStringForOffset(attrValue, filterParams.searchTimezone);
      }
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

const parseExperiments = function (runs, experiments, queryParams) {
  const entities = generateExperimentEntities(runs, experiments);
  const preparedData = prepareDataUsingFilters(entities, {
    name: queryParams.names,
    namespace: queryParams.namespaces,
    state: queryParams.states,
    type: queryParams.types
  }, {
    pattern: queryParams.searchBy,
    timezoneOffset: queryParams.timezoneOffset
  });
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
  const expsResourceName = 'experiments';
  if (!req.headers.authorization) {
    logger.debug('Missing authorization token');
    res.status(HttpStatus.UNAUTHORIZED).send({message: errMessages.AUTH.MISSING_TOKEN});
    return;
  }
  const token = req.headers.authorization;
  const queryParams = {
    ...req.query,
    timezoneOffset: req.headers['timezone-offset']
  };
  logger.debug(queryParams);
  let expCustomObjects = null, runCustomObjects = null;
  k8s.listClusterCustomObject(token, runsResourceName)
    .then(function (runsData) {
      logger.info('Runs retrieved');
      runCustomObjects = runsData.items;
      const API_GROUP_NAME = 'aipg.intel.com';
      return k8s.listClusterCustomObject(token, expsResourceName, API_GROUP_NAME);
    })
    .then(function (expsData) {
      logger.info('Experiments retrieved');
      expCustomObjects = expsData.items;
      logger.debug('Preparation data');
      const experiments = parseExperiments(runCustomObjects, expCustomObjects, queryParams);
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
              resources: container.resources,
              status: k8s.parseContainerState(containerStatuses[container.name])
            }
          })
        };
      });
      logger.debug(JSON.stringify(result));
      res.send(result);
    })
    .catch(function (err) {
      logger.error('Cannot get pods');
      res.status(err.status).send({message: err.message});
    })
};

const getExperimentLogs = function (req, res) {
  const runName = req.params.experiment;
  const owner = req.params.owner;
  const mode = req.params.mode;
  const number = req.params.number;

  if (!runName || !owner || !mode || !number) {
    res.status(HttpStatus.BAD_REQUEST).send({message: errMessages.GENERAL.BAD_REQUEST});
    return;
  }

  const contentSeparator = mode === 'show' ? '<br/>' : '\n';

  elasticsearchUtils.getRunLastLogs(contentSeparator, runName, owner, number)
    .then(function (logs) {
      logger.info('Sending logs');
      res.send(logs);
    })
    .catch(function (err) {
      logger.error('Cannot get logs for experiment');
      res.status(err.status).send({message: err.message});
    })
};

const getAllExperimentLogs = async function (req, res) {
  const runName = req.params.experiment;
  const owner = req.params.owner;

  if (!runName || !owner) {
    res.status(HttpStatus.BAD_REQUEST).send({message: errMessages.GENERAL.BAD_REQUEST});
    return;
  }

  logger.info('Searching logs in Elasticsearch service');

  const client = new elasticsearch.Client({
    host: elasticsearchUtils.getElasticsearchServiceUrl()
  });

  let response = null;

  try {
    response = await client.search({
      index: '_all',
      scroll: '30s',
      q: elasticsearchUtils.getLuceneQuery(runName, owner),
      sort: '@timestamp:asc',
      size: 20
    });
  } catch (err) {
    logger.error('Cannot get logs from elasticsearch');
    res.status(HttpStatus.INTERNAL_SERVER_ERROR).send({message: errMessages.ELASTICSEARCH.CANNOT_GET_SEARCH_RESULT});
    return;
  }

  logger.debug('Received first chunk of logs from Elasticsearch service');

  res.writeHead(200, {
    'Content-Type': 'text/plain',
    'Transfer-Encoding': 'chunked'
  });

  let queue = [];
  queue.push(response);

  let counter = 0;
  while (queue.length) {
    const response = queue.shift();

    response.hits.hits.forEach(function (item) {
      const entry = elasticsearchUtils.parseLogEntry(item);
      res.write(entry);
      counter++;
    });

    if (response.hits.total === counter) {
      logger.info('Received last chunk of logs from Elasticsearch service');
      res.end();
      break;
    }

    try {
      logger.debug('Scrolling logs');
      queue.push(
        await client.scroll({
          scrollId: response._scroll_id,
          scroll: '30s'
        })
      );
    } catch (err) {
      logger.error('Cannot scroll logs from elasticsearch');
      res.status(HttpStatus.INTERNAL_SERVER_ERROR).send({message: errMessages.ELASTICSEARCH.CANNOT_GET_SEARCH_RESULT});
      return;
    }
  }
};

module.exports = {
  getUserExperiments: getUserExperiments,
  parseExperiments: parseExperiments,
  prepareDataUsingFilters: prepareDataUsingFilters,
  extractAttrsNames: extractAttrsNames,
  applyOrderParams: applyOrderParams,
  generateExperimentEntities: generateExperimentEntities,
  getExperimentResourcesData: getExperimentResourcesData,
  getExperimentLogs: getExperimentLogs,
  getAllExperimentLogs: getAllExperimentLogs
};
