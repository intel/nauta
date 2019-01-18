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

// The Vue build version to load with the `import` command
// (runtime-only or standalone) has been set in webpack.base.conf with an alias.
import Vue from 'vue';
import Vuetify from 'vuetify';
import App from './App';
import router from './router';
import store from './store';
import axios from 'axios';
import Notifications from 'vue-notification';

import 'vuetify/dist/vuetify.min.css';
import 'material-icons/iconfont/material-icons.css';
import './fonts.css';

Vue.use(Notifications);
Vue.use(Vuetify, {
  theme: {
    intel_primary: '#0071c5',
    intel_secondary: '#003c71',
    intel_lightest_gray: '#f3f3f3'
  }
});

Vue.config.productionTip = false;

if (process.env.NODE_ENV === 'development') {
  axios.defaults.baseURL = 'http://localhost:9000';
}

router.beforeEach((to, from, next) => {
  if (to.meta.authorized) {
    store.dispatch('loadAuthority').then(() => {
      const authorized = store.getters.isLogged;
      if (!authorized) {
        next({path: '/invalid_token'});
      } else {
        next();
      }
    });
  } else {
    next();
  }
});

/* eslint-disable no-new */
new Vue({
  el: '#app',
  store,
  router,
  components: { App },
  template: '<App/>'
});
