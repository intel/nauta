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
import {testAction} from '../../../utils';
import {getters, actions, mutations} from '../../../../../src/store/modules/auth';
import axios from 'axios';
import MockAdapter from 'axios-mock-adapter';
import sinon from 'sinon';
import RESPONSE_TYPES from '../../../../../src/utils/constants/message-types';
import RESPONSE_MESSAGES from '../../../../../src/utils/constants/messages';
import Q from 'q';

describe('VUEX modules auth', () => {
  const state = {
    logged: false,
    username: 'anonymous',
    authLoadingState: false
  };

  describe('Getters', () => {
    it('isLogged', () => {
      const result = getters.isLogged(state);
      expect(result).to.equal(state.logged);
    });

    it('username', () => {
      const result = getters.username(state);
      expect(result).to.equal(state.username);
    });

    it('authLoadingState', () => {
      const result = getters.authLoadingState(state);
      expect(result).to.equal(state.authLoadingState);
    });
  });

  describe('Mutations', () => {
    it('setAuthority', () => {
      const logged = true;
      const username = 'username';
      mutations.setAuthority(state, {logged, username});
      expect(state.logged).to.deep.equal(logged);
      expect(state.username).to.deep.equal(username);
    });

    it('setAuthLoadingState', () => {
      const isActive = true;
      mutations.setAuthLoadingState(state, isActive);
      expect(state.authLoadingState).to.equal(isActive);
    });
  });

  describe('Actions', () => {
    const token = 'token';
    const state = {};
    let expectedMutations = [];
    let expectedActions = [];
    let mock;

    describe('loadAuthority', () => {
      beforeEach(() => {
        expectedMutations = [];
        expectedActions = [];
        mock = new MockAdapter(axios);
        mock.reset();
      });

      it('should show error if internal server error occurs', (done) => {
        expectedMutations = [
          {type: 'setAuthLoadingState', payload: true}
        ];
        expectedActions = [
          {type: 'showError', payload: {type: RESPONSE_TYPES.ERROR, content: RESPONSE_MESSAGES.ERROR.INTERNAL_SERVER_ERROR}}
        ];
        mock.onPost('/api/auth/decode').reply(500, 'Internal Server Error');
        testAction(actions.loadAuthority, token, state, expectedMutations, expectedActions, done);
      });

      it('should show invalid token page if token is invalid', (done) => {
        expectedMutations = [
          {type: 'setAuthLoadingState', payload: true}
        ];
        expectedActions = [];
        mock.onPost('/api/auth/decode').reply(400, {response: {status: 400}});
        testAction(actions.loadAuthority, token, state, expectedMutations, expectedActions, done);
      });

      it('should set user session if authorized', (done) => {
        expectedMutations = [
          {type: 'setAuthLoadingState', payload: true},
          {type: 'setAuthority', payload: {logged: true, username: 'test'}},
          {type: 'setAuthLoadingState', payload: false}
        ];
        expectedActions = [
          {type: 'showMenuToggleBtn'},
          {type: 'showUserbox'}
        ];
        mock.onPost('/api/auth/decode').reply(200, {
          decoded: {username: 'test'}
        });
        testAction(actions.loadAuthority, token, state, expectedMutations, expectedActions, done);
      });

      it('should remove user session if not authorized', (done) => {
        const redirectionPath = '/signed_out';
        const deferred = Q.defer();
        const dispatchMock = sinon.stub().returns(deferred.promise);
        const commitMock = sinon.spy();
        deferred.resolve();
        actions.handleLogOut({commit: commitMock, dispatch: dispatchMock}, redirectionPath);
        process.nextTick(() => {
          expect(commitMock.calledOnce).to.equal(true);
          expect(commitMock.calledWith('setAuthority', {logged: false, username: ''})).to.equal(true);
          expect(dispatchMock.calledTwice).to.equal(true);
          expect(dispatchMock.getCall(0).args[0]).to.equal('hideMenuToggleBtn');
          expect(dispatchMock.getCall(1).args[0]).to.equal('hideUserbox');
          done();
        })
      });
    });

    describe('logIntoK8SDashboard', () => {
      beforeEach(() => {
        expectedMutations = [];
        expectedActions = [];
        mock = new MockAdapter(axios);
        mock.reset();
      });

      it('should show error if internal server error occurs', (done) => {
        expectedMutations = [];
        expectedActions = [
          {type: 'showError', payload: {type: RESPONSE_TYPES.ERROR, content: RESPONSE_MESSAGES.ERROR.INTERNAL_SERVER_ERROR}}
        ];
        mock.onGet('/dashboard/api/v1/csrftoken/login').reply(500, 'Internal Server Error');
        testAction(actions.logIntoK8SDashboard, token, state, expectedMutations, expectedActions, done);
      });

      it('should show error if internal server error occurs', (done) => {
        expectedMutations = [];
        expectedActions = [
          {type: 'showError', payload: {type: RESPONSE_TYPES.ERROR, content: RESPONSE_MESSAGES.ERROR.INTERNAL_SERVER_ERROR}}
        ];
        mock.onGet('/dashboard/api/v1/csrftoken/login').reply(200, {token: 'token'});
        mock.onPost('/dashboard/api/v1/login').reply(500, 'Internal Server Error');
        testAction(actions.logIntoK8SDashboard, token, state, expectedMutations, expectedActions, done);
      });
    });
  });
});
