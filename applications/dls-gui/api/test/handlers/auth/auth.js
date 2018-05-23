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

const expect = require('chai').expect;
const sinon = require('sinon');
const rewire =  require('rewire');
const authApi = rewire('../../../src/handlers/auth/auth');

describe('Handlers | Auth', function () {

  let resMock, reqMock, jwtMock, tokenPayload;

  describe('decodeToken', function () {

    beforeEach(function () {
      resMock = {
        status: sinon.stub().returns({
          send: sinon.spy()
        }),
        send: sinon.spy()
      };
      reqMock = {
        body: {
          token: 'fake_token'
        }
      };
      jwtMock = {
        decode: sinon.spy()
      };
      tokenPayload = {};
    });

    it('should return error if invalid request body', function () {
      delete reqMock.body.token;
      authApi.decodeToken(reqMock, resMock);
      expect(resMock.status.calledOnce).to.equal(true);
      expect(resMock.status.calledWith(400)).to.equal(true);
    });

    it('should return UNAUTHORIZED error if token is incorrect', function () {
      jwtMock.decode = sinon.stub().returns(null);
      authApi.__set__('jwt', jwtMock);
      authApi.decodeToken(reqMock, resMock);
      expect(resMock.status.calledOnce).to.equal(true);
      expect(resMock.status.calledWith(401)).to.equal(true);
    });

    it('should return UNAUTHORIZED error if token is not valid for DLS4E', function () {
      jwtMock.decode = sinon.stub().returns(tokenPayload);
      authApi.__set__('jwt', jwtMock);
      authApi.decodeToken(reqMock, resMock);
      expect(resMock.status.calledOnce).to.equal(true);
      expect(resMock.status.calledWith(401)).to.equal(true);
    });

    it('should return decoded token data if token is valid', function () {
      tokenPayload['kubernetes.io/serviceaccount/service-account.name'] = 'test';
      jwtMock.decode = sinon.stub().returns(tokenPayload);
      authApi.__set__('jwt', jwtMock);
      authApi.decodeToken(reqMock, resMock);
      expect(resMock.send.calledOnce).to.equal(true);
      expect(resMock.send.calledWith({decoded: tokenPayload})).to.equal(true);
    });

  });

});
