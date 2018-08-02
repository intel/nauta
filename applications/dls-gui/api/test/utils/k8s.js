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
});
