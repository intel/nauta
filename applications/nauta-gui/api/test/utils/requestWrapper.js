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
