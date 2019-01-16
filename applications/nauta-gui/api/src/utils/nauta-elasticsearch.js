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
