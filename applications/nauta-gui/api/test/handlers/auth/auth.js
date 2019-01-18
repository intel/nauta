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
const rewire = require('rewire');
const Q = require('q');
const authApi = rewire('../../../src/handlers/auth/auth');
const errHandler = require('../../../src/utils/error-handler');
const errMessages = require('../../../src/utils/error-messages');
const HttpStatus = require('http-status-codes');

describe('Handlers | Auth', function () {

  let resMock, reqMock, deferred;

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
  });

  describe('decodeToken', function () {
    let jwtMock, decoded, token;
    beforeEach(function () {
      decoded = {
        'kubernetes.io/serviceaccount/namespace': 'username'
      };
      jwtMock = {
        decode: sinon.stub()
      };
      token = 'fake_token';
    });

    it('should return error if cannot decode token', function () {
      jwtMock.decode = sinon.stub().returns(null);
      authApi.__set__('jwt', jwtMock);
      return authApi.decodeToken(token)
        .catch(function () {
          expect(jwtMock.decode.calledOnce).to.equal(true);
        });
    });

    it('should return decoded data if token valid', function () {
      jwtMock.decode = sinon.stub().returns(decoded);
      authApi.__set__('jwt', jwtMock);
      return authApi.decodeToken(token)
        .then(function (data) {
          expect(jwtMock.decode.calledOnce).to.equal(true);
          expect(data['kubernetes.io/serviceaccount/namespace']).to.equal(decoded['kubernetes.io/serviceaccount/namespace'])
        });
    });
  });

  describe('getUserAuthority', function () {
    let decodeTokenMock, decoded;
    beforeEach(function () {
      decoded = {
        'kubernetes.io/serviceaccount/namespace': 'username'
      };
      deferred = Q.defer();
      decodeTokenMock = sinon.stub().returns(deferred.promise);
    });

    it('should return error if invalid request body', function () {
      delete reqMock.body.token;
      authApi.getUserAuthority(reqMock, resMock);
      expect(resMock.status.calledOnce).to.equal(true);
      expect(resMock.status.calledWith(400)).to.equal(true);
    });

    it('should return UNAUTHORIZED error if token is incorrect', function (done) {
      authApi.__set__('decodeToken', decodeTokenMock);
      authApi.getUserAuthority(reqMock, resMock);
      deferred.reject(errHandler(HttpStatus.UNAUTHORIZED, errMessages.AUTH.INVALID_TOKEN));
      process.nextTick(function () {
        expect(decodeTokenMock.calledOnce).to.equal(true);
        expect(resMock.status.calledOnce).to.equal(true);
        expect(resMock.status.calledWith(401)).to.equal(true);
        done();
      });
    });

    it('should return decoded token data if token is valid', function (done) {
      authApi.__set__('decodeToken', decodeTokenMock);
      authApi.getUserAuthority(reqMock, resMock);
      deferred.resolve(decoded);
      process.nextTick(function () {
        expect(resMock.send.calledOnce).to.equal(true);
        expect(resMock.send.getCall(0).args[0].decoded.username).to.equal(decoded['kubernetes.io/serviceaccount/namespace']);
        done();
      });
    });

  });
});
