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
const nauta = rewire('../../src/utils/nauta');
const HttpStatus = require('http-status-codes');

describe('Utils | k8s', function () {

  let authApiMock, requestMock, deferred, data, token, error, expName;

  beforeEach(function () {
    authApiMock = {
      decodeToken: sinon.spy()
    };
    data = {
      'kubernetes.io/serviceaccount/namespace': 'username'
    };
    error = {
      status: HttpStatus.INTERNAL_SERVER_ERROR,
      message: 'error'
    };
    token = 'token';
    expName = 'experiment';
  });

  describe('createTensorBoardInstance', function () {
    beforeEach(function () {
      deferred = Q.defer();
    });

    it('should return error if cannot decode token', function () {
      authApiMock.decodeToken = sinon.stub().returns(deferred.promise);
      nauta.__set__('authApi', authApiMock);
      deferred.reject(error);
      return nauta.createTensorBoardInstance(token, expName)
        .catch(function (err) {
          expect(err).to.equal(error)
        });
    });

    it('should return error if request to api failed', function () {
      const reqDefer = Q.defer();
      authApiMock.decodeToken = sinon.stub().returns(deferred.promise);
      requestMock = sinon.stub().returns(reqDefer.promise);
      nauta.__set__('authApi', authApiMock);
      nauta.__set__('request', requestMock);
      deferred.resolve(data);
      reqDefer.reject(error);
      return nauta.createTensorBoardInstance(token, expName)
        .catch(function (err) {
          expect(err).to.equal(error)
        });
    });

    it('should return data if request to api with success', function () {
      const reqDefer = Q.defer();
      authApiMock.decodeToken = sinon.stub().returns(deferred.promise);
      requestMock = sinon.stub().returns(reqDefer.promise);
      nauta.__set__('authApi', authApiMock);
      nauta.__set__('request', requestMock);
      deferred.resolve(data);
      reqDefer.resolve(data);
      return nauta.createTensorBoardInstance(token, expName)
        .then(function (res) {
          expect(res).to.equal(data)
        });
    });
  });

  describe('getTensorboardInstanceState', function () {
    beforeEach(function () {
      deferred = Q.defer();
    });

    it('should return error if cannot decode token', function () {
      authApiMock.decodeToken = sinon.stub().returns(deferred.promise);
      nauta.__set__('authApi', authApiMock);
      deferred.reject(error);
      return nauta.getTensorboardInstanceState(token, expName)
        .catch(function (err) {
          expect(err).to.equal(error)
        });
    });

    it('should return error if request to api failed', function () {
      const reqDefer = Q.defer();
      authApiMock.decodeToken = sinon.stub().returns(deferred.promise);
      requestMock = sinon.stub().returns(reqDefer.promise);
      nauta.__set__('authApi', authApiMock);
      nauta.__set__('request', requestMock);
      deferred.resolve(data);
      reqDefer.reject(error);
      return nauta.getTensorboardInstanceState(token, expName)
        .catch(function (err) {
          expect(err).to.equal(error)
        });
    });

    it('should return data if request to api with success', function () {
      const reqDefer = Q.defer();
      authApiMock.decodeToken = sinon.stub().returns(deferred.promise);
      requestMock = sinon.stub().returns(reqDefer.promise);
      nauta.__set__('authApi', authApiMock);
      nauta.__set__('request', requestMock);
      deferred.resolve(data);
      reqDefer.resolve(data);
      return nauta.getTensorboardInstanceState(token, expName)
        .then(function (res) {
          expect(res).to.equal(data)
        });
    });
  });
});
