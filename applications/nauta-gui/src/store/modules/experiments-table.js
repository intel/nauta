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

export const INITIAL_COLUMNS = ['name', 'state', 'creationTimestamp', 'trainingStartTime', 'trainingDurationTime', 'type', 'namespace'];
export const ALWAYS_VISIBLE_COLUMNS = ['name', 'state'];
export const FILTERABLE_BY_VAL_COLUMNS = ['name', 'namespace', 'state', 'type'];

const state = {
  experiments: {
    selectedByUser: [],
    allUsersMode: false
  },
  columns: {
    selectedByUser: [].concat(INITIAL_COLUMNS)
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

export const getters = {
  selectedExperimentsByUser: state => state.experiments.selectedByUser,
  currentlyVisibleColumns: state => state.columns.selectedByUser,
  allUsersMode: state => state.experiments.allUsersMode,
  currentPage: state => state.pagination.currentPage,
  itemsCountPerPage: state => state.pagination.itemsCountPerPage,
  refreshInterval: state => state.refresh.interval,
  refreshMessage: state => state.refresh.message
};

export const actions = {
  clearExperimentSelection: ({commit}) => {
    commit('setExperimentsSelectedData', {data: []});
  },
  markExperimentsAsSelected: ({commit}, {data}) => {
    commit('setExperimentsSelectedData', {data});
  },
  markExperimentAsSelected: ({commit}, {data}) => {
    commit('setExperimentSelectedData', {data});
  },
  showColumns: ({commit}, {data}) => {
    commit('setColumnsSelectedData', {data})
  },
  showColumn: ({commit}, {data}) => {
    commit('setColumnSelectedData', {data})
  },
  clearColumnsSelection: ({commit}) => {
    commit('setColumnsSelectedData', {data: INITIAL_COLUMNS})
  },
  switchAllUsersMode: ({commit}) => {
    commit('setAllUsersMode')
  },
  clearAllUsersMode: ({commit}) => {
    commit('setAllUsersMode', {data: false})
  },
  updatePageNumber: ({commit}, {data}) => {
    commit('setPageNumber', {data});
  },
  updateItemsCountPerPage: ({commit}, {data}) => {
    commit('setItemsCountPerPage', {data});
  },
  showRefreshMessage: ({commit}, {data}) => {
    commit('setRefreshMessage', {data});
  },
  updateRefreshInterval: ({commit}, {data}) => {
    commit('setRefreshInterval', {data});
  }
};

export const mutations = {
  setExperimentsSelectedData: (state, {data}) => {
    state.experiments.selectedByUser = data;
  },
  setExperimentSelectedData: (state, {data}) => {
    state.experiments.selectedByUser = state.experiments.selectedByUser.concat(data);
  },
  setColumnsSelectedData: (state, {data}) => {
    state.columns.selectedByUser = data;
  },
  setColumnSelectedData: (state, {data}) => {
    state.columns.selectedByUser = state.columns.selectedByUser.concat(data);
  },
  setAllUsersMode: (state, data) => {
    if (!data) {
      state.experiments.allUsersMode = !state.experiments.allUsersMode;
    } else {
      state.experiments.allUsersMode = data.data;
    }
  },
  setPageNumber: (state, {data}) => {
    state.pagination.currentPage = data;
  },
  setItemsCountPerPage: (state, {data}) => {
    state.pagination.itemsCountPerPage = data;
  },
  setRefreshMessage: (state, {data}) => {
    state.refresh.message = data;
  },
  setRefreshInterval: (state, {data}) => {
    state.refresh.interval = data;
  }
};

export default {
  state,
  getters,
  actions,
  mutations
}
