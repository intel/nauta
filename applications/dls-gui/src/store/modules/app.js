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
