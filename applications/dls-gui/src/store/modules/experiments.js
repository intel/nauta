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

import router from '../../router';
import {getExperiments} from '../handlers/experiments';
import RESPONSE_TYPES from '../../utils/constants/message-types';
import RESPONSE_MESSAGES from '../../utils/constants/messages';

const state = {
  experiments: {
    data: [],
    params: [],
    stats: {
      total: 0,
      a: 0,
      b: 0,
      pageNumber: 0,
      totalPagesCount: 0
    }
  }
};

export const getters = {
  experimentsData: state => state.experiments.data,
  experimentsParams: state => state.experiments.params,
  experimentsTotal: state => state.experiments.stats.total,
  experimentsBegin: state => state.experiments.stats.a,
  experimentsEnd: state => state.experiments.stats.b,
  experimentsPageNumber: state => state.experiments.stats.pageNumber,
  experimentsTotalPagesCount: state => state.experiments.stats.totalPagesCount
};

export const actions = {
  getUserExperiments: ({commit, dispatch}, {limitPerPage, pageNo, orderBy, order, searchBy}) => {
    getExperiments(limitPerPage, pageNo, orderBy, order, searchBy)
      .then((res) => {
        const data = res.data;
        commit('setExperimentsData', {data: data.data});
        commit('setExperimentsParams', {data: data.params});
        commit('setExperimentsStats', {data: data.stats});
      })
      .catch((err) => {
        if (err && err.response && err.response.status && err.response.status === 401) {
          router.push({path: '/invalid_token'});
          dispatch('clearAuthorityData');
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
  setExperimentsStats: (state, {data}) => {
    state.experiments.stats = data;
  }
};

export default {
  state,
  getters,
  actions,
  mutations
}
