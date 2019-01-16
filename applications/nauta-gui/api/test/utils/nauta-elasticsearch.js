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
const expect = require('chai').expect;
const sinon = require('sinon');
const rewire = require('rewire');
const Q = require('q');
const elasticSearchUtils = rewire('../../src/utils/nauta-elasticsearch');
const HttpStatus = require('http-status-codes');
const errMessages = require('../../src/utils/error-messages');

describe('Utils | nauta-elasticsearch', function () {

  let elasticsearchClientMock, deferred, error, runName, namespace, entry, lines, data;

  beforeEach(function () {
    deferred = Q.defer();
    elasticsearchClientMock = sinon.stub().returns({
      search: sinon.stub().returns(deferred)
    });
    error = {
      status: HttpStatus.INTERNAL_SERVER_ERROR,
      message: errMessages.ELASTICSEARCH.CANNOT_GET_SEARCH_RESULT
    };
    runName = 'experiment';
    namespace = 'owner';
    lines = 10;
    entry = {
      '_source': {
        '@timestamp': '123',
        kubernetes: {
          pod_name: 'pod1'
        },
        log: 'log1'
      }
    };
    data = {
      hits: {
        hits: [entry, entry, entry]
      }
    }
  });

  describe('parseLogEntry', function () {

    it('should return static text for entry object', function () {
      const expectedResult = `${entry['_source']['@timestamp']} ${entry['_source']['kubernetes']['pod_name']} ${entry['_source']['log']}`;
      const result = elasticSearchUtils.parseLogEntry(entry);
      expect(result).to.deep.equal(expectedResult);
    });

  });

  describe('makeSearch', function () {
    it('should return error if cannot decode token', function () {
      elasticSearchUtils.__set__('elasticsearch.Client', elasticsearchClientMock);
      deferred.resolve();
      return elasticSearchUtils.makeSearch(runName, namespace, lines)
        .then(function (data) {
          expect(elasticsearchClientMock.calledOnce).to.equal(true);
          expect(data.hasOwnProperty('data')).to.equal(true);
          expect(data.hasOwnProperty('client')).to.equal(true);
        });
    });
  });

  describe('getRunLastLogs', function () {
    beforeEach(function () {
      deferred = Q.defer();
    });

    it('should return error if cannot get logs from elasticsearch', function () {
      const makeSearchMock = sinon.stub().returns(deferred.promise);
      elasticSearchUtils.__set__('makeSearch', makeSearchMock);
      deferred.reject(error);
      return elasticSearchUtils.getRunLastLogs(null, runName, namespace, lines)
        .catch(function (err) {
          expect(err).to.deep.equal(error)
        });
    });

    it('should return default string if not data', function () {
      const makeSearchMock = sinon.stub().returns(deferred.promise);
      elasticSearchUtils.__set__('makeSearch', makeSearchMock);
      delete data.hits;
      deferred.resolve(data);
      return elasticSearchUtils.getRunLastLogs(null, runName, namespace, lines)
        .then(function (data) {
          expect(data).to.equal('No data');
        });
    });

    it('should return logs data if logs entries retrieved', function () {
      const expectedResult = data.hits.hits.map(
        (entry) => `${entry['_source']['@timestamp']} ${entry['_source']['kubernetes']['pod_name']} ${entry['_source']['log']}`).join('');
      const makeSearchMock = sinon.stub().returns(deferred.promise);
      elasticSearchUtils.__set__('makeSearch', makeSearchMock);
      deferred.resolve({data: data});
      return elasticSearchUtils.getRunLastLogs(null, runName, namespace, lines)
        .then(function (data) {
          expect(data).to.equal(expectedResult);
        });
    });
  });
});
