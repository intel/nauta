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
