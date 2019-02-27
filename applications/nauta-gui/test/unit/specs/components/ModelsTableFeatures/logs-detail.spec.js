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
import Vuetify from 'vuetify';
import VueRouter from 'vue-router'
import {shallowMount, createLocalVue} from '@vue/test-utils';
import FooterElements from '../../../../../src/components/ModelsTableFeatures/LogsDetail';

describe('VUE components LogsDetail', () => {
  let wrapper, router, props, localVue;
  beforeEach(function () {
    props = {
      keyname: 'keyname',
      name: 'name1',
      owner: 'owner1'
    };
    localVue = createLocalVue();
    localVue.use(VueRouter);
    localVue.use(Vuetify);
    router = new VueRouter();
    wrapper = shallowMount(FooterElements, {propsData: props, router, localVue});
  });

  it('Should render logs details elements correctly', function () {
    expect(wrapper.text().includes(props.keyname)).to.equal(true);
  });

});
