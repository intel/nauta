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

const elasticsearch = require('elasticsearch');
const HttpStatus = require('http-status-codes');
const Q = require('q');
const logger = require('./logger');
const errHandler = require('./error-handler');
const errMessages = require('./error-messages');

const ELASTICSEARCH_SERVICE = 'nauta-elasticsearch';
const ELASTICSEARCH_NAMESPACE = 'nauta';
const ELASTICSEARCH_PORT = 9200;

const getElasticsearchServiceUrl = function () {
  const devUrl = `http://localhost:9090/api/v1/namespaces/${ELASTICSEARCH_NAMESPACE}/services/${ELASTICSEARCH_SERVICE}:nauta/proxy`;
  const prodUrl = `http://${ELASTICSEARCH_SERVICE}.${ELASTICSEARCH_NAMESPACE}:${ELASTICSEARCH_PORT}`;
  return process.env.NODE_ENV === 'dev' ? devUrl : prodUrl;
};

const getLuceneQuery = function (runName, namespace) {
  return `kubernetes.labels.runName.keyword:"${runName}" AND kubernetes.namespace_name.keyword:"${namespace}"`;
};

const parseLogEntry = function (entry) {
  const timestamp = entry['_source']['@timestamp'];
  const podName = entry['_source']['kubernetes']['pod_name'];
  const logMessage = entry['_source']['log'];
  return `${timestamp} ${podName} ${logMessage}`;
};

const makeSearch = async function (runName, namespace, lines, sort) {
  const client = new elasticsearch.Client({
    host: getElasticsearchServiceUrl()
  });
  const data = await client.search({
    index: '_all',
    scroll: '30s',
    q: getLuceneQuery(runName, namespace),
    sort: sort || '@timestamp:desc',
    size: lines || 20
  });
  return {
    data,
    client
  };
};

const getRunLastLogs = function (separator, runName, namespace, lines) {
  return Q.Promise(function (resolve, reject) {
    makeSearch(runName, namespace, lines)
      .then(function (res) {
        logger.debug('Elasticsearch response received');
        const data = res.data;
        if (data && data.hits && data.hits.hits) {
          logger.debug('Parsing log entries for current search');
          const logs = data.hits.hits.map((entry) => parseLogEntry(entry));
          const sortedLogs = logs.sort().join(separator || '');
          resolve(sortedLogs);
        } else {
          resolve('No data');
        }
      })
      .catch(function () {
        reject(errHandler(HttpStatus.INTERNAL_SERVER_ERROR, errMessages.ELASTICSEARCH.CANNOT_GET_SEARCH_RESULT));
      });
  });
};

module.exports = {
  getRunLastLogs: getRunLastLogs,
  makeSearch: makeSearch,
  parseLogEntry: parseLogEntry,
  getElasticsearchServiceUrl: getElasticsearchServiceUrl,
  getLuceneQuery: getLuceneQuery
};
