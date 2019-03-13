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
import FooterElements from '../../../../../src/components/ModelsTableFeatures/ExpResourcesDetail';

describe('VUE components FooterElements', () => {
  let wrapper, router, props, localVue;
  beforeEach(function () {
    props = {
      keyname: 'keyname',
      podsList: [
        {
          name: 'name1',
          state: ['running'],
          containers: [
            {
              name: 'container1',
              status: 'running',
              resources: {
                requests: {
                  cpu: '1',
                  memory: '2'
                },
                limits: {
                  cpu: '1',
                  memory: '2'
                }
              }
            }
          ]
        },
        {
          name: 'name2',
          state: ['running'],
          containers: [
            {
              name: 'container1',
              status: 'running',
              resources: {
                requests: {
                  cpu: '12',
                  memory: '21'
                },
                limits: {
                  cpu: '12',
                  memory: '21'
                }
              }
            }
          ]
        }
      ]
    };
    localVue = createLocalVue();
    localVue.use(VueRouter);
    localVue.use(Vuetify);
    router = new VueRouter();
    wrapper = shallowMount(FooterElements, {propsData: props, router, localVue});
  });

  it('Should render exp resources details elements correctly', function () {
    expect(wrapper.text().includes(props.keyname)).to.equal(true);
  });

  it('Should parse exp state details correctly', function () {
    const state = ['state1', 'state2'];
    const expectedStateString = 'state1, state2';
    expect(wrapper.vm.parseValue('state', state)).to.equal(expectedStateString);
  });

  it('Should parse exp state details correctly when state obj empty', function () {
    const state = null;
    const expectedStateString = '--';
    expect(wrapper.vm.parseValue('state', state)).to.equal(expectedStateString);
  });

  it('Should parse exp resources details correctly', function () {
    const resources = {
      limits: {
        cpu: '1'
      }
    };
    const expectedStateString = '1';
    expect(wrapper.vm.parseValue('resources', 'cpu', 'limits', resources)).to.equal(expectedStateString);
  });

  it('Should parse exp state details correctly when resources cpu obj empty', function () {
    const resources = {};
    const expectedStateString = '--';
    expect(wrapper.vm.parseValue('resources', 'cpu', resources)).to.equal(expectedStateString);
  });

  it('Should parse exp state details correctly when resources obj empty', function () {
    const resources = null;
    const expectedStateString = '--';
    expect(wrapper.vm.parseValue('resources', 'cpu', resources)).to.equal(expectedStateString);
  });

  it('Should parse data with unknown key correctly', function () {
    const keyname = 'unknownKey';
    const value = 'unknownValue';
    const expectedStateString = 'unknownValue';
    expect(wrapper.vm.parseValue(keyname, value)).to.equal(expectedStateString);
  });

});
