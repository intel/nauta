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
import cookies from 'js-cookie';
import router from '../../router';
import {decodeAuthK8SToken, getK8SDashboardCsrfToken, getK8SDashboardCookieContent} from '../handlers/auth';
import RESPONSE_TYPES from '../../utils/constants/message-types';
import RESPONSE_MESSAGES from '../../utils/constants/messages';

const INVALID_TOKEN_STATUS_GROUP = 4;
const TOKEN_COOKIE_KEY = 'TOKEN';

const state = {
  logged: false,
  username: 'anonymous',
  authLoadingState: false
};

export const getters = {
  isLogged: state => state.logged,
  username: state => state.username,
  authLoadingState: state => state.authLoadingState
};

export const actions = {
  loadAuthority: ({commit, dispatch}, token) => {
    const savedToken = token || cookies.get(TOKEN_COOKIE_KEY);
    commit('setAuthLoadingState', true);
    return decodeAuthK8SToken(savedToken)
      .then((res) => {
        const logged = true;
        const username = res.data.decoded.username;
        cookies.set(TOKEN_COOKIE_KEY, savedToken);
        commit('setAuthority', {logged, username});
        dispatch('showMenuToggleBtn');
        dispatch('showUserbox');
        commit('setAuthLoadingState', false);
      })
      .catch((err) => {
        commit('setAuthLoadingState', false);
        if (err && err.response && err.response.status && Math.round(err.response.status / 100) === INVALID_TOKEN_STATUS_GROUP) {
          router.push({path: '/invalid_token'});
        } else {
          dispatch('showError', {type: RESPONSE_TYPES.ERROR, content: RESPONSE_MESSAGES.ERROR.INTERNAL_SERVER_ERROR});
        }
      });
  },
  handleLogOut: ({commit, dispatch}, redirectionPath) => {
    cookies.remove(TOKEN_COOKIE_KEY);
    dispatch('hideMenuToggleBtn')
      .then(() => {
        return dispatch('hideUserbox');
      })
      .then(() => {
        commit('setAuthority', {logged: false, username: ''});
        router.push({path: redirectionPath});
      });
  },
  logIntoK8SDashboard: ({dispatch}) => {
    getK8SDashboardCsrfToken()
      .then((res) => {
        const csrfToken = res.data.token;
        const authToken = cookies.get(TOKEN_COOKIE_KEY);
        return getK8SDashboardCookieContent(csrfToken, authToken);
      })
      .then((res) => {
        const jweToken = res.data.jweToken;
        cookies.set('jweToken', jweToken, {domain: 'localhost', path: '/dashboard'});
      })
      .catch(() => {
        dispatch('showError', {type: RESPONSE_TYPES.ERROR, content: RESPONSE_MESSAGES.ERROR.INTERNAL_SERVER_ERROR});
      });
  }
};

export const mutations = {
  setAuthority: (state, {logged, username}) => {
    state.logged = logged;
    state.username = username;
  },
  setAuthLoadingState: (state, isActive) => {
    state.authLoadingState = isActive;
  }
};

export default {
  state,
  getters,
  actions,
  mutations
}
