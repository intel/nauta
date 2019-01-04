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
import RESPONSE_TYPES from '../../utils/constants/message-types';

const DEFAULT_BANNER_TYPE = RESPONSE_TYPES.WARNING;

const state = {
  menu: {
    visible: false,
    btnVisible: false
  },
  userbox: {
    visible: false
  },
  error: {
    content: '',
    type: DEFAULT_BANNER_TYPE,
    visible: false,
    time: null
  }
};

export const getters = {
  menuVisibility: state => state.menu.visible,
  menuBtnVisibility: state => state.menu.btnVisible,
  getUserboxParams: state => state.userbox,
  errorType: state => state.error.type,
  errorTime: state => state.error.time,
  errorContent: state => state.error.content
};

export const actions = {
  toggleMenu: ({commit}) => {
    commit('setMenuVisibility');
  },
  showMenuToggleBtn: ({commit}) => {
    commit('setMenuToggleBtnVisibility', true);
  },
  hideMenuToggleBtn: ({commit}) => {
    commit('setMenuToggleBtnVisibility', false);
  },
  showUserbox: ({commit}) => {
    commit('setUserboxVisibility', true);
  },
  hideUserbox: ({commit}) => {
    commit('setUserboxVisibility', false);
  },
  showError: ({commit}, {type, content}) => {
    commit('setError', {type, content});
  },
  hideError: ({commit}) => {
    commit('removeError');
  }
};

export const mutations = {
  setMenuVisibility: (state, visible) => {
    state.menu.visible = typeof (visible) !== 'undefined' ? visible : !state.menu.visible;
  },
  setMenuToggleBtnVisibility: (state, visibility) => {
    state.menu.btnVisible = visibility;
  },
  setUserboxVisibility: (state, visibility) => {
    state.userbox.visible = visibility;
  },
  setError: (state, {type, content}) => {
    const currentTime = Date.now();
    const lastErrorTimeDiffer = currentTime - state.error.time;
    const updateTheSameErrorInterval = 10000;
    if (state.error.content === content && state.error.type === type) {
      if (lastErrorTimeDiffer > updateTheSameErrorInterval) {
        state.error.time = currentTime;
      }
    } else {
      state.error.time = currentTime;
    }
    state.error.type = type;
    state.error.content = content;
    state.error.visible = true;
  },
  removeError: (state) => {
    state.error.type = '';
    state.error.content = '';
    state.error.visible = false;
  }
};

export default {
  state,
  getters,
  actions,
  mutations
}
