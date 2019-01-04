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
import {testAction} from '../../../utils';
import {getters, actions, mutations} from '../../../../../src/store/modules/experiments';
import axios from 'axios';
import MockAdapter from 'axios-mock-adapter';
import RESPONSE_TYPES from '../../../../../src/utils/constants/message-types';
import RESPONSE_MESSAGES from '../../../../../src/utils/constants/messages';

describe('VUEX modules experiments', () => {
  const state = {
    fetchingDataActive: false,
    tensorboardLaunching: false,
    initialized: false,
    experiments: {
      data: [],
      params: [],
      filterByColumnValue: {
        current: {},
        options: {}
      },
      stats: {
        total: 0,
        a: 0,
        b: 0,
        pageNumber: 0,
        totalPagesCount: 0,
        filteredDataCount: 0,
        datetime: 1
      },
      resources: [{name: 'test1', data: 'data1'}]
    }
  };

  describe('Getters', () => {
    it('experimentsData', () => {
      const result = getters.experimentsData(state);
      expect(result).to.equal(state.experiments.data);
    });

    it('experimentsParams', () => {
      const result = getters.experimentsParams(state);
      expect(result).to.equal(state.experiments.params);
    });

    it('experimentsTotal', () => {
      const result = getters.experimentsTotal(state);
      expect(result).to.equal(state.experiments.stats.total);
    });

    it('experimentsBegin', () => {
      const result = getters.experimentsBegin(state);
      expect(result).to.equal(state.experiments.stats.a);
    });

    it('experimentsEnd', () => {
      const result = getters.experimentsEnd(state);
      expect(result).to.equal(state.experiments.stats.b);
    });

    it('experimentsPageNumber', () => {
      const result = getters.experimentsPageNumber(state);
      expect(result).to.equal(state.experiments.stats.pageNumber);
    });

    it('experimentsTotalPagesCount', () => {
      const result = getters.experimentsTotalPagesCount(state);
      expect(result).to.equal(state.experiments.stats.totalPagesCount);
    });

    it('lastUpdate', () => {
      const result = getters.lastUpdate(state);
      expect(result).to.equal(state.experiments.stats.datetime);
    });

    it('fetchingDataActive', () => {
      const result = getters.fetchingDataActive(state);
      expect(result).to.equal(state.fetchingDataActive);
    });

    it('tensorboardLaunching', () => {
      const result = getters.tensorboardLaunching(state);
      expect(result).to.equal(state.tensorboardLaunching);
    });

    it('columnValuesOptions', () => {
      const result = getters.columnValuesOptions(state);
      expect(result).to.equal(state.experiments.filterByColumnValue.options);
    });

    it('columnValuesApplied', () => {
      const result = getters.columnValuesApplied(state);
      expect(result).to.equal(state.experiments.filterByColumnValue.current);
    });

    it('filteredDataCount', () => {
      const result = getters.filteredDataCount(state);
      expect(result).to.equal(state.experiments.stats.filteredDataCount);
    });

    it('initializedDataFlag', () => {
      const result = getters.initializedDataFlag(state);
      expect(result).to.equal(state.initialized);
    });

    it('experimentResources should return item if exists', () => {
      const expName = 'test1';
      const expectedResult = 'data1';
      const result = getters.experimentResources(state)(expName);
      expect(result).to.equal(expectedResult);
    });

    it('experimentResources should return null if does not exist', () => {
      const expName = 'testXXXXXXXX';
      const expectedResult = null;
      const result = getters.experimentResources(state)(expName);
      expect(result).to.equal(expectedResult);
    });
  });

  describe('Mutations', () => {
    it('setExperimentsData', () => {
      const data = ['data'];
      mutations.setExperimentsData(state, {data});
      expect(state.experiments.data).to.deep.equal(data);
    });

    it('setExperimentsParams', () => {
      const data = ['data'];
      mutations.setExperimentsParams(state, {data});
      expect(state.experiments.params).to.deep.equal(data);
    });

    it('setExperimentsStats', () => {
      const data = ['data'];
      mutations.setExperimentsStats(state, {data});
      expect(state.experiments.stats).to.deep.equal(data);
    });

    it('setFetchingDataFlag', () => {
      const data = {isActive: true};
      mutations.setFetchingDataFlag(state, data);
      expect(state.fetchingDataActive).to.equal(data.isActive);
    });

    it('setTensorboardLaunchingFlag', () => {
      const data = {isActive: true};
      mutations.setTensorboardLaunchingFlag(state, data);
      expect(state.tensorboardLaunching).to.equal(data.isActive);
    });

    it('setFilterColumnValues', () => {
      const data = {options: [1], current: [2]};
      mutations.setFilterColumnValues(state, {data});
      expect(state.experiments.filterByColumnValue).to.deep.equal(data);
    });

    it('setInitializedData', () => {
      mutations.setInitializedData(state);
      expect(state.initialized).to.equal(true);
    });

    it('setExperimentsResource should add new item', () => {
      const expName = 'tested1';
      const data = 'data_tested_1';
      mutations.setExperimentsResource(state, {experimentName: expName, data});
      const newItem = state.experiments.resources.find((item) => {
        return item.name === expName;
      });
      expect(newItem).to.not.equal(null);
    });

    it('setExperimentsResource should update existing item', () => {
      const expName = state.experiments.resources[0].name;
      const data = 'data_tested_1';
      mutations.setExperimentsResource(state, {experimentName: expName, data});
      const newItem = state.experiments.resources.find((item) => {
        return item.name === expName;
      });
      expect(newItem).to.not.equal(null);
      expect(newItem.data).to.equal(data);
      expect(newItem.name).to.equal(expName);
    });
  });

  describe('Actions', () => {
    const state = {};
    let expectedMutations = [];
    let expectedActions = [];
    let mock = {};

    describe('getUserExperiments', () => {
      beforeEach(() => {
        expectedMutations = [];
        expectedActions = [];
        mock = new MockAdapter(axios);
        mock.reset();
      });

      it('should show error if internal server error occurs in  experiments fetching', (done) => {
        expectedMutations = [
          {type: 'setFetchingDataFlag', payload: {isActive: true}},
          {type: 'setFetchingDataFlag', payload: {isActive: false}}
        ];
        expectedActions = [
          {type: 'showError', payload: {type: RESPONSE_TYPES.ERROR, content: RESPONSE_MESSAGES.ERROR.INTERNAL_SERVER_ERROR}}
        ];
        mock.onGet('/api/experiments/list').reply(500, 'Internal Server Error');
        testAction(actions.getUserExperiments, {}, state, expectedMutations, expectedActions, done);
      });

      it('should show invalid token page if token is invalid', (done) => {
        expectedMutations = [
          {type: 'setFetchingDataFlag', payload: {isActive: true}},
          {type: 'setFetchingDataFlag', payload: {isActive: false}}
        ];
        expectedActions = [
          {type: 'handleLogOut', payload: '/invalid_token'}
        ];
        mock.onGet('/api/experiments/list').reply(401, {response: {status: 401}});
        testAction(actions.getUserExperiments, {}, state, expectedMutations, expectedActions, done);
      });

      it('should set experiments data if req with success', (done) => {
        const data = {
          data: ['test1'],
          params: ['test2'],
          stats: ['test3'],
          filterColumnValues: ['test4']
        };
        expectedMutations = [
          {type: 'setFetchingDataFlag', payload: {isActive: true}},
          {type: 'setExperimentsData', payload: {data: data.data}},
          {type: 'setExperimentsParams', payload: {data: data.params}},
          {type: 'setFilterColumnValues', payload: {data: data.filterColumnValues}},
          {type: 'setExperimentsStats', payload: {data: data.stats}},
          {type: 'setFetchingDataFlag', payload: {isActive: false}}
        ];
        expectedActions = [];
        mock.onGet('/api/experiments/list').reply(200, data);
        testAction(actions.getUserExperiments, {}, state, expectedMutations, expectedActions, done);
      });

      it('should not set flag about fetching data if refresh data mode triggered [success]', (done) => {
        const data = {
          data: ['test1'],
          params: ['test2'],
          stats: ['test3'],
          filterColumnValues: ['test4']
        };
        expectedMutations = [
          {type: 'setExperimentsData', payload: {data: data.data}},
          {type: 'setExperimentsParams', payload: {data: data.params}},
          {type: 'setFilterColumnValues', payload: {data: data.filterColumnValues}},
          {type: 'setExperimentsStats', payload: {data: data.stats}},
        ];
        expectedActions = [];
        mock.onGet('/api/experiments/list').reply(200, data);
        testAction(actions.getUserExperiments, {refreshMode: true}, state, expectedMutations, expectedActions, done);
      });

      it('should not set flag about fetching data if refresh data mode triggered [error]', (done) => {
        expectedMutations = [];
        expectedActions = [
          {type: 'showError', payload: {type: RESPONSE_TYPES.ERROR, content: RESPONSE_MESSAGES.ERROR.INTERNAL_SERVER_ERROR}}
        ];
        mock.onGet('/api/experiments/list').reply(500, 'Internal Server Error');
        testAction(actions.getUserExperiments, {refreshMode: true}, state, expectedMutations, expectedActions, done);
      });
    });

    describe('getExperimentResources', () => {
      const expName = 'exp1';
      beforeEach(() => {
        expectedMutations = [];
        expectedActions = [];
        mock = new MockAdapter(axios);
        mock.reset();
      });

      it('should show error if internal server error occurs in  experiments fetching', (done) => {
        expectedMutations = [];
        expectedActions = [
          {type: 'showError', payload: {type: RESPONSE_TYPES.ERROR, content: RESPONSE_MESSAGES.ERROR.INTERNAL_SERVER_ERROR}}
        ];
        mock.onGet(`/api/experiments/${expName}/resources`).reply(500, 'Internal Server Error');
        testAction(actions.getExperimentResources, {experimentName: expName}, state, expectedMutations, expectedActions, done);
      });

      it('should show invalid token page if token is invalid', (done) => {
        expectedMutations = [];
        expectedActions = [
          {type: 'handleLogOut', payload: '/invalid_token'}
        ];
        mock.onGet(`/api/experiments/${expName}/resources`).reply(401, {response: {status: 401}});
        testAction(actions.getExperimentResources, {experimentName: expName}, state, expectedMutations, expectedActions, done);
      });

      it('should set resources data if req with success', (done) => {
        const data = {
          data: ['test1']
        };
        expectedMutations = [
          {type: 'setExperimentsResource', payload: {experimentName: expName, data}}
        ];
        expectedActions = [];
        mock.onGet(`/api/experiments/${expName}/resources`).reply(200, data);
        testAction(actions.getExperimentResources, {experimentName: expName}, state, expectedMutations, expectedActions, done);
      });
    });
  });
});
