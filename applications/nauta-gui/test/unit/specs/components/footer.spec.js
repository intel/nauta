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
import Vuex from 'vuex';
import Vuetify from 'vuetify';
import VueRouter from 'vue-router'
import {shallowMount, createLocalVue} from '@vue/test-utils';
import Footer from '../../../../src/components/Footer';

describe('VUE components Footer', () => {
  let wrapper, router, store, localVue;
  beforeEach(function () {
    store = new Vuex.Store({});
    localVue = createLocalVue();
    localVue.use(Vuex);
    localVue.use(VueRouter);
    localVue.use(Vuetify);
    router = new VueRouter();
    wrapper = shallowMount(Footer, {store, router, localVue});
  });

  it('Should render footer with valid text', function () {
    const content = wrapper.text();
    const expectedText = 'Ⓒ Intel Corporation. All rights reserved';
    expect(content.includes(expectedText)).to.equal(true);
  });
});
