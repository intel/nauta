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
