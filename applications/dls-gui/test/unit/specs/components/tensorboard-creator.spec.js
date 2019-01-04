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
import sinon from 'sinon';
import VueRouter from 'vue-router'
import {shallowMount, createLocalVue} from '@vue/test-utils';
import * as tb from '../../../../src/store/handlers/tensorboard';
import Q from 'q';
import TensorboardCreator from '../../../../src/components/TensorBoardCreator';

describe('VUE components TensorBoardCreator', () => {
  let wrapper, router, deferedLaunch, deferedCheck, launchStub, checkStub, localVue, launchData, clock, windowMock,
    store, actions;
  beforeEach(function () {
    localVue = createLocalVue();
    localVue.use(Vuex);
    localVue.use(VueRouter);
    localVue.use(Vuetify);
    actions = {
      showError: sinon.spy()
    };
    store = new Vuex.Store({
      actions
    });
    router = new VueRouter();
    deferedLaunch = Q.defer();
    deferedCheck = Q.defer();
    launchStub = sinon.stub(tb, 'launchTensorBoard').returns(deferedLaunch.promise);
    checkStub = sinon.stub(tb, 'checkIsTBInstanceReady').returns(deferedCheck.promise);
    launchData = {
      data: {
        url: 'url',
        id: 'id'
      }
    };
    clock = sinon.useFakeTimers();
    windowMock = sinon.stub(window.location, 'assign');
  });

  afterEach(() => {
    launchStub.restore();
    checkStub.restore();
    clock.restore();
    windowMock.restore();
  });

  it('Should call launch method on component instance creation', function () {
    deferedLaunch.reject();
    wrapper = shallowMount(TensorboardCreator, {router, localVue});
    expect(launchStub.calledOnce).to.equal(true);
  });

  it('Should not check instance state if instance not created', function () {
    delete launchData.data.id;
    delete launchData.data.url;
    deferedLaunch.resolve(launchData);
    wrapper = shallowMount(TensorboardCreator, {router, localVue});
    expect(checkStub.called).to.equal(false);
  });

  it('Should set interval and call check method if launch request with success but invalid runs occurred', function (done) {
    launchData.data.invalidRuns = [{name: 1}];
    deferedLaunch.resolve(launchData);
    deferedCheck.resolve();
    wrapper = shallowMount(TensorboardCreator, {router, localVue, store});
    expect(launchStub.calledOnce).to.equal(true);
    process.nextTick(() => {
      clock.tick(5100);
      expect(checkStub.calledOnce).to.equal(true);
      expect(actions.showError.calledOnce).to.equal(true);
      done();
    });
  });

  it('Should set interval and call check method if launch request with success', function (done) {
    deferedLaunch.resolve(launchData);
    deferedCheck.resolve();
    wrapper = shallowMount(TensorboardCreator, {router, localVue});
    expect(launchStub.calledOnce).to.equal(true);
    process.nextTick(() => {
      clock.tick(5100);
      expect(checkStub.calledOnce).to.equal(true);
      done();
    });
  });

  it('Should retry check method if instance not ready after 5 seconds', function (done) {
    deferedLaunch.resolve(launchData);
    deferedCheck.reject();
    wrapper = shallowMount(TensorboardCreator, {router, localVue});
    expect(launchStub.calledOnce).to.equal(true);
    process.nextTick(() => {
      clock.tick(10100);
      expect(checkStub.calledTwice).to.equal(true);
      done();
    });
  });

  it('Should retry check method if max retries not achieved', function (done) {
    deferedLaunch.resolve(launchData);
    deferedCheck.reject();
    wrapper = shallowMount(TensorboardCreator, {router, localVue});
    expect(launchStub.calledOnce).to.equal(true);
    process.nextTick(() => {
      const maxRetries = 20;
      clock.tick(104000);
      expect(checkStub.callCount).to.equal(maxRetries);
      done();
    });
  });
});
