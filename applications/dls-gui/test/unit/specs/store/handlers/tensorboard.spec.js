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
