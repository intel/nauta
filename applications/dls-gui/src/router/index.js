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
import Vue from 'vue';
import Router from 'vue-router';
import ModelsTable from '../components/ModelsTable.vue';
import Home from '../components/Home.vue';
import TensorBoardCreator from '../components/TensorBoardCreator';
import InvalidToken from '../components/InvalidToken.vue';
import SignedOut from '../components/SignedOut.vue';

Vue.use(Router);

const router = new Router({
  mode: 'history',
  routes: [
    {
      path: '/',
      name: 'Home',
      component: Home,
      meta: {
        authorized: false
      }
    },
    {
      path: '/models',
      name: 'Models',
      component: ModelsTable,
      meta: {
        authorized: true
      }
    },
    {
      path: '/tensorboard',
      name: 'TensorBoardCreator',
      component: TensorBoardCreator,
      meta: {
        authorized: true
      }
    },
    {
      path: '/invalid_token',
      name: 'InvalidToken',
      component: InvalidToken,
      meta: {
        authorized: false
      }
    },
    {
      path: '/signed_out',
      name: 'SignedOut',
      component: SignedOut,
      meta: {
        authorized: false
      }
    }
  ]
});

export default router;
