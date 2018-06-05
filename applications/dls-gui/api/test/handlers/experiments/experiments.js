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
const expApi = rewire('../../../src/handlers/experiments/experiments');
const HttpStatus = require('http-status-codes');

describe('Handlers | Experiments', function () {

  let resMock, reqMock, k8sMock, data, error, deferred;

  beforeEach(function () {
    resMock = {
      status: sinon.stub().returns({
        send: sinon.spy()
      }),
      send: sinon.spy()
    };
    reqMock = {
      headers: {
        authorization: 'token'
      }
    };
    k8sMock = {
      listNamespacedCustomObject: sinon.spy()
    };
    data = {
      items: [{name: 'exp1'}]
    };
    error = {
      status: 500,
      message: 'error'
    };
  });

  describe('getUserExperiments', function () {
    beforeEach(function () {
      deferred = Q.defer();
      k8sMock = {
        listNamespacedCustomObject: sinon.stub().returns(deferred.promise)
      };
    });

    it('should return error if invalid request headers', function () {
      delete reqMock.headers.authorization;
      expApi.getUserExperiments(reqMock, resMock);
      expect(resMock.status.calledOnce).to.equal(true);
      expect(resMock.status.calledWith(HttpStatus.UNAUTHORIZED)).to.equal(true);
    });

    it('should return error if cannot fetch namespaced custom object', function (done) {
      expApi.__set__('k8s', k8sMock);
      expApi.getUserExperiments(reqMock, resMock);
      deferred.reject(error);
      process.nextTick(function () {
        expect(resMock.status.calledOnce).to.equal(true);
        expect(resMock.status.calledWith(error.status)).to.equal(true);
        expect(k8sMock.listNamespacedCustomObject.calledOnce).to.equal(true);
        done();
      });
    });

    it('should return empty array without parsing if no data', function (done) {
      data.items = [];
      const parseExpMock = sinon.spy();
      expApi.__set__('k8s', k8sMock);
      expApi.__set__('parseExperiments', parseExpMock);
      expApi.getUserExperiments(reqMock, resMock);
      deferred.resolve(data);
      process.nextTick(function () {
        expect(resMock.send.calledOnce).to.equal(true);
        expect(resMock.send.calledWith(data.items)).to.equal(true);
        expect(k8sMock.listNamespacedCustomObject.calledOnce).to.equal(true);
        expect(parseExpMock.called).to.equal(false);
        done();
      });
    });

    it('should return empty array without parsing if no data', function (done) {
      const parseExpMock = sinon.stub().returns(data.items);
      expApi.__set__('k8s', k8sMock);
      expApi.__set__('parseExperiments', parseExpMock);
      expApi.getUserExperiments(reqMock, resMock);
      deferred.resolve(data);
      process.nextTick(function () {
        expect(resMock.send.calledOnce).to.equal(true);
        expect(resMock.send.calledWith(data.items)).to.equal(true);
        expect(k8sMock.listNamespacedCustomObject.calledOnce).to.equal(true);
        expect(parseExpMock.calledOnce).to.equal(true);
        done();
      });
    });

  });

  describe('parseExperiments', function () {
    let dateMock;
    beforeEach(function () {
      data = [
        {
          metadata: {
            creationTimestamp: '2018-05-23T11:50:27Z',
            namespace: 'test'
          },
          spec: {
            name: 'name1',
            param1: 'param1',
            param2: 'param2',
            param3: 0
          }
        },
        {
          metadata: {
            creationTimestamp: '2011-05-23T11:51:27Z',
            namespace: 'test'
          },
          spec: {
            name: 'name2',
            param1: 'param1',
            param2: 'param2',
            param3: 1
          }
        }
      ];
      Date.now = sinon.stub().returns(1);
    });

    it('should return correct data if no experiments provided', function () {
      const expectedResult = {
        data: [],
        stats: {
          total: 0,
          datetime: 1
        },
        params: []
      };
      const result = expApi.parseExperiments([]);
      expect(result.data).to.deep.equal(expectedResult.data);
      expect(result.stats).to.deep.equal(expectedResult.stats);
      expect(result.params).to.deep.equal(expectedResult.params);
    });

    it('should return correct data if no experiments provided', function () {
      const expectedResult = {
        data: [
          {
            creationTimestamp: 'Wed, 23 May 2018 11:50:27 GMT',
            namespace: 'test',
            name: 'name1',
            param1: 'param1',
            param2: 'param2',
            param3: 0
          },
          {
            creationTimestamp: 'Mon, 23 May 2011 11:51:27 GMT',
            namespace: 'test',
            name: 'name2',
            param1: 'param1',
            param2: 'param2',
            param3: 1
          }
        ],
        stats: {
          total: 2,
          datetime: 1
        },
        params: ['creationTimestamp', 'namespace', 'name', 'param1', 'param2', 'param3']
      };
      const result = expApi.parseExperiments(data);
      expect(result.data).to.deep.equal(expectedResult.data);
      expect(result.stats).to.deep.equal(expectedResult.stats);
      expect(result.params).to.deep.equal(expectedResult.params);
    });

    it('should return correct data if search pattern provided', function () {
      const query = {searchBy: 'name1'};
      const expectedResult = {
        data: [
          {
            creationTimestamp: 'Wed, 23 May 2018 11:50:27 GMT',
            namespace: 'test',
            name: 'name1',
            param1: 'param1',
            param2: 'param2',
            param3: 0
          }
        ],
        stats: {
          total: 1,
          datetime: 1
        },
        params: ['creationTimestamp', 'namespace', 'name', 'param1', 'param2', 'param3']
      };
      const result = expApi.parseExperiments(data, query);
      expect(result.data).to.deep.equal(expectedResult.data);
      expect(result.stats).to.deep.equal(expectedResult.stats);
      expect(result.params).to.deep.equal(expectedResult.params);
    });

    it('should return correct data if order params provided', function () {
      const query = {order: 'desc', orderBy: 'param3'};
      const expectedResult = {
        data: [
          {
            creationTimestamp: 'Mon, 23 May 2011 11:51:27 GMT',
            namespace: 'test',
            name: 'name2',
            param1: 'param1',
            param2: 'param2',
            param3: 1
          },
          {
            creationTimestamp: 'Wed, 23 May 2018 11:50:27 GMT',
            namespace: 'test',
            name: 'name1',
            param1: 'param1',
            param2: 'param2',
            param3: 0
          }
        ],
        stats: {
          total: 2,
          datetime: 1
        },
        params: ['creationTimestamp', 'namespace', 'name', 'param1', 'param2', 'param3']
      };
      const result = expApi.parseExperiments(data, query);
      expect(result.data).to.deep.equal(expectedResult.data);
      expect(result.stats).to.deep.equal(expectedResult.stats);
      expect(result.params).to.deep.equal(expectedResult.params);
    });

    it('should return correct data if pagination params provided', function () {
      const query = {limit: 1, page: 2};
      const expectedResult = {
        data: [
          {
            creationTimestamp: 'Mon, 23 May 2011 11:51:27 GMT',
            namespace: 'test',
            name: 'name2',
            param1: 'param1',
            param2: 'param2',
            param3: 1
          }
        ],
        stats: {
          total: 2,
          a: 2,
          b: 2,
          pageNumber: 2,
          totalPagesCount: 2,
          datetime: 1
        },
        params: ['creationTimestamp', 'namespace', 'name', 'param1', 'param2', 'param3']
      };
      const result = expApi.parseExperiments(data, query);
      expect(result.data).to.deep.equal(expectedResult.data);
      expect(result.stats).to.deep.equal(expectedResult.stats);
      expect(result.params).to.deep.equal(expectedResult.params);
    });

  });
});
