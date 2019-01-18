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
const tensorboardApi = rewire('../../../src/handlers/tensorboard/tensorboard');
const HttpStatus = require('http-status-codes');

describe('Handlers | Tensorboard', function () {

  let resMock, reqMock, nautaMock, error, deferred, instance;

  beforeEach(function () {
    urls = ['1', '2', '3'];
    error = {
      status: 500,
      message: 'error'
    };
    instance = {
      id: '1'
    };
  });

  describe('createTensorBoardInstance', function () {
    beforeEach(function () {
      deferred = Q.defer();
      nautaMock = {
        createTensorBoardInstance: sinon.stub().returns(deferred.promise)
      };
      resMock = {
        status: sinon.stub().returns({
          send: sinon.spy()
        }),
        send: sinon.spy()
      };
      reqMock = {
        headers: {
          authorization: 'token'
        },
        body: {
          items: [{name: 1}, {name: 2}, {name: 3}]
        }
      };
    });

    it('should return error if invalid request headers', function () {
      delete reqMock.headers.authorization;
      tensorboardApi.createTensorBoardInstance(reqMock, resMock);
      expect(resMock.status.calledOnce).to.equal(true);
      expect(resMock.status.calledWith(HttpStatus.UNAUTHORIZED)).to.equal(true);
    });

    it('should return error if request body not provided', function () {
      delete reqMock.body;
      tensorboardApi.createTensorBoardInstance(reqMock, resMock);
      expect(resMock.status.calledOnce).to.equal(true);
      expect(resMock.status.calledWith(HttpStatus.BAD_REQUEST)).to.equal(true);
    });

    it('should return error if empty request body provided', function () {
      reqMock.body = {};
      tensorboardApi.createTensorBoardInstance(reqMock, resMock);
      expect(resMock.status.calledOnce).to.equal(true);
      expect(resMock.status.calledWith(HttpStatus.BAD_REQUEST)).to.equal(true);
    });

    it('should return error if cannot create tensorboard instance', function (done) {
      tensorboardApi.__set__('nauta', nautaMock);
      deferred.reject(error);
      tensorboardApi.createTensorBoardInstance(reqMock, resMock);
      setTimeout(() => {
        expect(resMock.status.calledOnce).to.equal(true);
        expect(resMock.status.calledWith(error.status)).to.equal(true);
        done();
      }, 200);
    });

    it('should return url if list of experiments provided', function (done) {
      tensorboardApi.__set__('nauta', nautaMock);
      deferred.resolve(instance);
      tensorboardApi.createTensorBoardInstance(reqMock, resMock);
      process.nextTick(() => {
        expect(resMock.send.calledOnce).to.equal(true);
        expect(resMock.send.calledWith(instance)).to.deep.equal(true);
        done();
      });
    });
  });

  describe('getTensorBoardInstanceState', function () {
    beforeEach(function () {
      deferred = Q.defer();
      nautaMock = {
        getTensorboardInstanceState: sinon.stub().returns(deferred.promise)
      };
      resMock = {
        status: sinon.stub().returns({
          send: sinon.spy()
        }),
        send: sinon.spy()
      };
      reqMock = {
        headers: {
          authorization: 'token'
        },
        params: {
          id: 1
        }
      };
    });

    it('should return error if invalid request headers', function () {
      delete reqMock.headers.authorization;
      tensorboardApi.getTensorBoardInstanceState(reqMock, resMock);
      expect(resMock.status.calledOnce).to.equal(true);
      expect(resMock.status.calledWith(HttpStatus.UNAUTHORIZED)).to.equal(true);
    });

    it('should return error if instance id in param not provided', function () {
      delete reqMock.params.id;
      tensorboardApi.getTensorBoardInstanceState(reqMock, resMock);
      expect(resMock.status.calledOnce).to.equal(true);
      expect(resMock.status.calledWith(HttpStatus.BAD_REQUEST)).to.equal(true);
    });

    it('should return error if cannot get tensorboard instance', function (done) {
      tensorboardApi.__set__('nauta', nautaMock);
      deferred.reject(error);
      tensorboardApi.getTensorBoardInstanceState(reqMock, resMock);
      setTimeout(() => {
        expect(resMock.status.calledOnce).to.equal(true);
        expect(resMock.status.calledWith(error.status)).to.equal(true);
        done();
      }, 200);
    });

    it('should return instance if request for getting data with success', function (done) {
      tensorboardApi.__set__('nauta', nautaMock);
      deferred.resolve(instance);
      tensorboardApi.getTensorBoardInstanceState(reqMock, resMock);
      process.nextTick(() => {
        expect(resMock.send.calledOnce).to.equal(true);
        expect(resMock.send.calledWith(instance)).to.deep.equal(true);
        done();
      });
    });
  });
});
