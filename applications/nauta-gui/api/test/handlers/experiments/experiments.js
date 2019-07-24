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
const expApi = rewire('../../../src/handlers/experiments/experiments');
const k8sUtils = require('../../../src/utils/k8s');
const datetimeUtils = require('../../../src/utils/datetime-utils');
const HttpStatus = require('http-status-codes');

describe('Handlers | Experiments', function () {

  let resMock, reqMock, k8sMock, podsList, k8sRunEntities, k8sExpsEntities, k8sRunsResponse, generatedEntities, error,
    deferred, currentTime, clock, elasticsearchUtilsMock;

  beforeEach(function () {
    currentTime = '2018-06-11T011:35:06Z';
    clock = sinon.useFakeTimers(new Date(currentTime).getTime());
    resMock = {
      status: sinon.stub().returns({
        send: sinon.spy()
      }),
      send: sinon.spy(),
      writeHead: sinon.spy(),
      write: sinon.spy(),
      end: sinon.spy()
    };
    reqMock = {
      headers: {
        authorization: 'token',
        'timezone-offset': new Date().getTimezoneOffset()
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
    k8sExpsEntities = [
      {
        metadata: {
          creationTimestamp: '2018-06-11T07:35:06Z',
          name: 'exp-mnist-sing-18-06-11-09-34-45-41',
          namespace: 'andrzej',
          clusterName: '',
          generation: 1,
          labels: {
            'runKind': 'training'
          }
        },
        spec: {
          'template-name': 'tf-training-tfjob',
          'template-namespace': 'template-namespace',
          'template-version': '0.1.0'
        }
      },
      {
        metadata: {
          creationTimestamp: '2018-06-11T07:35:06Z',
          name: 'exp-mnist-sing-18-06-11-09-34-45-42',
          namespace: 'andrzej',
          clusterName: '',
          generation: 1,
          labels: {
            'runKind': 'training'
          }
        },
        spec: {
          'template-name': 'tf-training-tfjob',
          'template-namespace': 'template-namespace',
          'template-version': '0.1.0'
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
          accuracy: k8sRunEntities[0].spec.metrics['accuracy'],
          podSelector: k8sRunEntities[0].spec['pod-selector']['matchLabels'],
          podCount: k8sRunEntities[0].spec['pod-count'],
          parameters: k8sRunEntities[0].spec['parameters'],
          trainingStartTime: k8sRunEntities[0].spec['start-time'],
          trainingEndTime: k8sRunEntities[0].spec['end-time'],
          trainingDurationTime: datetimeUtils.calculateTimeDifferenceFromDateString(
            k8sRunEntities[0].spec['start-time'], k8sRunEntities[0].spec['end-time']),
          trainingTimeInQueue: datetimeUtils.calculateTimeDifferenceFromDateString(
            k8sRunEntities[0].metadata.creationTimestamp, k8sRunEntities[0].spec['start-time']),
          'template-name': k8sExpsEntities[0].spec['template-name'],
          'template-namespace': k8sExpsEntities[0].spec['template-namespace'],
          'template-version': k8sExpsEntities[0].spec['template-version']
        }
      },
      {
        attributes: {
          creationTimestamp: k8sRunEntities[1].metadata.creationTimestamp,
          name: k8sRunEntities[1].metadata.name,
          namespace: k8sRunEntities[1].metadata.namespace,
          state: k8sRunEntities[1].spec.state,
          type: k8sRunEntities[1].metadata.labels.runKind,
          accuracy: k8sRunEntities[1].spec.metrics['accuracy'],
          podSelector: k8sRunEntities[1].spec['pod-selector']['matchLabels'],
          podCount: k8sRunEntities[1].spec['pod-count'],
          parameters: k8sRunEntities[1].spec['parameters'],
          trainingStartTime: k8sRunEntities[1].spec['start-time'],
          trainingEndTime: k8sRunEntities[1].spec['end-time'],
          trainingDurationTime: datetimeUtils.calculateTimeDifferenceFromDateString(
            k8sRunEntities[1].spec['start-time'], k8sRunEntities[1].spec['end-time']),
          trainingTimeInQueue: datetimeUtils.calculateTimeDifferenceFromDateString(
            k8sRunEntities[1].metadata.creationTimestamp, k8sRunEntities[1].spec['start-time']),
          'template-name': k8sExpsEntities[1].spec['template-name'],
          'template-namespace': k8sExpsEntities[1].spec['template-namespace'],
          'template-version': k8sExpsEntities[1].spec['template-version']
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

  afterEach(function () {
    clock.restore();
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
        expect(k8sMock.listClusterCustomObject.calledTwice).to.equal(true);
        expect(parseExpMock.calledOnce).to.equal(true);
        done();
      });
    });

  });

  describe('prepareDataUsingFilters', function () {
    it('should return throw exception if no array object', function () {
      try {
        expApi.prepareDataUsingFilters();
      } catch (err) {
        expect(err).to.equal('Incorrect Array Data');
      }
    });

    it('should return correct valuesForFilterableAttrs object if data provided', function () {
      const expectedResult = {
        name: [generatedEntities[0].attributes.name, generatedEntities[1].attributes.name],
        namespace: [generatedEntities[0].attributes.namespace],
        state: [generatedEntities[0].attributes.state, generatedEntities[1].attributes.state],
        type: [generatedEntities[0].attributes.type, generatedEntities[1].attributes.type]
      };
      const result = expApi.prepareDataUsingFilters(generatedEntities);
      expect(result.valuesForFilterableAttrs).to.deep.equal(expectedResult);
    });

    it('should return correct object if empty array provided', function () {
      const expectedResult = {
        data: [],
        queryParams: {
          name: [],
          namespace: [],
          state: [],
          type: [],
          searchPattern: '',
          searchTimezone: reqMock.headers['timezone-offset']
        },
        valuesForFilterableAttrs: {
          name: [],
          namespace: [],
          state: [],
          type: []
        }
      };
      const result = expApi.prepareDataUsingFilters([]);
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
          searchPattern: '',
          searchTimezone: reqMock.headers['timezone-offset']
        },
        valuesForFilterableAttrs: {
          name: [generatedEntities[0].attributes.name, generatedEntities[1].attributes.name],
          namespace: [generatedEntities[0].attributes.namespace],
          state: [generatedEntities[0].attributes.state, generatedEntities[1].attributes.state],
          type: [generatedEntities[0].attributes.type, generatedEntities[1].attributes.type]
        }
      };
      const result = expApi.prepareDataUsingFilters(generatedEntities);
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
          searchPattern: '',
          searchTimezone: reqMock.headers['timezone-offset']
        },
        valuesForFilterableAttrs: {
          name: [generatedEntities[0].attributes.name, generatedEntities[1].attributes.name],
          namespace: [generatedEntities[0].attributes.namespace],
          state: [generatedEntities[0].attributes.state, generatedEntities[1].attributes.state],
          type: [generatedEntities[0].attributes.type, generatedEntities[1].attributes.type]
        }
      };
      const queryParams = {name: [generatedEntities[0].attributes.name]};
      const result = expApi.prepareDataUsingFilters(generatedEntities, queryParams);
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
          searchPattern: '',
          searchTimezone: reqMock.headers['timezone-offset']
        },
        valuesForFilterableAttrs: {
          name: [generatedEntities[0].attributes.name, generatedEntities[1].attributes.name],
          namespace: [generatedEntities[0].attributes.namespace],
          state: [generatedEntities[0].attributes.state, generatedEntities[1].attributes.state],
          type: [generatedEntities[0].attributes.type, generatedEntities[1].attributes.type]
        }
      };
      const queryParams = {name: '*'};
      const result = expApi.prepareDataUsingFilters(generatedEntities, queryParams);
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
          searchPattern: 'MNIST-SING-18-06-11-09-34-45-41',
          searchTimezone: reqMock.headers['timezone-offset']
        },
        valuesForFilterableAttrs: {
          name: [generatedEntities[0].attributes.name, generatedEntities[1].attributes.name],
          namespace: [generatedEntities[0].attributes.namespace],
          state: [generatedEntities[0].attributes.state, generatedEntities[1].attributes.state],
          type: [generatedEntities[0].attributes.type, generatedEntities[1].attributes.type]
        }
      };
      const searchPattern = 'mnist-SING-18-06-11-09-34-45-41';
      const result = expApi.prepareDataUsingFilters(generatedEntities, null, {
        pattern: searchPattern, timezoneOffset: reqMock.headers['timezone-offset']
      });
      expect(result).to.deep.equal(expectedResult);
    });
  });

  describe('generateExperimentEntities', function () {
    it('should return empty array if not data', function () {
      const result = expApi.generateExperimentEntities();
      expect(result).to.deep.equal([]);
    });

    it('should return generated entities if data provided', function () {
      const expectedResult = generatedEntities;
      const result = expApi.generateExperimentEntities(k8sRunEntities, k8sExpsEntities);
      expect(result).to.deep.equal(expectedResult);
    });

    it('should return generated entities if data without metrics provided', function () {
      delete k8sRunEntities[0].spec.metrics;
      delete generatedEntities[0].attributes.accuracy;
      const expectedResult = generatedEntities;
      const result = expApi.generateExperimentEntities(k8sRunEntities, k8sExpsEntities);
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
      const expectedResult = ['creationTimestamp', 'name', 'namespace', 'state', 'type', 'accuracy', 'podSelector',
        'podCount', 'parameters', 'trainingStartTime', 'trainingEndTime', 'trainingDurationTime', 'trainingTimeInQueue',
        'template-name', 'template-namespace', 'template-version'];
      const result = expApi.extractAttrsNames(generatedEntities);
      expect(result).to.deep.equal(expectedResult);
    });
  });

  describe('parseExperiments', function () {
    let generateExperimentEntitiesMock, prepareDataUsingFiltersMock,
      applyOrderParamsMock, extractAttrsNamesMock;
    beforeEach(function () {
      generateExperimentEntitiesMock = sinon.stub().returns(generatedEntities);
      prepareDataUsingFiltersMock = sinon.stub().returns({
        valuesForFilterableAttrs: {
          name: [generatedEntities[0].attributes.name, generatedEntities[1].attributes.name],
          namespace: [generatedEntities[0].attributes.namespace],
          state: [generatedEntities[0].attributes.state, generatedEntities[1].attributes.state],
          type: [generatedEntities[0].attributes.type, generatedEntities[1].attributes.type]
        },
        data: generatedEntities,
        queryParams: {
          name: [generatedEntities[0].attributes.name, generatedEntities[1].attributes.name],
          namespace: [generatedEntities[0].attributes.namespace],
          state: [generatedEntities[0].attributes.state, generatedEntities[1].attributes.state],
          type: [generatedEntities[0].attributes.type, generatedEntities[1].attributes.type],
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

    it('should return correct data', function () {
      const queryParams = {};
      expApi.__set__('generateExperimentEntities', generateExperimentEntitiesMock);
      expApi.__set__('prepareDataUsingFilters', prepareDataUsingFiltersMock);
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
            state: [generatedEntities[0].attributes.state, generatedEntities[1].attributes.state],
            type: [generatedEntities[0].attributes.type, generatedEntities[1].attributes.type]
          },
          current: {
            name: [generatedEntities[0].attributes.name, generatedEntities[1].attributes.name],
            namespace: [generatedEntities[0].attributes.namespace],
            state: [generatedEntities[0].attributes.state, generatedEntities[1].attributes.state],
            type: [generatedEntities[0].attributes.type, generatedEntities[1].attributes.type],
            searchPattern: ''
          }
        },
        params: ['creationTimestamp', 'name', 'namespace', 'podSelector', 'podCount', 'state', 'parameters', 'accuracy'],
        data: generatedEntities
      };
      const result = expApi.parseExperiments(k8sRunEntities, k8sExpsEntities, queryParams);
      expect(result).to.deep.equal(expectedResult);
      expect(generateExperimentEntitiesMock.calledOnce).to.equal(true);
      expect(prepareDataUsingFiltersMock.calledOnce).to.equal(true);
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
            status: `Terminated, containerID: ${podsList.items[0].status.containerStatuses[0].state.terminated.containerID}; exitCode: ${podsList.items[0].status.containerStatuses[0].state.terminated.exitCode}; finishedAt: ${podsList.items[0].status.containerStatuses[0].state.terminated.finishedAt}; reason: ${podsList.items[0].status.containerStatuses[0].state.terminated.reason}; startedAt: ${podsList.items[0].status.containerStatuses[0].state.terminated.startedAt}; `
          }
        ]
      }];
      expApi.__set__('k8s', k8sMock);
      expApi.getExperimentResourcesData(reqMock, resMock);
      deferred.resolve(podsList);
      process.nextTick(function () {
        expect(resMock.send.calledOnce).to.equal(true);
        expect(resMock.send.getCall(0).args[0]).to.deep.equal(expectedResult);
        expect(resMock.send.calledWith(expectedResult)).to.equal(true);
        expect(k8sMock.listPodsByLabelValue.calledOnce).to.equal(true);
        done();
      });
    });

  });

  describe('getExperimentLogs', function () {
    beforeEach(function () {
      deferred = Q.defer();
      elasticsearchUtilsMock = {
        getRunLastLogs: sinon.stub().returns(deferred.promise)
      };
      reqMock.params = {
        experiment: 'exp',
        owner: 'owner',
        mode: 'show',
        number: 100
      }
    });

    it('should return error missing required data', function () {
      delete reqMock.params.experiment;
      expApi.getExperimentLogs(reqMock, resMock);
      expect(resMock.status.calledOnce).to.equal(true);
      expect(resMock.status.calledWith(HttpStatus.BAD_REQUEST)).to.equal(true);
    });

    it('should return error if cannot fetch logs', function (done) {
      expApi.__set__('elasticsearchUtils', elasticsearchUtilsMock);
      expApi.getExperimentLogs(reqMock, resMock);
      deferred.reject(error);
      process.nextTick(function () {
        expect(resMock.status.calledOnce).to.equal(true);
        expect(resMock.status.calledWith(error.status)).to.equal(true);
        expect(elasticsearchUtilsMock.getRunLastLogs.calledOnce).to.equal(true);
        done();
      });
    });

    it('should return data if everything ok', function (done) {
      const expectedResult = 'result';
      expApi.__set__('elasticsearchUtils', elasticsearchUtilsMock);
      expApi.getExperimentLogs(reqMock, resMock);
      deferred.resolve(expectedResult);
      process.nextTick(function () {
        expect(resMock.send.calledOnce).to.equal(true);
        expect(resMock.send.getCall(0).args[0]).to.deep.equal(expectedResult);
        expect(resMock.send.calledWith(expectedResult)).to.equal(true);
        expect(elasticsearchUtilsMock.getRunLastLogs.calledOnce).to.equal(true);
        done();
      });
    });

  });

  describe('getAllExperimentLogs', function () {
    let elasticsearchClientMock, data, entry, searchMock, scrollMock, searchDeferred, scrollDeferred;

    beforeEach(function () {
      scrollDeferred = Q.defer();
      searchDeferred = Q.defer();
      elasticsearchUtilsMock = {
        getRunLastLogs: sinon.stub().returns(deferred.promise),
        getElasticsearchServiceUrl: sinon.stub().returns('url'),
        getLuceneQuery: sinon.stub().returns('query'),
        parseLogEntry: sinon.stub().returns('log')
      };
      searchMock = sinon.stub().returns(searchDeferred.promise);
      scrollMock = sinon.stub().returns(scrollDeferred.promise);
      elasticsearchClientMock = sinon.stub().returns({
        search: searchMock,
        scroll: scrollMock
      });
      reqMock.params = {
        experiment: 'exp',
        owner: 'owner'
      };
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
          hits: [entry, entry, entry],
          total: 6
        }
      };
    });

    it('should return error missing required data', function () {
      delete reqMock.params.experiment;
      expApi.getAllExperimentLogs(reqMock, resMock);
      expect(resMock.status.calledOnce).to.equal(true);
      expect(resMock.status.calledWith(HttpStatus.BAD_REQUEST)).to.equal(true);
    });

    it('should return error if cannot fetch logs', function (done) {
      expApi.__set__('elasticsearchUtils', elasticsearchUtilsMock);
      expApi.__set__('elasticsearch.Client', elasticsearchClientMock);
      searchDeferred.reject(error);
      expApi.getAllExperimentLogs(reqMock, resMock)
        .then(() => {
          expect(resMock.status.calledOnce).to.equal(true);
          expect(resMock.status.calledWith(error.status)).to.equal(true);
          expect(elasticsearchUtilsMock.getElasticsearchServiceUrl.calledOnce).to.equal(true);
          expect(elasticsearchUtilsMock.getLuceneQuery.calledOnce).to.equal(true);
          expect(searchMock.calledOnce).to.equal(true);
          expect(scrollMock.calledOnce).to.equal(false);
          done();
        });
    });

    it('should return result if everything ok in fetch logs', function (done) {
      expApi.__set__('elasticsearchUtils', elasticsearchUtilsMock);
      expApi.__set__('elasticsearch.Client', elasticsearchClientMock);
      searchDeferred.resolve(data);
      scrollDeferred.resolve(data);
      expApi.getAllExperimentLogs(reqMock, resMock)
        .then(() => {
          expect(resMock.write.callCount).to.equal(data.hits.total);
          expect(resMock.writeHead.calledOnce).to.equal(true);
          expect(resMock.end.calledOnce).to.equal(true);
          expect(elasticsearchUtilsMock.parseLogEntry.callCount).to.equal(data.hits.total);
          expect(searchMock.calledOnce).to.equal(true);
          expect(scrollMock.calledOnce).to.equal(true);
          done();
        });
    });

    it('should return error if scroll logs with fail', function (done) {
      expApi.__set__('elasticsearchUtils', elasticsearchUtilsMock);
      expApi.__set__('elasticsearch.Client', elasticsearchClientMock);
      searchDeferred.resolve(data);
      scrollDeferred.reject(error);
      expApi.getAllExperimentLogs(reqMock, resMock)
        .then(() => {
          expect(resMock.write.callCount).to.equal(data.hits.hits.length);
          expect(resMock.writeHead.calledOnce).to.equal(true);
          expect(resMock.end.calledOnce).to.equal(false);
          expect(elasticsearchUtilsMock.parseLogEntry.callCount).to.equal(data.hits.hits.length);
          expect(searchMock.calledOnce).to.equal(true);
          expect(scrollMock.calledOnce).to.equal(true);
          done();
        });
    });

  });
});
