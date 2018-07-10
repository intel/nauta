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

import sinon from 'sinon';
import cookies from 'js-cookie';
import axios from 'axios';
import MockAdapter from 'axios-mock-adapter';
import {launchTensorBoard, checkIsTBInstanceReady} from '../../../../../src/store/handlers/tensorboard';

describe('VUEX handlers tensorboard', () => {

  let cookieMock;

  describe('launchTensorBoard', () => {

    const COOKIE_TOKEN_KEY = 'TOKEN';
    const RUNS_LIST = [1, 2, 3];

    beforeEach(() => {
      cookieMock = sinon.stub(cookies, 'get');
    });

    afterEach(() => {
      cookieMock.restore();
    });

    it('should load token from cookie before request', () => {
      launchTensorBoard(RUNS_LIST);
      expect(cookieMock.calledOnce).to.equal(true);
      expect(cookieMock.calledWith(COOKIE_TOKEN_KEY)).to.equal(true);
    });
  });

  describe('checkIsTBInstanceReady', () => {

    const COOKIE_TOKEN_KEY = 'TOKEN';
    const INSTANCE_ID = 1;
    const error = 'error';
    let mock, response;

    beforeEach(() => {
      cookieMock = sinon.stub(cookies, 'get');
      mock = new MockAdapter(axios);
      mock.reset();
      response = {
        status: 'RUNNING'
      }
    });

    afterEach(() => {
      cookieMock.restore();
    });

    it('should load token from cookie before request', () => {
      mock.onGet(`/api/tensorboard/status/${INSTANCE_ID}`).reply(500, 'Internal Server Error');
      return checkIsTBInstanceReady(INSTANCE_ID)
        .catch(() => {
          expect(cookieMock.calledOnce).to.equal(true);
          expect(cookieMock.calledWith(COOKIE_TOKEN_KEY)).to.equal(true);
        });
    });

    it('should return error if cannot perform request', () => {
      mock.onGet(`/api/tensorboard/status/${INSTANCE_ID}`).reply(500, error);
      return checkIsTBInstanceReady(INSTANCE_ID)
        .catch((err) => {
          expect(err.response.data).to.deep.equal(error);
        });
    });

    it('should return status if request with success', () => {
      mock.onGet(`/api/tensorboard/status/${INSTANCE_ID}`).reply(200, response);
      return checkIsTBInstanceReady(INSTANCE_ID)
        .then((data) => {
          expect(data.data).to.deep.equal(response);
        });
    });

    it('should return error if request with success but instance not running', () => {
      response.status = 'CREATING';
      mock.onGet(`/api/tensorboard/status/${INSTANCE_ID}`).reply(200, response);
      return checkIsTBInstanceReady(INSTANCE_ID)
        .catch((data) => {
          expect(data.data).to.deep.equal(response);
        });
    });
  });


});
