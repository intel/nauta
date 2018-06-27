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
const dls4e = rewire('../../src/utils/dls4e');
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
      dls4e.__set__('authApi', authApiMock);
      deferred.reject(error);
      return dls4e.createTensorBoardInstance(token, expName)
        .catch(function (err) {
          expect(err).to.equal(error)
        });
    });

    it('should return error if request to api failed', function () {
      const reqDefer = Q.defer();
      authApiMock.decodeToken = sinon.stub().returns(deferred.promise);
      requestMock = sinon.stub().returns(reqDefer.promise);
      dls4e.__set__('authApi', authApiMock);
      dls4e.__set__('request', requestMock);
      deferred.resolve(data);
      reqDefer.reject(error);
      return dls4e.createTensorBoardInstance(token, expName)
        .catch(function (err) {
          expect(err).to.equal(error)
        });
    });

    it('should return data if request to api with success', function () {
      const reqDefer = Q.defer();
      authApiMock.decodeToken = sinon.stub().returns(deferred.promise);
      requestMock = sinon.stub().returns(reqDefer.promise);
      dls4e.__set__('authApi', authApiMock);
      dls4e.__set__('request', requestMock);
      deferred.resolve(data);
      reqDefer.resolve(data);
      return dls4e.createTensorBoardInstance(token, expName)
        .then(function (res) {
          expect(res).to.equal(data)
        });
    });
  });
});
