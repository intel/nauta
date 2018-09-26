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

const expect = require('chai').expect;
const sinon = require('sinon');
const rewire = require('rewire');
const Q = require('q');
const elasticSearchUtils = rewire('../../src/utils/dls4e-elasticsearch');
const HttpStatus = require('http-status-codes');
const errMessages = require('../../src/utils/error-messages');

describe('Utils | dls4e-elasticsearch', function () {

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
