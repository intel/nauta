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
