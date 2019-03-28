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
import {getters, actions, mutations} from '../../../../../src/store/modules/experiments-table';

describe('VUEX modules experiments-table', () => {
  const state = {
    experiments: {
      selectedByUser: [],
      allUsersMode: false
    },
    columns: {
      selectedByUser: [].concat(['name', 'state', 'creationTimestamp', 'trainingStartTime', 'trainingDurationTime',
        'type', 'namespace'])
    },
    pagination: {
      itemsCountPerPage: 5,
      currentPage: 1
    },
    refresh: {
      interval: 30,
      message: ''
    }
  };

  describe('Getters', () => {
    it('selectedExperimentsByUser', () => {
      const result = getters.selectedExperimentsByUser(state);
      expect(result).to.equal(state.experiments.selectedByUser);
    });

    it('currentlyVisibleColumns', () => {
      const result = getters.currentlyVisibleColumns(state);
      expect(result).to.equal(state.columns.selectedByUser);
    });

    it('allUsersMode', () => {
      const result = getters.allUsersMode(state);
      expect(result).to.equal(state.experiments.allUsersMode);
    });

    it('currentPage', () => {
      const result = getters.currentPage(state);
      expect(result).to.equal(state.pagination.currentPage);
    });

    it('itemsCountPerPage', () => {
      const result = getters.itemsCountPerPage(state);
      expect(result).to.equal(state.pagination.itemsCountPerPage);
    });

    it('refreshInterval', () => {
      const result = getters.refreshInterval(state);
      expect(result).to.equal(state.refresh.interval);
    });

    it('refreshMessage', () => {
      const result = getters.refreshMessage(state);
      expect(result).to.equal(state.refresh.message);
    });

  });

  describe('Mutations', () => {

    it('setExperimentSelectedData', () => {
      const data = ['data'];
      mutations.setExperimentSelectedData(state, {data});
      expect(state.experiments.selectedByUser).to.deep.equal(data);
    });

    it('setExperimentsSelectedData', () => {
      const data = ['data'];
      mutations.setExperimentsSelectedData(state, {data});
      expect(state.experiments.selectedByUser).to.deep.equal(data);
    });

    it('setColumnSelectedData', () => {
      const data = ['data'];
      mutations.setColumnSelectedData(state, {data});
      expect(state.columns.selectedByUser.length).to.equal(8);
      expect(state.columns.selectedByUser.includes(data[0])).to.equal(true);
    });

    it('setColumnsSelectedData', () => {
      const data = ['data'];
      mutations.setColumnsSelectedData(state, {data});
      expect(state.columns.selectedByUser).to.deep.equal(data);
    });

    it('setAllUsersMode with arg', () => {
      const arg = true;
      mutations.setAllUsersMode(state, {data: arg});
      expect(state.experiments.allUsersMode).to.equal(arg);
    });

    it('setAllUsersMode without arg', () => {
      const initialVal = state.experiments.allUsersMode;
      mutations.setAllUsersMode(state);
      expect(state.experiments.allUsersMode).to.equal(!initialVal);
    });

    it('setPageNumber', () => {
      const data = 3;
      mutations.setPageNumber(state, {data});
      expect(state.pagination.currentPage).to.equal(data);
    });

    it('setItemsCountPerPage ', () => {
      const data = 3;
      mutations.setItemsCountPerPage(state, {data});
      expect(state.pagination.itemsCountPerPage).to.equal(data);
    });

    it('setRefreshMessage', () => {
      const data = 'test message';
      mutations.setRefreshMessage(state, {data});
      expect(state.refresh.message).to.equal(data);
    });

    it('setRefreshInterval', () => {
      const data = 45;
      mutations.setRefreshInterval(state, {data});
      expect(state.refresh.interval).to.equal(data);
    });

  });

  describe('Actions', () => {

    it('clearExperimentSelection', (done) => {
      testAction(actions.clearExperimentSelection, null, state, [
        { type: 'setExperimentsSelectedData', payload: {data: []} }
      ], [], done);
    });

    it('markExperimentsAsSelected', (done) => {
      const payload = {data: ['test']};
      testAction(actions.markExperimentsAsSelected, payload, state, [
        { type: 'setExperimentsSelectedData', payload }
      ], [], done);
    });

    it('markExperimentAsSelected', (done) => {
      const payload = {data: ['test']};
      testAction(actions.markExperimentAsSelected, payload, state, [
        { type: 'setExperimentSelectedData', payload }
      ], [], done);
    });

    it('showColumns', (done) => {
      const payload = {data: ['test']};
      testAction(actions.showColumns, payload, state, [
        { type: 'setColumnsSelectedData', payload }
      ], [], done);
    });

    it('showColumn', (done) => {
      const payload = {data: ['test']};
      testAction(actions.showColumn, payload, state, [
        { type: 'setColumnSelectedData', payload }
      ], [], done);
    });

    it('clearColumnsSelection', (done) => {
      const payload = {data: ['name', 'state', 'creationTimestamp', 'trainingStartTime', 'trainingDurationTime',
        'type', 'namespace']};
      testAction(actions.clearColumnsSelection, null, state, [
        { type: 'setColumnsSelectedData', payload  }
      ], [], done);
    });

    it('switchAllUsersMode', (done) => {
      testAction(actions.switchAllUsersMode, null, state, [
        { type: 'setAllUsersMode' }
      ], [], done);
    });

    it('clearAllUsersMode', (done) => {
      const payload = {data: false};
      testAction(actions.clearAllUsersMode, null, state, [
        { type: 'setAllUsersMode', payload }
      ], [], done);
    });

    it('updatePageNumber', (done) => {
      const payload = {data: 3};
      testAction(actions.updatePageNumber, payload, state, [
        { type: 'setPageNumber', payload }
      ], [], done);
    });

    it('updateItemsCountPerPage', (done) => {
      const payload = {data: 30};
      testAction(actions.updateItemsCountPerPage, payload, state, [
        { type: 'setItemsCountPerPage', payload }
      ], [], done);
    });

    it('showRefreshMessage', (done) => {
      const payload = {data: 'test'};
      testAction(actions.showRefreshMessage, payload, state, [
        { type: 'setRefreshMessage', payload }
      ], [], done);
    });

    it('updateRefreshInterval', (done) => {
      const payload = {data: 30};
      testAction(actions.updateRefreshInterval, payload, state, [
        { type: 'setRefreshInterval', payload }
      ], [], done);
    });

  });
});
