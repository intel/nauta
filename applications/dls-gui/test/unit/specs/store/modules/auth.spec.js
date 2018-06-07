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
    username: 'anonymous'
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
  });

  describe('Mutations', () => {
    it('setAuthority', () => {
      const logged = true;
      const username = 'username';
      mutations.setAuthority(state, {logged, username});
      expect(state.logged).to.deep.equal(logged);
      expect(state.username).to.deep.equal(username);
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
        expectedMutations = [];
        expectedActions = [
          {type: 'hideSpinner'},
          {type: 'showError', payload: {type: RESPONSE_TYPES.ERROR, content: RESPONSE_MESSAGES.ERROR.INTERNAL_SERVER_ERROR}}
        ];
        mock.onPost('/api/auth/decode').reply(500, 'Internal Server Error');
        testAction(actions.loadAuthority, token, state, expectedMutations, expectedActions, done);
      });

      it('should show invalid token page if token is invalid', (done) => {
        expectedMutations = [];
        expectedActions = [
          {type: 'hideSpinner'}
        ];
        mock.onPost('/api/auth/decode').reply(400, {response: {status: 400}});
        testAction(actions.loadAuthority, token, state, expectedMutations, expectedActions, done);
      });

      it('should set user session if authorized', (done) => {
        expectedMutations = [
          {type: 'setAuthority', payload: {logged: true, username: 'test'}}
        ];
        expectedActions = [
          {type: 'hideSpinner'},
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
  });
});
