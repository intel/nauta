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
      items: [
        {
          metadata: {
            creationTimestamp: '2018-06-11T07:35:06Z',
            name: 'exp-mnist-sing-18-06-11-09-34-45-41',
            namespace: 'andrzej',
          },
          spec: {
            'experiment-name': 'experiment-name-will-be-added-soon',
            metrics: {
              accuracy: '52.322'
            },
            parameters: [
              'mnist_single_node.py'
            ],
            'pod-count': 1,
            'pod-selector': {
              matchLabels: {
                app: 'tf-training-tfjob',
                draft: 'exp-mnist-sing-18-06-11-09-34-45-41',
                release: 'exp-mnist-sing-18-06-11-09-34-45-41'
              }
            },
            state: 'FAILED'
          }
        }
      ]
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

    it('should return data with parsing', function (done) {
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
    beforeEach(function () {
      data = [
        {
          metadata: {
            creationTimestamp: '2018-06-11T07:35:06Z',
            name: 'exp-mnist-sing-18-06-11-09-34-45-41',
            namespace: 'andrzej',
          },
          spec: {
            'experiment-name': 'experiment-name-will-be-added-soon',
            metrics: {
              accuracy: '52.322'
            },
            parameters: [
              'mnist_single_node.py'
            ],
            'pod-count': 1,
            'pod-selector': {
              matchLabels: {
                app: 'tf-training-tfjob',
                draft: 'exp-mnist-sing-18-06-11-09-34-45-41',
                release: 'exp-mnist-sing-18-06-11-09-34-45-41'
              }
            },
            state: 'FAILED'
          }
        },
        {
          metadata: {
            creationTimestamp: '2018-06-11T07:35:06Z',
            name: 'exp-mnist-sing-18-06-11-09-34-45-42',
            namespace: 'andrzej',
          },
          spec: {
            'experiment-name': 'experiment-name-will-be-added-soon',
            metrics: {
              accuracy: '52.322'
            },
            parameters: [
              'mnist_single_node.py'
            ],
            'pod-count': 1,
            'pod-selector': {
              matchLabels: {
                app: 'tf-training-tfjob',
                draft: 'exp-mnist-sing-18-06-11-09-34-45-41',
                release: 'exp-mnist-sing-18-06-11-09-34-45-41'
              }
            },
            state: 'FAILED'
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
            creationTimestamp: data[0].metadata.creationTimestamp,
            name: data[0].metadata.name,
            namespace: data[0].metadata.namespace,
            podSelector: data[0].spec['pod-selector']['matchLabels'],
            podCount: data[0].spec['pod-count'],
            state: data[0].spec['state'],
            parameters: data[0].spec['parameters'],
            accuracy: data[0].spec['metrics']['accuracy']
          },
          {
            creationTimestamp: data[1].metadata.creationTimestamp,
            name: data[1].metadata.name,
            namespace: data[1].metadata.namespace,
            podSelector: data[1].spec['pod-selector']['matchLabels'],
            podCount: data[1].spec['pod-count'],
            state: data[1].spec['state'],
            parameters: data[1].spec['parameters'],
            accuracy: data[1].spec['metrics']['accuracy']
          }
        ],
        stats: {
          total: 2,
          datetime: 1
        },
        params: ['creationTimestamp', 'name', 'namespace', 'podSelector', 'podCount', 'state', 'parameters', 'accuracy']
      };
      const result = expApi.parseExperiments(data);
      expect(result.data).to.deep.equal(expectedResult.data);
      expect(result.stats).to.deep.equal(expectedResult.stats);
      expect(result.params).to.deep.equal(expectedResult.params);
    });

    it('should return correct data if search pattern provided', function () {
      const query = {searchBy: '09-34-45-41'};
      const expectedResult = {
        data: [
          {
            creationTimestamp: data[0].metadata.creationTimestamp,
            name: data[0].metadata.name,
            namespace: data[0].metadata.namespace,
            podSelector: data[0].spec['pod-selector']['matchLabels'],
            podCount: data[0].spec['pod-count'],
            state: data[0].spec['state'],
            parameters: data[0].spec['parameters'],
            accuracy: data[0].spec['metrics']['accuracy']
          }
        ],
        stats: {
          total: 1,
          datetime: 1
        },
        params: ['creationTimestamp', 'name', 'namespace', 'podSelector', 'podCount', 'state', 'parameters', 'accuracy']
      };
      const result = expApi.parseExperiments(data, query);
      expect(result.data).to.deep.equal(expectedResult.data);
      expect(result.stats).to.deep.equal(expectedResult.stats);
      expect(result.params).to.deep.equal(expectedResult.params);
    });

    it('should return correct data if order params provided', function () {
      const query = {order: 'desc', orderBy: 'name'};
      const expectedResult = {
        data: [
          {
            creationTimestamp: data[1].metadata.creationTimestamp,
            name: data[1].metadata.name,
            namespace: data[1].metadata.namespace,
            podSelector: data[1].spec['pod-selector']['matchLabels'],
            podCount: data[1].spec['pod-count'],
            state: data[1].spec['state'],
            parameters: data[1].spec['parameters'],
            accuracy: data[1].spec['metrics']['accuracy']
          },
          {
            creationTimestamp: data[0].metadata.creationTimestamp,
            name: data[0].metadata.name,
            namespace: data[0].metadata.namespace,
            podSelector: data[0].spec['pod-selector']['matchLabels'],
            podCount: data[0].spec['pod-count'],
            state: data[0].spec['state'],
            parameters: data[0].spec['parameters'],
            accuracy: data[0].spec['metrics']['accuracy']
          }
        ],
        stats: {
          total: 2,
          datetime: 1
        },
        params: ['creationTimestamp', 'name', 'namespace', 'podSelector', 'podCount', 'state', 'parameters', 'accuracy']
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
            creationTimestamp: data[1].metadata.creationTimestamp,
            name: data[1].metadata.name,
            namespace: data[1].metadata.namespace,
            podSelector: data[1].spec['pod-selector']['matchLabels'],
            podCount: data[1].spec['pod-count'],
            state: data[1].spec['state'],
            parameters: data[1].spec['parameters'],
            accuracy: data[1].spec['metrics']['accuracy']
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
        params: ['creationTimestamp', 'name', 'namespace', 'podSelector', 'podCount', 'state', 'parameters', 'accuracy']
      };
      const result = expApi.parseExperiments(data, query);
      expect(result.data).to.deep.equal(expectedResult.data);
      expect(result.stats).to.deep.equal(expectedResult.stats);
      expect(result.params).to.deep.equal(expectedResult.params);
    });

  });
});
