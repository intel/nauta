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
const k8sApi = rewire('../../src/utils/k8s');
const errMessages = require('../../src/utils/error-messages');
const HttpStatus = require('http-status-codes');

describe('Utils | k8s', function () {

  let authApiMock, requestMock, deferred, data, token, error, resourceName, labelName, labelValue;

  beforeEach(function () {
    authApiMock = {
      decodeToken: sinon.spy()
    };
    data = {
      'kubernetes.io/serviceaccount/namespace': 'username'
    };
    error = {
      status: HttpStatus.INTERNAL_SERVER_ERROR,
      message: errMessages.K8S.CUSTOM_OBJECT.CANNOT_LIST
    };
    token = 'token';
    resourceName = 'experiment';
    labelName = 'labelName';
    labelValue = 'labelValue';
  });

  describe('listNamespacedCustomObject', function () {
    beforeEach(function () {
      deferred = Q.defer();
    });

    it('should return error if cannot decode token', function () {
      authApiMock.decodeToken = sinon.stub().returns(deferred.promise);
      k8sApi.__set__('authApi', authApiMock);
      deferred.reject(error);
      return k8sApi.listNamespacedCustomObject(token, resourceName)
        .catch(function (err) {
          expect(err).to.equal(error)
        });
    });

    it('should return error if request to api failed', function () {
      const reqDefer = Q.defer();
      authApiMock.decodeToken = sinon.stub().returns(deferred.promise);
      requestMock = sinon.stub().returns(reqDefer.promise);
      k8sApi.__set__('authApi', authApiMock);
      k8sApi.__set__('request', requestMock);
      deferred.resolve(data);
      reqDefer.reject(error);
      return k8sApi.listNamespacedCustomObject(token, resourceName)
        .catch(function (err) {
          expect(err).to.equal(error)
        });
    });

    it('should return data if request to api with success', function () {
      const reqDefer = Q.defer();
      authApiMock.decodeToken = sinon.stub().returns(deferred.promise);
      requestMock = sinon.stub().returns(reqDefer.promise);
      k8sApi.__set__('authApi', authApiMock);
      k8sApi.__set__('request', requestMock);
      deferred.resolve(data);
      reqDefer.resolve(data);
      return k8sApi.listNamespacedCustomObject(token, resourceName)
        .then(function (res) {
          expect(res).to.equal(data)
        });
    });

    it('should not return data if request to api with success but string in response', function () {
      const reqDefer = Q.defer();
      authApiMock.decodeToken = sinon.stub().returns(deferred.promise);
      requestMock = sinon.stub().returns(reqDefer.promise);
      k8sApi.__set__('authApi', authApiMock);
      k8sApi.__set__('request', requestMock);
      deferred.resolve(data);
      reqDefer.resolve('string');
      return k8sApi.listNamespacedCustomObject(token, resourceName)
        .catch(function (err) {
          expect(err).to.deep.equal(error);
        });
    });
  });

  describe('listClusterCustomObject', function () {
    beforeEach(function () {
      deferred = Q.defer();
    });

    it('should return error if cannot decode token', function () {
      authApiMock.decodeToken = sinon.stub().returns(deferred.promise);
      k8sApi.__set__('authApi', authApiMock);
      deferred.reject(error);
      return k8sApi.listClusterCustomObject(token, resourceName)
        .catch(function (err) {
          expect(err).to.equal(error)
        });
    });

    it('should return error if request to api failed', function () {
      const reqDefer = Q.defer();
      authApiMock.decodeToken = sinon.stub().returns(deferred.promise);
      requestMock = sinon.stub().returns(reqDefer.promise);
      k8sApi.__set__('authApi', authApiMock);
      k8sApi.__set__('request', requestMock);
      deferred.resolve(data);
      reqDefer.reject(error);
      return k8sApi.listClusterCustomObject(token, resourceName)
        .catch(function (err) {
          expect(err).to.equal(error)
        });
    });

    it('should return data if request to api with success', function () {
      const reqDefer = Q.defer();
      authApiMock.decodeToken = sinon.stub().returns(deferred.promise);
      requestMock = sinon.stub().returns(reqDefer.promise);
      k8sApi.__set__('authApi', authApiMock);
      k8sApi.__set__('request', requestMock);
      deferred.resolve(data);
      reqDefer.resolve(data);
      return k8sApi.listClusterCustomObject(token, resourceName)
        .then(function (res) {
          expect(res).to.equal(data)
        });
    });

    it('should not return data if request to api with success but string in response', function () {
      const reqDefer = Q.defer();
      authApiMock.decodeToken = sinon.stub().returns(deferred.promise);
      requestMock = sinon.stub().returns(reqDefer.promise);
      k8sApi.__set__('authApi', authApiMock);
      k8sApi.__set__('request', requestMock);
      deferred.resolve(data);
      reqDefer.resolve('string');
      return k8sApi.listClusterCustomObject(token, resourceName)
        .catch(function (err) {
          expect(err).to.deep.equal(error);
        });
    });
  });

  describe('listPodsByLabelValue', function () {
    beforeEach(function () {
      deferred = Q.defer();
      error = {
        status: HttpStatus.INTERNAL_SERVER_ERROR,
        message: errMessages.K8S.PODS.CANNOT_LIST
      };
    });

    it('should return error if cannot decode token', function () {
      authApiMock.decodeToken = sinon.stub().returns(deferred.promise);
      k8sApi.__set__('authApi', authApiMock);
      deferred.reject(error);
      return k8sApi.listPodsByLabelValue(token, labelName, labelValue)
        .catch(function (err) {
          expect(err).to.equal(error)
        });
    });

    it('should return error if request to api failed', function () {
      const reqDefer = Q.defer();
      authApiMock.decodeToken = sinon.stub().returns(deferred.promise);
      requestMock = sinon.stub().returns(reqDefer.promise);
      k8sApi.__set__('authApi', authApiMock);
      k8sApi.__set__('request', requestMock);
      deferred.resolve(data);
      reqDefer.reject(error);
      return k8sApi.listPodsByLabelValue(token, labelName, labelValue)
        .catch(function (err) {
          expect(err).to.equal(error)
        });
    });

    it('should return data if request to api with success', function () {
      const reqDefer = Q.defer();
      authApiMock.decodeToken = sinon.stub().returns(deferred.promise);
      requestMock = sinon.stub().returns(reqDefer.promise);
      k8sApi.__set__('authApi', authApiMock);
      k8sApi.__set__('request', requestMock);
      deferred.resolve(data);
      reqDefer.resolve(data);
      return k8sApi.listPodsByLabelValue(token, labelName, labelValue)
        .then(function (res) {
          expect(res).to.equal(data)
        });
    });

    it('should return data if request to api with success without label name and value', function () {
      const reqDefer = Q.defer();
      authApiMock.decodeToken = sinon.stub().returns(deferred.promise);
      requestMock = sinon.stub().returns(reqDefer.promise);
      k8sApi.__set__('authApi', authApiMock);
      k8sApi.__set__('request', requestMock);
      deferred.resolve(data);
      reqDefer.resolve(data);
      return k8sApi.listPodsByLabelValue(token)
        .then(function (res) {
          expect(res).to.equal(data)
        });
    });

    it('should not return data if request to api with success but string in response', function () {
      const reqDefer = Q.defer();
      authApiMock.decodeToken = sinon.stub().returns(deferred.promise);
      requestMock = sinon.stub().returns(reqDefer.promise);
      k8sApi.__set__('authApi', authApiMock);
      k8sApi.__set__('request', requestMock);
      deferred.resolve(data);
      reqDefer.resolve('string');
      return k8sApi.listPodsByLabelValue(token, labelName, labelValue)
        .catch(function (err) {
          expect(err).to.deep.equal(error);
        });
    });
  });

  describe('parseContainerState', function () {

    it('should return static text if state obj not defined', function () {
      const state = null;
      const expectedResult = 'Not created';
      const result = k8sApi.parseContainerState(state);
      expect(result).to.deep.equal(expectedResult);
    });

    it('should return static text if state running', function () {
      const state = {running: 'running'};
      const expectedResult = `Running, running`;
      const result = k8sApi.parseContainerState(state);
      expect(result).to.deep.equal(expectedResult);
    });

    it('should return static text if state terminated', function () {
      const state = {terminated: {reason: 'reason'}};
      const expectedResult = `Terminated, reason: ${state.terminated.reason}; `;
      const result = k8sApi.parseContainerState(state);
      expect(result).to.deep.equal(expectedResult);
    });

    it('should return static text if state waiting', function () {
      const state = {waiting: 'waiting'};
      const expectedResult = `Waiting, waiting`;
      const result = k8sApi.parseContainerState(state);
      expect(result).to.deep.equal(expectedResult);
    });

  });
});
