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

import cookies from 'js-cookie';
import router from '../../router';
import {decodeAuthK8SToken} from '../handlers/auth';
import RESPONSE_TYPES from '../../utils/constants/message-types';
import RESPONSE_MESSAGES from '../../utils/constants/messages';

const INVALID_TOKEN_STATUS_GROUP = 4;
const TOKEN_COOKIE_KEY = 'TOKEN';

const state = {
  logged: false,
  username: 'anonymous'
};

export const getters = {
  isLogged: state => state.logged,
  username: state => state.username
};

export const actions = {
  loadAuthority: ({commit, dispatch}, token) => {
    const savedToken = token || cookies.get(TOKEN_COOKIE_KEY);
    decodeAuthK8SToken(savedToken)
      .then((res) => {
        const logged = true;
        const username = res.data.decoded['kubernetes.io/serviceaccount/service-account.name'];
        cookies.set(TOKEN_COOKIE_KEY, savedToken);
        commit('setAuthority', {logged, username});
        dispatch('hideSpinner');
        dispatch('showMenuToggleBtn');
        dispatch('showUserbox');
        router.push({path: '/models'})
      })
      .catch((err) => {
        dispatch('hideSpinner');
        if (err && err.response && err.response.status && Math.round(err.response.status / 100) === INVALID_TOKEN_STATUS_GROUP) {
          router.push({path: '/invalid_token'});
        } else {
          dispatch('showError', {type: RESPONSE_TYPES.ERROR, content: RESPONSE_MESSAGES.ERROR.INTERNAL_SERVER_ERROR});
        }
      });
  },
  clearAuthorityData: ({commit}) => {
    cookies.remove(TOKEN_COOKIE_KEY);
    commit('setAuthority', {logged: false, username: ''});
    location.reload();
  }
};

export const mutations = {
  setAuthority: (state, {logged, username}) => {
    state.logged = logged;
    state.username = username;
  }
};

export default {
  state,
  getters,
  actions,
  mutations
}
