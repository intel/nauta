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

import {getExperiments, getExperimentsResources} from '../handlers/experiments';
import RESPONSE_TYPES from '../../utils/constants/message-types';
import RESPONSE_MESSAGES from '../../utils/constants/messages';

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
      filteredDataCount: 0,
      a: 0,
      b: 0,
      pageNumber: 0,
      totalPagesCount: 0,
      datetime: 0
    },
    resources: []
  }
};

export const getters = {
  experimentsData: state => state.experiments.data,
  experimentsParams: state => state.experiments.params,
  columnValuesOptions: state => state.experiments.filterByColumnValue.options,
  columnValuesApplied: state => state.experiments.filterByColumnValue.current,
  experimentsTotal: state => state.experiments.stats.total,
  filteredDataCount: state => state.experiments.stats.filteredDataCount,
  experimentsBegin: state => state.experiments.stats.a,
  experimentsEnd: state => state.experiments.stats.b,
  experimentsPageNumber: state => state.experiments.stats.pageNumber,
  experimentsTotalPagesCount: state => state.experiments.stats.totalPagesCount,
  lastUpdate: state => state.experiments.stats.datetime,
  fetchingDataActive: state => state.fetchingDataActive,
  tensorboardLaunching: state => state.tensorboardLaunching,
  initializedDataFlag: state => state.initialized,
  experimentResources: state => experimentName => {
    const item = state.experiments.resources.find((item) => {
      return item.name === experimentName;
    });
    return item ? item.data : null;
  }
};

export const actions = {
  getUserExperiments: ({commit, dispatch}, {limitPerPage, pageNo, orderBy, order, searchBy, names, states,
    namespaces, types, refreshMode}) => {
    if (!refreshMode) {
      commit('setFetchingDataFlag', {isActive: true});
    }
    getExperiments(limitPerPage, pageNo, orderBy, order, searchBy, names, states, namespaces, types)
      .then((res) => {
        const data = res.data;
        commit('setExperimentsData', {data: data.data});
        commit('setExperimentsParams', {data: data.params});
        commit('setFilterColumnValues', {data: data.filterColumnValues});
        commit('setExperimentsStats', {data: data.stats});
        if (!refreshMode) {
          commit('setFetchingDataFlag', {isActive: false});
        }
        commit('setInitializedData');
      })
      .catch((err) => {
        if (err && err.response && err.response.status && err.response.status === 401) {
          dispatch('handleLogOut', '/invalid_token');
        } else {
          dispatch('showError', {type: RESPONSE_TYPES.ERROR, content: RESPONSE_MESSAGES.ERROR.INTERNAL_SERVER_ERROR});
        }
        if (!refreshMode) {
          commit('setFetchingDataFlag', {isActive: false});
        }
      });
  },
  getExperimentResources: ({commit, dispatch}, {experimentName}) => {
    getExperimentsResources(experimentName)
      .then((res) => {
        const data = res.data;
        commit('setExperimentsResource', {experimentName, data});
      })
      .catch((err) => {
        if (err && err.response && err.response.status && err.response.status === 401) {
          dispatch('handleLogOut', '/invalid_token');
        } else {
          dispatch('showError', {type: RESPONSE_TYPES.ERROR, content: RESPONSE_MESSAGES.ERROR.INTERNAL_SERVER_ERROR});
        }
      });
  }
};

export const mutations = {
  setExperimentsData: (state, {data}) => {
    state.experiments.data = data;
  },
  setExperimentsParams: (state, {data}) => {
    state.experiments.params = data;
  },
  setFilterColumnValues: (state, {data}) => {
    state.experiments.filterByColumnValue = data;
  },
  setExperimentsStats: (state, {data}) => {
    state.experiments.stats = data;
  },
  setFetchingDataFlag: (state, {isActive}) => {
    state.fetchingDataActive = isActive;
  },
  setTensorboardLaunchingFlag: (state, {isActive}) => {
    state.tensorboardLaunching = isActive;
  },
  setInitializedData: (state) => {
    state.initialized = true;
  },
  setExperimentsResource: (state, {experimentName, data}) => {
    const filteredData = state.experiments.resources.filter((item) => {
      return item.name !== experimentName;
    });
    const newData = [{name: experimentName, data: data}];
    state.experiments.resources = filteredData.concat(newData);
  }
};

export default {
  state,
  getters,
  actions,
  mutations
}
