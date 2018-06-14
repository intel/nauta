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

import {testAction} from '../../../utils';
import {getters, actions, mutations} from '../../../../../src/store/modules/experiments';
import axios from 'axios';
import MockAdapter from 'axios-mock-adapter';
import RESPONSE_TYPES from '../../../../../src/utils/constants/message-types';
import RESPONSE_MESSAGES from '../../../../../src/utils/constants/messages';

describe('VUEX modules experiments', () => {
  const state = {
    fetchingDataActive: false,
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
      }
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

    it('setFilterColumnValues', () => {
      const data = {options: [1], current: [2]};
      mutations.setFilterColumnValues(state, {data});
      expect(state.experiments.filterByColumnValue).to.deep.equal(data);
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
    });
  });
});
