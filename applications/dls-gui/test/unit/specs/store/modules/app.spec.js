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
import {getters, actions, mutations} from '../../../../../src/store/modules/app';

describe('VUEX modules app', () => {
  const state = {
    menu: {
      visible: true,
      btnVisible: false
    },
    userbox: {
      visible: false
    },
    error: {
      content: '',
      type: 'warning',
      visible: false,
      time: 1
    }
  };

  describe('Getters', () => {

    it('menuVisibility', () => {
      const result = getters.menuVisibility(state);
      expect(result).to.deep.equal(state.menu.visible);
    });

    it('menuBtnVisibility', () => {
      const result = getters.menuBtnVisibility(state);
      expect(result).to.deep.equal(state.menu.btnVisible);
    });

    it('getUserboxParams', () => {
      const result = getters.getUserboxParams(state);
      expect(result).to.deep.equal(state.userbox);
    });

    it('errorType', () => {
      const result = getters.errorType(state);
      expect(result).to.deep.equal(state.error.type);
    });

    it('errorContent', () => {
      const result = getters.errorContent(state);
      expect(result).to.deep.equal(state.error.content);
    });

    it('errorTime', () => {
      const result = getters.errorTime(state);
      expect(result).to.deep.equal(state.error.time);
    });
  });

  describe('Mutations', () => {

    it('setMenuVisibility', () => {
      const visibility = true;
      mutations.setMenuVisibility(state, visibility);
      expect(state.menu.visible).to.deep.equal(visibility);
    });

    it('setMenuToggleBtnVisibility', () => {
      const visibility = true;
      mutations.setMenuToggleBtnVisibility(state, visibility);
      expect(state.menu.btnVisible).to.deep.equal(visibility);
    });

    it('setUserboxVisibility', () => {
      const visibility = true;
      mutations.setUserboxVisibility(state, visibility);
      expect(state.userbox.visible).to.deep.equal(visibility);
    });

    it('setError', () => {
      const type = 'success';
      const content = 'content';
      mutations.setError(state, {type, content});
      expect(state.error.visible).to.deep.equal(true);
      expect(state.error.content).to.deep.equal(content);
      expect(state.error.type).to.deep.equal(type);
    });

    it('setError with the same content and small time difference', (done) => {
      const type = 'success';
      const content = 'content';
      mutations.setError(state, {type, content});
      const currentErrorTime = state.error.time;
      setTimeout(() => {
        mutations.setError(state, {type, content});
        expect(state.error.visible).to.deep.equal(true);
        expect(state.error.content).to.deep.equal(content);
        expect(state.error.type).to.deep.equal(type);
        expect(state.error.time).to.equal(currentErrorTime);
        done();
      }, 100);
    });

    it('setError with the same content and small time difference', () => {
      const type = 'success';
      const content = 'content';
      const currentErrorTime = 1;
      const state = {
        error: {
          content: content,
          type: type,
          visible: true,
          time: currentErrorTime
        }
      };
      mutations.setError(state, {type, content});
      expect(state.error.visible).to.deep.equal(true);
      expect(state.error.content).to.deep.equal(content);
      expect(state.error.type).to.deep.equal(type);
      expect(state.error.time).to.not.equal(currentErrorTime);
    });

    it('removeError', () => {
      mutations.removeError(state);
      expect(state.error.visible).to.deep.equal(false);
    });

  });

  describe('Actions', () => {
    it('toggleMenu', (done) => {
      testAction(actions.toggleMenu, null, state, [
        { type: 'setMenuVisibility' }
      ], [], done);
    });

    it('showMenuToggleBtn', (done) => {
      testAction(actions.showMenuToggleBtn, null, state, [
        { type: 'setMenuToggleBtnVisibility', payload: true }
      ], [], done);
    });

    it('hideMenuToggleBtn', (done) => {
      testAction(actions.hideMenuToggleBtn, null, state, [
        { type: 'setMenuToggleBtnVisibility', payload: false }
      ], [], done);
    });

    it('showUserbox', (done) => {
      testAction(actions.showUserbox, null, state, [
        { type: 'setUserboxVisibility', payload: true }
      ], [], done);
    });

    it('hideUserbox', (done) => {
      testAction(actions.hideUserbox, null, state, [
        { type: 'setUserboxVisibility', payload: false }
      ], [], done);
    });

    it('showError', (done) => {
      const type = 'success';
      const content = 'content';
      testAction(actions.showError, {type, content}, state, [
        { type: 'setError', payload: {type, content} }
      ], [], done);
    });

    it('hideError', (done) => {
      testAction(actions.hideError, null, state, [
        { type: 'removeError' }
      ], [], done);
    });

  });
});
