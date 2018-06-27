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
const reqWrp = rewire('../../src/utils/requestWrapper');
const HttpStatus = require('http-status-codes');

describe('Utils | requestWrapper', function () {

  let requestMock, error, response, body, options;

  beforeEach(function () {
    requestMock = sinon.spy();
    options = {};
    error = {
      status: HttpStatus.INTERNAL_SERVER_ERROR,
      message: 'Internal server error'
    };
    response = {
      statusCode: HttpStatus.OK
    };
    body = JSON.stringify({test: 'test'});
  });

  it('should return error if cannot perform request', function () {
    requestMock = sinon.stub().callsArgWith(1, error, null, null);
    reqWrp.__set__('request', requestMock);
    return reqWrp(options)
      .catch(function (err) {
        expect(err.message).to.equal(error)
      });
  });

  it('should return error if response with 500 status code', function () {
    response.statusCode = HttpStatus.INTERNAL_SERVER_ERROR;
    requestMock = sinon.stub().callsArgWith(1, null, response, null);
    reqWrp.__set__('request', requestMock);
    return reqWrp(options)
      .catch(function (err) {
        expect(err.message).to.equal(error.message)
      });
  });

  it('should return UNAUTHORIZED if request to api unauthorized', function () {
    response.statusCode = HttpStatus.UNAUTHORIZED;
    requestMock = sinon.stub().callsArgWith(1, null, response, body);
    reqWrp.__set__('request', requestMock);
    return reqWrp(options)
      .catch(function (err) {
        expect(err.status).to.equal(HttpStatus.UNAUTHORIZED);
      });
  });

  it('should return FORBIDDEN if action in api forbidden', function () {
    response.statusCode = HttpStatus.FORBIDDEN;
    requestMock = sinon.stub().callsArgWith(1, null, response, body);
    reqWrp.__set__('request', requestMock);
    return reqWrp(options)
      .catch(function (err) {
        expect(err.status).to.equal(HttpStatus.FORBIDDEN);
      });
  });

  it('should return object if body parsable', function () {
    requestMock = sinon.stub().callsArgWith(1, null, response, body);
    reqWrp.__set__('request', requestMock);
    return reqWrp(options)
      .then(function (res) {
        expect(typeof(res)).to.equal('object');
      });
  });

  it('should return string if body not parsable', function () {
    body = 'example of not parsable data';
    requestMock = sinon.stub().callsArgWith(1, null, response, body);
    reqWrp.__set__('request', requestMock);
    return reqWrp(options)
      .then(function (res) {
        expect(typeof(res)).to.equal('string');
      });
  });
});
