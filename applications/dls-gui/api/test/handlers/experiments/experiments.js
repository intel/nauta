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
const k8sUtils = require('../../../src/utils/k8s');
const HttpStatus = require('http-status-codes');

describe('Handlers | Experiments', function () {

  let resMock, reqMock, k8sMock, podsList, k8sRunEntities, k8sRunsResponse, generatedEntities, error, deferred;

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
    k8sRunEntities = [
      {
        metadata: {
          creationTimestamp: '2018-06-11T07:35:06Z',
          name: 'exp-mnist-sing-18-06-11-09-34-45-41',
          namespace: 'andrzej',
          labels: {
            runKind: 'training'
          }
        },
        spec: {
          'start-time': '2018-08-22T06:52:46Z',
          'end-time': '2018-08-22T06:52:49Z',
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
          labels: {
            runKind: 'inference'
          }
        },
        spec: {
          'start-time': null,
          'end-time': null,
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
          state: 'QUEUED'
        }
      }
    ];
    k8sRunsResponse = {
      items: k8sRunEntities
    };
    generatedEntities = [
      {
        attributes: {
          creationTimestamp: k8sRunEntities[0].metadata.creationTimestamp,
          name: k8sRunEntities[0].metadata.name,
          namespace: k8sRunEntities[0].metadata.namespace,
          state: k8sRunEntities[0].spec.state,
          type: k8sRunEntities[0].metadata.labels.runKind,
          accuracy: k8sRunEntities[0].spec.metrics['accuracy']
        },
        params: {
          podSelector: k8sRunEntities[0].spec['pod-selector']['matchLabels'],
          podCount: k8sRunEntities[0].spec['pod-count'],
          parameters: k8sRunEntities[0].spec['parameters'],
          trainingStartTime: k8sRunEntities[0].spec['start-time'],
          trainingEndTime: k8sRunEntities[0].spec['end-time']
        }
      },
      {
        attributes: {
          creationTimestamp: k8sRunEntities[1].metadata.creationTimestamp,
          name: k8sRunEntities[1].metadata.name,
          namespace: k8sRunEntities[1].metadata.namespace,
          state: k8sRunEntities[1].spec.state,
          type: k8sRunEntities[1].metadata.labels.runKind,
          accuracy: k8sRunEntities[1].spec.metrics['accuracy']
        },
        params: {
          podSelector: k8sRunEntities[1].spec['pod-selector']['matchLabels'],
          podCount: k8sRunEntities[1].spec['pod-count'],
          parameters: k8sRunEntities[1].spec['parameters'],
          trainingStartTime: k8sRunEntities[1].spec['start-time'],
          trainingEndTime: k8sRunEntities[1].spec['end-time']
        }
      }
    ];
    podsList = {
      items: [
        {
          metadata: {
            name: 'name1'
          },
          status: {
            containerStatuses: [
              {
                name: 'tensorflow',
                state: {
                  terminated: {
                    containerID: 'docker://7e5515bc9f04fe4601e1dbea1d35852ec3af80434e6b040f42a22f0923d1773a',
                    exitCode: 0,
                    finishedAt: '2018-08-24T06:42:10Z',
                    reason: 'Completed',
                    startedAt: '2018-08-24T06:42:08Z'
                  }
                }
              }
            ],
            conditions: [
              {
                lastProbeTime: null,
                lastTransitionTime: '2018-08-24T06:42:07Z',
                reason: 'PodCompleted',
                status: 'True',
                type: 'Initialized'
              },
              {
                lastProbeTime: null,
                lastTransitionTime: '2018-08-24T06:42:10Z',
                reason: 'PodCompleted',
                status: 'False',
                type: 'Ready'
              },
              {
                lastProbeTime: null,
                lastTransitionTime: '2018-08-24T06:42:00Z',
                status: 'True',
                type: 'PodScheduled'
              }
            ],
            phase: 'succeed'
          },
          spec: {
            containers: [
              {
                name: 'tensorflow',
                resources: {},
                state: {
                  terminated: {
                    reason: 'Completed',
                  }
                }
              }
            ]
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
        listClusterCustomObject: sinon.stub().returns(deferred.promise)
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
        expect(k8sMock.listClusterCustomObject.calledOnce).to.equal(true);
        done();
      });
    });

    it('should return data with parsing', function (done) {
      const parseExpMock = sinon.stub().returns(k8sRunsResponse.items);
      expApi.__set__('k8s', k8sMock);
      expApi.__set__('parseExperiments', parseExpMock);
      expApi.getUserExperiments(reqMock, resMock);
      deferred.resolve(k8sRunsResponse);
      process.nextTick(function () {
        expect(resMock.send.calledOnce).to.equal(true);
        expect(resMock.send.calledWith(k8sRunsResponse.items)).to.equal(true);
        expect(k8sMock.listClusterCustomObject.calledOnce).to.equal(true);
        expect(parseExpMock.calledOnce).to.equal(true);
        done();
      });
    });

  });

  describe('generateExperimentEntities', function () {
    it('should return empty array if not data', function () {
      const result = expApi.generateExperimentEntities();
      expect(result).to.deep.equal([]);
    });

    it('should return generated entities if data provided', function () {
      const expectedResult = generatedEntities;
      const result = expApi.generateExperimentEntities(k8sRunEntities);
      expect(result).to.deep.equal(expectedResult);
    });

    it('should return generated entities if data without metrics provided', function () {
      delete k8sRunEntities[0].spec.metrics;
      delete generatedEntities[0].attributes.accuracy;
      const expectedResult = generatedEntities;
      const result = expApi.generateExperimentEntities(k8sRunEntities);
      expect(result).to.deep.equal(expectedResult);
    });
  });

  describe('extractValuesForFilterableAttrs', function () {
    it('should return correct object if not data', function () {
      const expectedResult = {
        name: [],
        namespace: [],
        state: [],
        type: []
      };
      const result = expApi.extractValuesForFilterableAttrs([]);
      expect(result).to.deep.equal(expectedResult);
    });

    it('should return correct object if data provided', function () {
      const expectedResult = {
        name: [generatedEntities[0].attributes.name, generatedEntities[1].attributes.name],
        namespace: [generatedEntities[0].attributes.namespace],
        state: [generatedEntities[0].attributes.state, generatedEntities[1].attributes.state],
        type: [generatedEntities[0].attributes.type, generatedEntities[1].attributes.type]
      };
      const result = expApi.extractValuesForFilterableAttrs(generatedEntities);
      expect(result).to.deep.equal(expectedResult);
    });
  });

  describe('applyQueryFilters', function () {
    it('should return throw exception if no array object', function () {
      try {
        expApi.applyQueryFilters();
      } catch (err) {
        expect(err).to.equal('Incorrect Array Data');
      }
    });

    it('should return correct object if empty array provided', function () {
      const expectedResult = {
        data: [],
        queryParams: {
          name: [],
          namespace: [],
          state: [],
          type: [],
          searchPattern: ''
        }
      };
      const result = expApi.applyQueryFilters([]);
      expect(result).to.deep.equal(expectedResult);
    });

    it('should return not filtered data if empty query', function () {
      const expectedResult = {
        data: generatedEntities,
        queryParams: {
          name: [generatedEntities[0].attributes.name, generatedEntities[1].attributes.name],
          namespace: [generatedEntities[0].attributes.namespace],
          state: [generatedEntities[0].attributes.state, generatedEntities[1].attributes.state],
          type: [generatedEntities[0].attributes.type, generatedEntities[1].attributes.type],
          searchPattern: ''
        }
      };
      const result = expApi.applyQueryFilters(generatedEntities);
      expect(result).to.deep.equal(expectedResult);
    });

    it('should return filtered data if query by name provided', function () {
      const expectedResult = {
        data: [generatedEntities[0]],
        queryParams: {
          name: [generatedEntities[0].attributes.name],
          namespace: [generatedEntities[0].attributes.namespace],
          state: [generatedEntities[0].attributes.state, generatedEntities[1].attributes.state],
          type: [generatedEntities[0].attributes.type, generatedEntities[1].attributes.type],
          searchPattern: ''
        }
      };
      const queryParams = {name: [generatedEntities[0].attributes.name]};
      const result = expApi.applyQueryFilters(generatedEntities, queryParams);
      expect(result).to.deep.equal(expectedResult);
    });

    it('should return filtered data if query by name with wildcard provided', function () {
      const expectedResult = {
        data: generatedEntities,
        queryParams: {
          name: [generatedEntities[0].attributes.name, generatedEntities[1].attributes.name],
          namespace: [generatedEntities[0].attributes.namespace],
          state: [generatedEntities[0].attributes.state, generatedEntities[1].attributes.state],
          type: [generatedEntities[0].attributes.type, generatedEntities[1].attributes.type],
          searchPattern: ''
        }
      };
      const queryParams = {name: '*'};
      const result = expApi.applyQueryFilters(generatedEntities, queryParams);
      expect(result).to.deep.equal(expectedResult);
    });

    it('should return filtered data if search pattern provided', function () {
      const expectedResult = {
        data: [generatedEntities[0]],
        queryParams: {
          name: [generatedEntities[0].attributes.name, generatedEntities[1].attributes.name],
          namespace: [generatedEntities[0].attributes.namespace],
          state: [generatedEntities[0].attributes.state, generatedEntities[1].attributes.state],
          type: [generatedEntities[0].attributes.type, generatedEntities[1].attributes.type],
          searchPattern: 'MNIST-SING-18-06-11-09-34-45-41'
        }
      };
      const searchPattern = 'mnist-SING-18-06-11-09-34-45-41';
      const result = expApi.applyQueryFilters(generatedEntities, null, searchPattern);
      expect(result).to.deep.equal(expectedResult);
    });
  });

  describe('applyOrderParams', function () {
    it('should throw exception if no array object', function () {
      try {
        expApi.applyOrderParams();
      } catch (err) {
        expect(err).to.equal('Incorrect Array Data');
      }
    });

    it('should return sorted data if sorting params provided', function () {
      const expectedResult = {
        data: [generatedEntities[1], generatedEntities[0]],
        a: 1,
        b: 2,
        totalPagesCount: 1,
        pageNumber: 1
      };
      const result = expApi.applyOrderParams(generatedEntities, 'name', 'desc');
      expect(result).to.deep.equal(expectedResult);
    });

    it('should return second page of data if pagination params provided', function () {
      const limitPerPage = 1;
      const pageNo = 2;
      const expectedResult = {
        data: [generatedEntities[1]],
        a: 2,
        b: 2,
        totalPagesCount: 2,
        pageNumber: 2
      };
      const result = expApi.applyOrderParams(generatedEntities, null, null, limitPerPage, pageNo);
      expect(result).to.deep.equal(expectedResult);
    });

    it('should return all data if pagination limit bigger than count of items', function () {
      const limitPerPage = 10;
      const pageNo = 1;
      const expectedResult = {
        data: [generatedEntities[0], generatedEntities[1]],
        a: 1,
        b: 2,
        totalPagesCount: 1,
        pageNumber: 1
      };
      const result = expApi.applyOrderParams(generatedEntities, null, null, limitPerPage, pageNo);
      expect(result).to.deep.equal(expectedResult);
    });
  });

  describe('extractAttrsNames', function () {
    it('should return throw exception if no array object', function () {
      try {
        expApi.extractAttrsNames();
      } catch (err) {
        expect(err).to.equal('Incorrect Array Data');
      }
    });

    it('should return all params', function () {
      const expectedResult = ['creationTimestamp', 'name', 'namespace', 'state', 'type', 'accuracy'];
      const result = expApi.extractAttrsNames(generatedEntities);
      expect(result).to.deep.equal(expectedResult);
    });
  });

  describe('parseExperiments', function () {
    let generateExperimentEntitiesMock, extractValuesForFilterableAttrsMock, applyQueryFiltersMock,
      applyOrderParamsMock, extractAttrsNamesMock;
    beforeEach(function () {
      generateExperimentEntitiesMock = sinon.stub().returns(generatedEntities);
      extractValuesForFilterableAttrsMock = sinon.stub().returns({
        name: [generatedEntities[0].attributes.name, generatedEntities[1].attributes.name],
        namespace: [generatedEntities[0].attributes.namespace],
        state: [generatedEntities[0].attributes.state, generatedEntities[1].attributes.state]
      });
      applyQueryFiltersMock = sinon.stub().returns({
        data: generatedEntities,
        queryParams: {
          name: [generatedEntities[0].attributes.name, generatedEntities[1].attributes.name],
          namespace: [generatedEntities[0].attributes.namespace],
          state: [generatedEntities[0].attributes.state, generatedEntities[1].attributes.state],
          searchPattern: ''
        }
      });
      applyOrderParamsMock = sinon.stub().returns({
        data: generatedEntities,
        a: 1,
        b: 2,
        totalPagesCount: 1,
        pageNumber: 1
      });
      extractAttrsNamesMock = sinon.stub().returns(['creationTimestamp', 'name', 'namespace',
        'podSelector', 'podCount', 'state', 'parameters', 'accuracy']);
      Date.now = sinon.stub().returns(1);
    });

    it('should return correct data if no experiments provided', function () {
      const queryParams = {};
      expApi.__set__('generateExperimentEntities', generateExperimentEntitiesMock);
      expApi.__set__('extractValuesForFilterableAttrs', extractValuesForFilterableAttrsMock);
      expApi.__set__('applyQueryFilters', applyQueryFiltersMock);
      expApi.__set__('applyOrderParams', applyOrderParamsMock);
      expApi.__set__('extractAttrsNames', extractAttrsNamesMock);
      const expectedResult = {
        stats: {
          total: 2,
          datetime: 1,
          filteredDataCount: 2,
          a: 1,
          b: 2,
          totalPagesCount: 1,
          pageNumber: 1
        },
        filterColumnValues: {
          options: {
            name: [generatedEntities[0].attributes.name, generatedEntities[1].attributes.name],
            namespace: [generatedEntities[0].attributes.namespace],
            state: [generatedEntities[0].attributes.state, generatedEntities[1].attributes.state]
          },
          current: {
            name: [generatedEntities[0].attributes.name, generatedEntities[1].attributes.name],
            namespace: [generatedEntities[0].attributes.namespace],
            state: [generatedEntities[0].attributes.state, generatedEntities[1].attributes.state],
            searchPattern: ''
          }
        },
        params: ['creationTimestamp', 'name', 'namespace', 'podSelector', 'podCount', 'state', 'parameters', 'accuracy'],
        data: generatedEntities
      };
      const result = expApi.parseExperiments(k8sRunEntities, queryParams);
      expect(result).to.deep.equal(expectedResult);
      expect(generateExperimentEntitiesMock.calledOnce).to.equal(true);
      expect(extractValuesForFilterableAttrsMock.calledOnce).to.equal(true);
      expect(applyQueryFiltersMock.calledOnce).to.equal(true);
      expect(applyOrderParamsMock.calledOnce).to.equal(true);
      expect(extractAttrsNamesMock.calledOnce).to.equal(true);
    });
  });

  describe('getExperimentResourcesData', function () {
    beforeEach(function () {
      deferred = Q.defer();
      k8sMock = {
        listPodsByLabelValue: sinon.stub().returns(deferred.promise),
        parseContainerState: k8sUtils.parseContainerState
      };
      reqMock.params = {
        experiment: 'exp'
      }
    });

    it('should return error if invalid request headers', function () {
      delete reqMock.headers.authorization;
      expApi.getExperimentResourcesData(reqMock, resMock);
      expect(resMock.status.calledOnce).to.equal(true);
      expect(resMock.status.calledWith(HttpStatus.UNAUTHORIZED)).to.equal(true);
    });

    it('should return error if missing exp name in params', function () {
      delete reqMock.params.experiment;
      expApi.getExperimentResourcesData(reqMock, resMock);
      expect(resMock.status.calledOnce).to.equal(true);
      expect(resMock.status.calledWith(HttpStatus.BAD_REQUEST)).to.equal(true);
    });

    it('should return error if cannot fetch pods', function (done) {
      expApi.__set__('k8s', k8sMock);
      expApi.getExperimentResourcesData(reqMock, resMock);
      deferred.reject(error);
      process.nextTick(function () {
        expect(resMock.status.calledOnce).to.equal(true);
        expect(resMock.status.calledWith(error.status)).to.equal(true);
        expect(k8sMock.listPodsByLabelValue.calledOnce).to.equal(true);
        done();
      });
    });

    it('should return data if everything ok', function (done) {
      const expectedResult = [{
        name: 'name1',
        state: ['Initialized: True , reason: PodCompleted', 'Ready: False , reason: PodCompleted', 'PodScheduled: True '],
        containers: [
          {
            name: 'tensorflow',
            resources: {},
            status: 'Terminated, "Completed"'
          }
        ]
      }];
      expApi.__set__('k8s', k8sMock);
      expApi.getExperimentResourcesData(reqMock, resMock);
      deferred.resolve(podsList);
      process.nextTick(function () {
        expect(resMock.send.calledOnce).to.equal(true);
        expect(resMock.send.calledWith(expectedResult)).to.equal(true);
        expect(k8sMock.listPodsByLabelValue.calledOnce).to.equal(true);
        done();
      });
    });

  });
});
