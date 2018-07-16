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

import Vuex from 'vuex';
import Vuetify from 'vuetify';
import sinon from 'sinon';
import VueRouter from 'vue-router'
import {shallowMount, createLocalVue} from '@vue/test-utils';
import * as tb from '../../../../src/store/handlers/tensorboard';
import Q from 'q';
import TensorboardCreator from '../../../../src/components/TensorBoardCreator';

describe('VUE components TensorBoardCreator', () => {
  let wrapper, router, deferedLaunch, deferedCheck, launchStub, checkStub, localVue, launchData, clock, windowMock;
  beforeEach(function () {
    localVue = createLocalVue();
    localVue.use(Vuex);
    localVue.use(VueRouter);
    localVue.use(Vuetify);
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
